import json
import uuid
from string import Template
import time
import os
import verisure
from contextlib import contextmanager

locks = [
    {
        "endpointId": "lock-001",
        "friendlyName": "Front Door"
    },
    {
        "endpointId": "lock-002",
        "friendlyName": "Storage Room"
    },
    {
        "endpointId": "lock-003",
        "friendlyName": "Backdoor"
    },
]

endpoint_to_device_label = {
    "lock-001": "2AQT 8F6A",
    "lock-002": "2AQT 8W8E",
    "lock-003": "2AQT 8WYH"
}


def generateEndpointDict(endpoint):
    with open('lock_endpoint.tpl', 'r') as template_file:
        template = Template(template_file.read())
        endpoint_json = template.substitute(endpointId=endpoint['endpointId'], friendlyName=endpoint['friendlyName'])
        return json.loads(endpoint_json)


def handle_discovery():
    response = {
        "event": {
            "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover.Response",
                "payloadVersion": "3",
                "messageId": str(uuid.uuid4())
            },
            "payload": {
                "endpoints": list(map(generateEndpointDict, locks))
            }
        }
    }

    return response


@contextmanager
def verisure_session():
    session = verisure.Session(os.environ['VerisureUsername'], os.environ['VerisurePassword'], cookieFileName='/tmp/verisure_cookie')
    session.login()
    yield session
    session.logout()


def render_template(template, **kwds):
    with open(template, 'r') as template_file:
        template = Template(template_file.read())
        response_json = template.substitute(kwds)
        return json.loads(response_json)


def set_lock_state(endpointId, state):
    with verisure_session() as session:
        try:
            session.set_lock_state(os.environ['VerisurePIN'], endpoint_to_device_label[endpointId], state)
        except verisure.ResponseError as err:
            if err.text['errorCode'] != 'VAL_00819':  # VAL_00819 means that lock was already in the requested state
                raise err


def handle_lock(endpointId, correlationToken):
    set_lock_state(endpointId, 'lock')
    return render_template('response.tpl', lockState='LOCKED', timeOfSample=get_utc_timestamp(), messageId=str(uuid.uuid4()),
                           correlationToken=correlationToken, endpointId=endpointId)


def handle_unlock(endpointId, correlationToken):
    set_lock_state(endpointId, 'unlock')
    return render_template('response.tpl', lockState='UNLOCKED', timeOfSample=get_utc_timestamp(), messageId=str(uuid.uuid4()),
                           correlationToken=correlationToken, endpointId=endpointId)


def handle_state_report(endpointId, correlationToken):
    label = endpoint_to_device_label[endpointId]
    with verisure_session() as session:
        lock_state = session.get_lock_state()
        lock = [ep for ep in lock_state if ep['deviceLabel'] == label][0]
        return render_template('state_response.tpl', lockState=lock['lockedState'], timeOfSample=get_utc_timestamp(),
                               messageId=str(uuid.uuid4()), correlationToken=correlationToken, endpointId=endpointId)


def lambda_handler(event, context):
    print("Input: " + str(event))

    if event['directive']['header']['namespace'] == 'Alexa.Discovery':
        return handle_discovery()
    elif event['directive']['header']['namespace'] == 'Alexa.LockController' and event['directive']['header']['name'] == 'Lock':
        return handle_lock(event['directive']['endpoint']['endpointId'], event['directive']['header']['correlationToken'])
    elif event['directive']['header']['namespace'] == 'Alexa.LockController' and event['directive']['header']['name'] == 'Unlock':
        return handle_unlock(event['directive']['endpoint']['endpointId'], event['directive']['header']['correlationToken'])
    elif event['directive']['header']['namespace'] == 'Alexa' and event['directive']['header']['name'] == 'ReportState':
        return handle_state_report(event['directive']['endpoint']['endpointId'], event['directive']['header']['correlationToken'])
    return {
        'error': 'Unknown request!'
    }


def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))
