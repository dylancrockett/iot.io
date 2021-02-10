from flask import Flask
from iotio import IoTManager, DeviceType, IoTClient
from eventlet import wsgi
import eventlet
"""
Example implementation of a Echo server.

Defines an EchoClient of type 'echo'.
Works with the corresponding 'echo' iot.io-client example.
"""

# create a flask app
app = Flask("Echo Example")

# create an instance of the IoTManager
manager = IoTManager(app)


# define the EchoClient device
class EchoClient(DeviceType):
    def on_connect(self, client: IoTClient):
        print("EchoClient Connected! ID: " + client.id)

    # define a handler for when the client receives a "echo" event
    def on_echo(self, message: str, client: IoTClient):
        print("Message from Client of type '" + self.type + "' with ID '" + client.id + "': '", message, "'")

        # respond to client with the 'echo_response' event
        return "echo_response", message

    def on_disconnect(self, client: IoTClient):
        print("EchoClient Disconnected! ID: " + client.id)


# add the device type to the manager
manager.add_type(EchoClient("echo"))

# run the server using eventlet
if __name__ == "__main__":
    wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
