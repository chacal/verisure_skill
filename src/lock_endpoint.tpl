{
  "endpointId": "$endpointId",
  "friendlyName": "$friendlyName",
  "description": "Yale Doorman",
  "manufacturerName": "Yale",
  "displayCategories": [
    "SMARTLOCK"
  ],
  "cookie": {
  },
  "capabilities": [
    {
      "type": "AlexaInterface",
      "interface": "Alexa.LockController",
      "version": "3",
      "properties": {
        "supported": [
          {
            "name": "lockState"
          }
        ],
        "proactivelyReported": false,
        "retrievable": true
      }
    },
    {
      "type": "AlexaInterface",
      "interface": "Alexa",
      "version": "3"
    }
  ]
}
