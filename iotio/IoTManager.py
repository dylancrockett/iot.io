# default lib imports
import logging
from geventwebsocket.websocket import WebSocket
from typing import List, Dict

# external lib imports
from flask import Flask
from flask_sockets import Sockets

# lib imports
from .IoTClient import IoTClient
from .DeviceType import DeviceType
from .error import ConnectionEnded
from .types import event_pair


# main server class
class IoTManager:
    """
    Main iot.io server for managing clients. Uses flask-sockets as the websocket endpoint. Requires a Flask instance
    to hook onto for the flask-sockets server.
    """

    def __init__(self, flask_app: Flask, logging_level: int = logging.ERROR, client_logging_level: int = logging.ERROR):
        # websocket server run off of a flask app
        self.sockets = Sockets(flask_app)

        # list of active clients
        self.__clients: List[IoTClient]
        self.__clients = []

        # a dict of device types
        self.__types: Dict[str, DeviceType]
        self.__types = {}

        # logger for the manager
        self.logger = logging.Logger("[iot.io.server]")

        # logging levels for main and client debuggers
        self.logger.setLevel(logging_level)
        self.client_logging_level = client_logging_level

        # route fo clients to connect to
        @self.sockets.route('/iot.io')
        def socket(ws: WebSocket):
            # create a new client
            try:
                # create a new client object if the client sends the handshake packet successfully
                client = IoTClient(ws, client_logging_level)
            except ConnectionEnded:
                # exit if the handshake fails
                return

            # check if the client has a valid type
            if self.__types.get(client.type, None) is None:
                # log and exit if the client has an invalid type
                self.logger.warning("Client with ID '" + client.id + "' claimed a device type of '" + client.type
                                    + "' but no such device type was defined. Refusing connection.")
                return

            # add the client to the client list
            self.__clients.append(client)

            # call the on_connect handler
            self.__on_connect_handlers(client)

            # begin the loop of accepting messages for the client
            client.loop(self.__handle_event_message)

            # call the on_disconnect handler
            self.__on_disconnect_handlers(client)

            # remove the client from the list of clients
            self.__clients = [x for x in self.__clients if client.id != x.__id]

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

    # used to add a new device type to the manager
    def add_type(self, device: DeviceType):
        """
        Define a new device type for the Manager.

        :param device: Any implementation of the subclass DeviceType.
        :return: None
        """

        # ensure the device is of type DeviceType
        if not isinstance(device, DeviceType):
            raise ValueError("device is not of type DeviceType")

        # ensure device.type is of type str
        if not isinstance(device.type, str):
            raise ValueError("device.type is not of type str")

        # add the device to the list of device types
        self.__types.update({device.type: device})

        # logging output
        self.logger.debug("Successfully added DeviceType '" + device.type + "'.")

    # event decorator function
    def event(self, coroutine):
        """
        Decorator which allows for simple overwriting of the generic on_connect, and
        on_disconnect functions.

        :param coroutine: Function named on_connect, or on_disconnect.
        :return: bool
        """

        # handle general on_connect, and on_disconnect handlers
        if coroutine.__name__ == "on_connect" or coroutine.__name__ == "on_disconnect":
            # logging output
            self.logger.info("Event handler '" + coroutine.__name__ + "' was added successfully.")

            # replaces the existing coroutine with the provided one
            setattr(self, coroutine.__name__, coroutine)
            return True
        return False

    def on_connect(self, client: IoTClient):
        """
        A empty implementation of the generic on_connect function, meant to be overwritten.

        Runs when any device connects to the server.

        :param client: Client object representing the connecting client.
        :return: None or str.
        """
        pass

    def on_disconnect(self, client: IoTClient):
        """
        A empty implementation of the generic on_disconnect function, meant to be overwritten.

        Runs when any device disconnects from the server.

        :param client: Client object representing the disconnecting client.
        :return: None.
        """
        pass
