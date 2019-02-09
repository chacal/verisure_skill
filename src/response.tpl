{
  "context": {
    "properties": [
      {
        "namespace": "Alexa.LockController",
        "name": "lockState",
        "value": "$lockState",
        "timeOfSample": "$timeOfSample",
        "uncertaintyInMilliseconds": 1000
      }
    ]
  },
  "event": {
    "header": {
      "namespace": "Alexa",
      "name": "Response",
      "payloadVersion": "3",
      "messageId": "$messageId",
      "correlationToken": "$correlationToken"
    },
    "endpoint": {
      "scope": {
        "type": "BearerToken",
        "token": "access-token-from-Amazon"
      },
      "endpointId": "$endpointId"
    },
    "payload": {}
  }
}