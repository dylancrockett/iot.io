from flask import Flask
from iotio import IoTManager, DeviceType, IoTClient
from flask_socketio import SocketIO
"""
Example implementation of a Echo server but running using the Flask-SocketIO server instead of eventlet's wsgi module.

This enables you to allow connection of both socket.io clients from the browser and iot.io clients from iot devices
all inside the same flask application!

Defines an EchoClient of type 'echo'.
Works with the corresponding 'echo' iot.io-client example.
"""

# create a flask app
app = Flask("Echo Example")

# create an instance of the IoTManager
manager = IoTManager(app)

# create SocketIO instance
socket_io = SocketIO(app, async_mode="eventlet")


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
    socket_io.run(app, "0.0.0.0", 5000)
