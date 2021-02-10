# iot.io Server
### iot.io Overview
This project aims to create a lightweight and intuitive system for connecting
IoT devices to a central server for small IoT system implementations and hobbyists.

The framework focuses on providing easy to use system of libraries so the end user does
not need to understand the protocol implementation, though this also is fairly simple.

The format of the framework is somewhat reminiscent of [Socket.IO](https://socket.io/) 
where handlers functions are defined and executed and run as events are triggered.


### Quickstart Guide (Server)
This is an example of a simple IoTManager instance which accepts a "EhcoClient"
and will print every message the client sends out to console.

```python
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
```

If you would like to see the matching quickstart guide for an example
client go [here](https://github.com/dylancrockett/iot.io-client).

