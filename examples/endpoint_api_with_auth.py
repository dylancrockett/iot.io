from flask import Flask
from iotio import IoTManager, DeviceType, IoTClient
from eventlet import wsgi
import eventlet
import functools
import logging
"""
"""

# config for logging
logging.basicConfig()

# create a flask app
app = Flask(__name__)


# test wrapper for api
def test_wrapper(f):
    @functools.wraps(f)
    def decorated_function(*args):
        print("From wrapper")
        return f(*args)
    return decorated_function


# create an instance of the IoTManager
manager = IoTManager(app, logging_level=logging.DEBUG, endpoint_api=True, endpoint_auth_decorator=test_wrapper)


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
manager.add_type(EchoClient("ping"))

# run the server
if __name__ == "__main__":
    wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
