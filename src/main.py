import json
import uuid
from string import Template
import time

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


def handle_lock(endpointId, correlationToken):
    #    print(os.environ['USERNAME'])
    #    print(os.environ['PIN'])
    with open('response.tpl', 'r') as template_file:
        template = Template(template_file.read())
        print(template)
        response_json = template.substitute(lockState='LOCKED', timeOfSample=get_utc_timestamp(), messageId=str(uuid.uuid4()),
                                            correlationToken=correlationToken, endpointId=endpointId)
        return json.loads(response_json)


def handle_unlock(endpointId, correlationToken):
    with open('response.tpl', 'r') as template_file:
        template = Template(template_file.read())
        response_json = template.substitute(lockState='UNLOCKED', timeOfSample=get_utc_timestamp(), messageId=str(uuid.uuid4()),
                                            correlationToken=correlationToken, endpointId=endpointId)
        return json.loads(response_json)


def handle_state_report(endpointId, correlationToken):
    with open('state_response.tpl', 'r') as template_file:
        template = Template(template_file.read())
        response_json = template.substitute(lockState='UNLOCKED', timeOfSample=get_utc_timestamp(), messageId=str(uuid.uuid4()),
                                            correlationToken=correlationToken, endpointId=endpointId)
        return json.loads(response_json)


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
