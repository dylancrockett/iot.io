# default
import json
import logging
from cgi import parse
from typing import List, Dict, Union, Callable

# external
import flask
from eventlet import websocket
from eventlet.websocket import WebSocket
try:
    from flask_restful import Api

    FLASK_RESTFUL_INSTALLED = True
except ImportError:
    Api = True

    FLASK_RESTFUL_INSTALLED = False

# internal
from .Client import IoTClient
from .Device import DeviceType
from .PacketEncoder import AbstractPacketEncoder, DefaultPacketEncoder
from .types import event_pair, sendable
from .exceptions import ConnectionEnded, ConnectionFailed, ClientNoId, ClientNoType, ClientInvalidType, \
    ClientInvalidData, ClientInvalidEndpoints, ClientNoProtocolVersion, ClientIncompatibleProtocolVersion
from .Errors import Errors
from .Endpoint import EndpointParseResponse, ValidationResponse, AbstractEndpointValidator
from .EndpointResource import EndpointResource
from .__main__ import __protocol_version__


class IoTManagerMiddleware(object):
    def __init__(self, app, wsgi_app, manager: 'IoTManager'):
        """
        Manager middleware for WSGI.

        :param app: Flask App object.
        :param wsgi_app: Flask App WSGI object.
        :param manager: IoTManager object.
        """
        self.app = app
        self.wsgi_app = wsgi_app
        self.manager = manager

        # eventlet websocket server handler
        self.ws = websocket.WebSocketWSGI(self.socket)

    def __call__(self, environ, start_response):
        # if the path belongs to the iot.io server
        if environ["PATH_INFO"].startswith("/iot.io"):
            # try to handle the request normally
            try:
                # handle using websocket function
                return self.ws(environ, start_response)
            # if an exception in the handler function is raised deal with it here
            except ConnectionFailed:
                # start response for a 400 code
                start_response("400 Bad Request", [('Content-Type', 'text/plain')])
                return [""]

        # hand down other requests
        return self.wsgi_app(environ, start_response)

    def socket(self, ws):
        self.manager.socket(ws)


# main class used for implementation
class IoTManager(object):
    """
    Main Flask extension.
    """

    def __init__(self, app: flask.Flask, logging_level: int = logging.ERROR, client_logging_level: int = logging.ERROR,
                 encoder: AbstractPacketEncoder = DefaultPacketEncoder, endpoint_api: Union[Api, bool] = None,
                 endpoint_auth_decorator: Callable[[Callable[..., None]], Callable[..., None]] = None):
        """
        A Flask extension used to allow IoT.IO clients to connect to the given flask server.

        :param app: Instance of a Flask object.
        :param logging_level: Logging level of the main IoTManager object.
        :param client_logging_level: Logging level for instances of IoTClient created by the manager.
        :param encoder: Instance of a AbstractPacketEncoder to be used for message serialization/deserialization by
                        instances of IoTClient.
        :param endpoint_api: Either True or an instance of Flask-Restful Api object, used to implement an automatic
                             REST Api for endpoints defined by clients, requires Flask-Restful to be installed.
        :param endpoint_auth_decorator: A wrapper function used to wrap the methods of the Flask-Restful Resource if
                                        user authentication is a desired requirement for accessing the resource.
        """
        # logger for the manager
        self.logger = logging.Logger("iot.io-server")

        # logging levels for main and client debuggers
        self.logger.setLevel(logging_level)
        self.client_logging_level = client_logging_level

        # reference to flask app
        self.app = app

        # reference to Api if it exists
        self.api = None

        # decorator used to authorize
        self.auth_decorator = endpoint_auth_decorator

        # encoder used by clients
        self.encoder = encoder

        # if app is provided initialize the app
        if app:
            self.init_app(app)

            if not hasattr(app, 'extensions'):
                app.extensions = {}  # pragma: no cover
            app.extensions['iot.io'] = self
        else:
            raise ValueError("app must be an instance of a flask application")

        # api object handling
        if endpoint_api is not None:
            if not FLASK_RESTFUL_INSTALLED:
                self.logger.warning("Unable to create Endpoint API, 'flask_restful' must be installed.")

            if isinstance(endpoint_api, Api):
                self.api = endpoint_api
            else:
                if endpoint_api:
                    self.api = Api(self.app, "/api")

        # if the Api exists
        if self.api:
            self.api.add_resource(EndpointResource, "/iot.io", resource_class_kwargs={
                "manager": self,
                "auth_decorator": self.auth_decorator
            })

        # list of active clients
        self.__clients: Dict[str, IoTClient] = {}

        # a dict of device types
        self.__types: Dict[str, DeviceType] = {}

        # dict which is used for storing which clients are in which rooms
        self.__rooms: Dict[str, List[str]] = {}

    # function for adding middleware
    def init_app(self, app: flask.Flask):
        app.wsgi_app = IoTManagerMiddleware(app, app.wsgi_app, self)

    # function for handling new websocket clients
    def socket(self, ws: WebSocket):
        # parse out client information from url
        args = parse(environ=ws.environ)

        # get headers
        headers = dict(ws.environ["headers_raw"])

        """
        for key, value in headers.items():
            print(key + ": ", value)
        """

        # if id is omitted
        if "IoT-IO-Id" not in headers.keys():
            # send error message to client
            self.__send_error(ws, Errors.CLIENT_NO_ID)

            raise ClientNoId()

        # if type is omitted
        if "IoT-IO-Type" not in headers.keys():
            # send error message to client
            self.__send_error(ws, Errors.CLIENT_NO_TYPE)

            raise ClientNoType()

        # if protocol version is omitted
        if "IoT-IO-ProtocolVersion" not in headers.keys():
            # send error message to client
            self.__send_error(ws, Errors.CLIENT_NO_PROTOCOL_VERSION)

            raise ClientNoProtocolVersion()

        # if data is omitted populate with default value
        if "IoT-IO-Data" not in headers.keys():
            headers["IoT-IO-Data"] = "{}"

        # if endpoints are omitted populate with default value
        if "IoT-IO-Endpoints" not in headers.keys():
            headers["IoT-IO-Endpoints"] = "[]"

        # deserialize headers
        try:
            headers["IoT-IO-Data"] = json.loads(headers["IoT-IO-Data"])
        except json.JSONDecodeError:
            # send error message to client
            self.__send_error(ws, Errors.CLIENT_INVALID_DATA)

            raise ClientInvalidData()

        try:
            headers["IoT-IO-Endpoints"] = json.loads(headers["IoT-IO-Endpoints"])
        except json.JSONDecodeError:
            # send error message to client
            self.__send_error(ws, Errors.CLIENT_INVALID_ENDPOINTS, {
                "endpointId": "",
                "endpointProblem": "invalid_json"
            })

            raise ClientInvalidEndpoints()

        # check if the client's protocol version matches that of the server
        if headers["IoT-IO-ProtocolVersion"] != __protocol_version__:
            # send error message to client
            self.__send_error(ws, Errors.CLIENT_INCOMPATIBLE_PROTOCOL_VERSION)

            raise ClientIncompatibleProtocolVersion()

        # check if the client has a valid type
        if self.__types.get(headers["IoT-IO-Type"], None) is None:
            # log and exit if the client has an invalid type
            self.logger.warning("Client with ID '" + args["id"] + "' claimed a device type of '" + args["type"]
                                + "' but no such device type was defined. Refusing connection.")

            # send error message to client
            self.__send_error(ws, Errors.CLIENT_INVALID_TYPE)

            # abort connection
            raise ClientInvalidType()

        # remove a client with the same id if it exists (getting rid of ghost clients)
        self.remove(headers["IoT-IO-Id"])

        # create a new client
        client = IoTClient(ws, headers["IoT-IO-Id"], headers["IoT-IO-Type"], headers["IoT-IO-Data"], self,
                           logging_level=self.client_logging_level, encoder=self.encoder)

        # parse endpoints
        endpoint_id, response = client.parse_endpoints(headers["IoT-IO-Endpoints"])

        if response != EndpointParseResponse.VALID:
            self.__send_error(ws, Errors.CLIENT_INVALID_ENDPOINTS, {
                "endpointId": endpoint_id,
                "endpointProblem": response.value
            })

            raise ClientInvalidEndpoints()

        self.add(client)

        # client loop
        try:
            data = ""

            while data is not None:
                # wait for message from the websocket
                data = ws.wait()

                # if the message is None check if the connection is closed
                if data is None:
                    break

                # decode received message
                event, message = self.encoder.decode(data)

                # call the callback associated with the event
                event, response = self.__handle_event_message(event, message, client)

                # check if there is a response to send to the client
                if response is not None:
                    try:
                        client.emit(event, response)
                    except ConnectionEnded:
                        return
        except BrokenPipeError:
            pass
        finally:
            self.remove(client)

    def add(self, client: IoTClient):
        """
        Add a client to the manager.

        :param client: An IoTClient instance.
        :return:
        """
        if not isinstance(client, IoTClient):
            raise TypeError("client must be an instance of IoTClient")

        # add the client to the client list
        self.__clients[client.id] = client

        # call the on_connect handler
        self.__on_connect_handlers(client)

    def remove(self, client: Union[IoTClient, str]):
        """
        Remove a client from the manager.

        :param client: Either the ID of the client as a string or a IoTClient instance
        :return:
        """
        if client is None:
            return False

        if isinstance(client, str):
            if self.__clients.get(client, None) is None:
                return False
            else:
                client = self.__clients[client]
        elif isinstance(client, IoTClient):
            pass
        else:
            raise TypeError("client must be either the id of a client as a str, or an instance of an IoTClient")

        # call the on_disconnect handler
        self.__on_disconnect_handlers(client)

        # remove the client from the rooms
        for room in self.__rooms.keys():
            # remove the client from the room
            self.__rooms[room].remove(client.id)

        # remove the client from the list of clients
        self.__clients.pop(client.id, None)

        return True

    @property
    def clients(self):
        """
        Gets a list of currently connected client IDs.

        :return: A list() of client IDs as strings.
        """
        return self.__clients.keys()

    def get_validator(self, client_id: str, endpoint_id: str) -> Union[AbstractEndpointValidator, ValidationResponse]:
        client = self.__clients.get(client_id, None)

        if client is None:
            return ValidationResponse.CLIENT_NOT_CONNECTED
        else:
            return client.get_validator(endpoint_id)

    def __send_error(self, ws: WebSocket, error: Errors, info: dict = None):
        """
        Send an error to a client via the WebSocket connection.

        :param ws: WebSocket object.
        :param error: Error which has occurred.
        :param info: Additional info about the error if needed.
        :return:
        """
        # log the error being sent
        self.logger.warning("Error being sent to client: '" + str(error.value) + "' | info: '" + str(info) + "'")

        # send the error to the client via the websocket
        ws.send(self.encoder.encode("error", {
            "error": error.value,
            "info": info
        }))

    # handles the device specific and generic on_connect handlers for the specified client
    def __on_connect_handlers(self, client: IoTClient):
        """
        Execute the generic and device specific on_connect handler.

        :param client: New client object.
        :return:
        """

        try:
            # call the type specific handler
            self.__types[client.type].on_connect(client)
        except Exception as e:
            # log the exception
            self.logger.error("Error when calling the type specific on_connect handler for client '" + client.id
                              + "': " + str(e))

        try:
            # call the generic handler
            self.on_connect(client)
        except Exception as e:
            # log the exception
            self.logger.error("Error when calling generic on_connect handler for client '" + client.id
                              + "': " + str(e))

    # handles the device specific and generic on_disconnect handlers for the specified client
    def __on_disconnect_handlers(self, client: IoTClient):
        """
        Execute the generic and device specific on_disconnect handler.

        :param client: New client object.
        :return:
        """

        try:
            # call the type specific handler
            self.__types[client.type].on_disconnect(client)
        except Exception as e:
            # log the exception
            self.logger.error("Error when calling the type specific on_disconnect handler for client '" + client.id
                              + "': " + str(e))

        try:
            # call the generic handler
            self.on_disconnect(client)
        except Exception as e:
            # log the exception
            self.logger.error("Error when calling generic on_disconnect handler for client '" + client.id
                              + "': " + str(e))

    # callback for when a client receives a message, sends it to the proper handler and squashes errors
    def __handle_event_message(self, event: str, message: str, client: IoTClient) -> event_pair:
        """
        Handles a given event and message given the client by executing the call_event_handler of the client's type.

        :param event: The event handler to trigger.
        :param message: The message to pass to the handler.
        :param client: The client object to pass to the handler.
        :return:
        """

        # activate the client type's event handler
        return self.__types[client.type].call_event_handler(event, message, client)

    def log_update(self, client: IoTClient, event: str, data: sendable):
        """
        Used by instances of IoTClient to log whenever they send data to

        :param client: Client object representing the client receiving the data.
        :param event: The event for which the data is being sent.
        :param data: The data that was sent to the client.
        :return:
        """
        try:
            self.on_update(client, event, data)
        except Exception as e:
            self.logger.error("Error when calling on_update handler: '" + str(e) + "'")

    def add_type(self, device: DeviceType):
        """
        Define a new device type for the Manager.

        :param device: Any implementation of the subclass DeviceType.
        :return: None
        """

        if not isinstance(device, DeviceType):
            raise ValueError("device is not of type DeviceType")
        elif not isinstance(device.type, str):
            raise ValueError("device.type is not of type str")

        self.__types[device.type] = device
        self.logger.debug("Successfully added DeviceType '" + device.type + "'.")

    def emit(self, event: str, data: sendable, client_id: str = None, client_type: str = None, room: str = None):
        """
        Emit function for sending data to a single client, group of client types, or room of clients.

        :param event: The client side event to send the data to.
        :param data: The data to be sent to the client(s).
        :param client_id: The id of the client to send the data to, if this param is specified client_type and room are
                          ignored.
        :param client_type: The type of client to send the message to. If it is the only param specified it will send
                            the data to all clients of the specified type, otherwise it acts as a filter on the room
                            specifier.
        :param room: A room id of which all clients should be specified. If client_type is provided it will act as a
                     filter and only send the data ot clients of that type which are also in the specified room.
        :return:
        """
        if client_id is not None:
            client = self.__clients.get(client_id, None)

            if client:
                client.emit(event, data)
        elif room is not None:
            if self.__rooms.get(room, None) is not None:
                for client_id in self.__rooms[room]:
                    client = self.__clients.get(client_id, None)

                    if client:
                        if client_type is None:
                            client.emit(event, data)
                        else:
                            if client.type == client_type:
                                client.emit(event, data)
        elif client_type is not None:
            for client in self.__clients.values():
                if client.type == client_type:
                    client.emit(event, data)
        else:
            raise ValueError("'client_id', 'client_type', or 'room' must be provided")

    def join(self, client: Union[IoTClient, str], room: str, **kwargs):
        """
        Add a client to a specified room.

        :param client: ID of a client as a string or an instance of a IoTClient
        :param room: ID of the room to be joined as a string
        :return:
        """
        if not isinstance(client, str) and not isinstance(client, IoTClient):
            raise TypeError("'client' must be the ID of the client as a str")
        elif not isinstance(room, str):
            raise TypeError("'room' must be an instance of str")

        if isinstance(client, IoTClient):
            client = client.id

        if self.__clients.get(client, None) is None:
            return

        if not kwargs.pop("called_by_client", False):
            self.__clients[client].join(room, called_by_manager=True)

        if self.__rooms.get(room, None) is None:
            self.__rooms[room] = [client]
        else:
            self.__rooms[room].append(client)

    def leave(self, client: Union[IoTClient, str], room: str, **kwargs):
        """
        Remove a client from a specified room.

        :param client: ID of a client as a string or an instance of a IoTClient
        :param room: ID of the room to be left as a string
        :return:
        """
        if not isinstance(client, str):
            raise TypeError("'client' must be the ID of the client as a str")
        elif not isinstance(room, str):
            raise TypeError("'room' must be an instance of str")

        if isinstance(client, IoTClient):
            client = client.id

        if self.__clients.get(client, None) is None:
            return

        if not kwargs.pop("called_by_client", False):
            self.__clients[client].join(room, called_by_manager=True)

        if self.__rooms.get(room, None) is None:
            return
        else:
            self.__rooms[room].remove(client)

    def close_room(self, room: str):
        """
        Close a room and remove all of it's clients.

        :param room: ID of the room to be closed
        :return:
        """
        if not isinstance(room, str):
            raise TypeError("'room' must be an instance of str")

        rooms = self.__rooms.pop(room, None)

        if rooms:
            for client in rooms:
                client = self.__clients.get(client, None)
                if client:
                    client.leave(room, called_by_manager=True)

    # event decorator function
    def event(self, coroutine):
        """
        Decorator which allows for simple overwriting of the generic on_connect, and
        on_disconnect functions.

        :param coroutine: Function named on_connect, on_disconnect, or on_update.
        :return: bool
        """

        # handle general on_connect, and on_disconnect, and on_update handlers
        if coroutine.__name__ == "on_connect" or coroutine.__name__ == "on_disconnect" or \
                coroutine.__name__ == "on_update":
            # logging output
            self.logger.info("Event handler '" + coroutine.__name__ + "' was added successfully.")

            # replaces the existing coroutine with the provided one
            setattr(self, coroutine.__name__, coroutine)
            return True
        return False

    def on_connect(self, client: IoTClient):
        """
        An empty implementation of the generic on_connect function, meant to be overwritten.

        Runs when any client connects to the server.

        :param client: Client object representing the connecting client.
        :return: None or str.
        """
        pass

    def on_disconnect(self, client: IoTClient):
        """
        An empty implementation of the generic on_disconnect function, meant to be overwritten.

        Runs when any client disconnects from the server.

        :param client: Client object representing the disconnecting client.
        :return: None.
        """
        pass

    def on_update(self, client: IoTClient, event: str, data: sendable):
        """
        An empty implementation of the on_update function, meant to be written overwritten.

        Runs whenever data is emitted from the server to a client.

        :param client: Client object representing the client receiving the data.
        :param event: The event for which the data is being sent.
        :param data: The data that was sent to the client.
        :return:
        """
        pass


def emit(event: str, data: sendable, client_id: str = None, client_type: str = None, room: str = None):
    """
    Emit function for sending data to a single client, group of client types, or room of clients.

    :param event: The client side event to send the data to.
    :param data: The data to be sent to the client(s).
    :param client_id: The id of the client to send the data to, if this param is specified client_type and room are
                      ignored.
    :param client_type: The type of client to send the message to. If it is the only param specified it will send
                        the data to all clients of the specified type, otherwise it acts as a filter on the room
                        specifier.
    :param room: A room id of which all clients should be specified. If client_type is provided it will act as a
                 filter and only send the data ot clients of that type which are also in the specified room.
    :return:
    """
    return flask.current_app.extensions["iot.io"].emit(event, data, client_id, client_type, room)


def join(client: Union[IoTClient, str], room: str):
    """
    Add a client to a specified room.

    :param client: ID of a client as a string or an instance of a IoTClient
    :param room: ID of the room to be joined as a string
    :return:
    """
    return flask.current_app.extensions["iot.io"].emit(client, room)


def leave(client: Union[IoTClient, str], room: str):
    """
    Remove a client from a specified room.

    :param client: ID of a client as a string or an instance of a IoTClient
    :param room: ID of the room to be left as a string
    :return:
    """
    return flask.current_app.extensions["iot.io"].emit(client, room)


def close_room(room: str):
    """
    Close a room and remove all of it's clients.

    :param room: ID of the room to be closed
    :return:
    """
    return flask.current_app.extensions["iot.io"].close_room(room)
