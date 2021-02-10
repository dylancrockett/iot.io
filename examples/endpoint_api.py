from flask import Flask
from iotio import IoTManager, DeviceType, IoTClient
from eventlet import wsgi
import eventlet
"""
Example implementation of a Echo server with the Endpoint Api enabled.

Defines an EchoClient of type 'echo'.
Works with the corresponding 'echo_endpoints' iot.io-client example.

When running allows you to make POST requests to the following url:
    localhost:5000/api/iot.io
    
With the following body structure:
    {
        "clientId": "test_endpoint_client",
        "endpointId: "(one of the following: boolean, integer, string, enum)",
        "data": "(the data to be sent and of the correct type)"
    }
    
Example of a valid request:
    {
        "clientId": "test_endpoint_client",
        "endpointId": "integer",
        "data": 7
    }
"""
# create a flask app
app = Flask("Endpoint Api Example")

# create an instance of the IoTManager with the endpoint Api enabled
manager = IoTManager(app, endpoint_api=True)


# define the EndpointEchoClient device
class EndpointEchoClient(DeviceType):
    def on_connect(self, client: IoTClient):
        print("EndpointEchoClient Connected! ID: " + client.id)

    # print messages echoed from the client
    def on_echo_response(self, message, client: IoTClient):
        print("Got data of type " + str(type(message)) + ": '" + str(message) + "'.")

    def on_disconnect(self, client: IoTClient):
        print("EndpointEchoClient Disconnected! ID: " + client.id)


# add the device type to the manager
manager.add_type(EndpointEchoClient("endpoint_echo"))

# run the server
if __name__ == "__main__":
    wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
