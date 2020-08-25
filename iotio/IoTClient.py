# default lib imports
from typing import Callable
import re
import json
import logging

# external lib imports
from geventwebsocket.websocket import WebSocket
from gevent import Timeout

# lib imports
from .error import ConnectionEnded
from .types import event_pair, sendable


# iot client class
class IoTClient:
    def __init__(self, ws: WebSocket, logging_level: int = logging.ERROR):
        # logger for the new client
        self.logger = logging.Logger("[iot.io.client:New Client]")
        self.logger.level = logging_level

        # reference to the client's websocket connection
        self.socket = ws

        # receive, waiting for the client to send the handshake packet, 30 second timeout before the connection closes
        with Timeout(30, False):
            # get the message
            message = ws.receive()

            # parse it
            self.__id, self.__type, self.__data = self.handshake(message)

            # set the new logger name
            self.logger.name = "[iot.io.client:" + self.__id + "]"

    # properties for id, type, and data
    @property
    def id(self):
        return self.__id

    @property
    def type(self):
        return self.__type

    @property
    def data(self):
        return self.__data

    # parse a iot.io packet and return the contents as a list
    @staticmethod
    def parse(message: str) -> list:
        """
        Messages between the client and server are formatted as a list, which each
         element being an argument. For example the handshake packet the client first sends to the server
         is structured like the following list: (id, type, data).

         This same packet would be sent as the following string by the client:
            '[/"1"/][/"id"/][/"type"/][/"data"/]'

        This parser takes than string and converts it to the following list:
            ['1', 'id', 'type', 'data']

        :param message: the message to be parsed as a string
        :return: a list of parsed arguments
        """

        # parse the message to return contents
        result = re.findall("\[/\"([^[\]]*)\"/\]", message)

        return result

    # parse a handshake packet, handle errors and notify the client
    def handshake(self, message: str):
        # parse the packet first
        args = self.parse(message)

        if len(args) != 3:
            # send an error message to client and end the connection
            self.logger.warning("Invalid handshake message, ending connection.")
            # TODO figure out an error system to notify clients
            self.socket.close()

            # raise the connection end error
            raise ConnectionEnded

        return args[0], args[1], args[2]

    # parse a normal message packet
    def parse_message(self, packet: str) -> event_pair:
        """
        Parse what is expected to be a basic iot.io message, returning the event and message

        :param packet: The iot.io packet to parse.
        :return: A event pair. [(None, None) or (str, sendable)]
        """
        # parse the packet
        args = self.parse(packet)

        # check for correct length
        if len(args) != 2:
            self.logger.warning("When attempting to parse a client message a invalid message format was received. ("
                                "Raw Message: " + str(packet) + " | Parsed Message: " + str(args) + ")")
            return None, None

        # attempt deserialization of message
        try:
            args[1] = json.loads(args[1])
        except ValueError or json.JSONDecodeError:
            pass

        # return the event and the message
        return args[0], args[1]

    # sends event message to the client
    def send(self, event: str, message: sendable):
        # check type of message
        if not isinstance(message, (bool, int, float, str, dict)):
            raise ValueError("A non-sendable value was passed to a client's send method.")

        # conversions from sendable to string
        if isinstance(message, dict):
            # serialize the dict as a json string
            message = json.dumps(message)
        # convert generics to string counterpart
        else:
            # convert to string
            message = str(message)

        # check if the connection is alive
        if not self.socket.closed:
            # logging
            self.logger.debug("Sending a message for event '" + event + "':" + message)

            # send the message
            self.socket.send("[/\"" + event + "\"/][/\"" + message + "\"/]")
        else:
            raise ConnectionEnded

    # loops and receives messages from the client and calls the specified callback when one is received
    def loop(self, callback: Callable[[str, sendable, 'IoTClient'], event_pair]):
        """
        Runs a loop which accepts client messages until the client closes the connection.

        :param callback: A callback function which accepts the event, message, and Client.
        :return: None
        """

        # loop while the connection is still alive
        while not self.socket.closed:
            # receive from the client
            message = self.socket.receive()

            # if the message is None then client connection has ended so exit the loop
            if message is None:
                break

            # parse the message
            event, message = self.parse_message(message)

            # check if even is none
            if event is not None:
                # call the callback
                event, response = callback(event, message, self)

                # check if there is a response to send to the client
                if response is not None:
                    try:
                        self.send(event, response)
                    except ConnectionEnded:
                        break
