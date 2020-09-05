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

# create a flask app
app = Flask("iot.io demo app")

# create an instance of the IoTManager
manager = IoTManager(app)

# define our EchoClient device
class EchoClient(DeviceType):
    # announce clients connecting
    def on_connect(self, client: IoTClient):
        print("New Ping Client Connected! ID: " + client.id)
    
    # define a handler for when the client recieves a "message" event
    def on_message(self, message: str, client: IoTClient):
        print("Message from Client with ID '" + client.id + "': " + message)
        
        # respond by sending a message to the client's 'message' event handler
        return message
    
    # announce clients disconnecting
    def on_disconnect(self, client: IoTClient):
        print("Echo Client Disconnected! ID: " + client.id)

# add the device type to the manager
manager.add_type(EchoClient("echo"))

# run the server
if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
```

If you would like to see the matching quickstart guide for an example
client go [here](https://github.com/dylancrockett/iot.io-client).

