# default lib imports
from typing import TYPE_CHECKING, Tuple, Union
if TYPE_CHECKING:
    from .Manager import IoTManager
import logging

# external lib imports
import flask
from eventlet.websocket import WebSocket

# lib imports
from .PacketEncoder import AbstractPacketEncoder, DefaultPacketEncoder
from .types import sendable
from .Endpoint import EndpointManager, EndpointParseResponse, ValidationResponse, AbstractEndpointValidator


# iot client class
class IoTClient:
    def __init__(self, ws: WebSocket, client_id: str, client_type: str, client_data: dict, manager: 'IoTManager',
                 logging_level: int = logging.ERROR, encoder: AbstractPacketEncoder = DefaultPacketEncoder):
        """
        Class which represents an active connection by a IoTClient and is used to manage that connection.

        :param ws: WebSocket object which is the connection used to communicate between the client and server.
        :param client_id: ID of the connecting client, should be a unique identifier which can be used to identify the
                          client over multiple connections.
        :param client_type: The type of the client, used to separate different types of connecting devices.
        :param client_data: JSON data provided by the client at time of connection.
        :param logging_level: Logging level of the instance, useful for debugging.
        :param encoder: A instance of a AbstractPacketEncoder implementation, used to define how packets should be
                        encoded/decoded from binary by the server when communicating with the client. Shouldn't be
                        changed unless the user has a good understanding of how the iot.io protocol works.
        """
        self.logger = logging.Logger("[iot.io.client:" + client_id + "]")
        self.logger.level = logging_level

        # reference to the client's websocket connection
        self.socket = ws

        # reference to the IoTManager
        self.manager = manager

        # encoder used for encoding and decoding packets
        self.encoder = encoder

        # the list of rooms the client is in
        self.__rooms = []

        # save the id and type
        self.__id = client_id
        self.__type = client_type
        self.__data = client_data

        # endpoint validation manager
        self.__endpoint_manager = EndpointManager()

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

    @property
    def rooms(self):
        return self.__rooms

    # get the endpoint_validator
    def get_validator(self, endpoint_id: str) -> Union[AbstractEndpointValidator, ValidationResponse]:
        if self.__endpoint_manager.initialized:
            return self.__endpoint_manager.get_validator(endpoint_id=endpoint_id)
        else:
            return ValidationResponse.CLIENT_ENDPOINTS_NOT_INITIALIZED

    def parse_endpoints(self, endpoints) -> Tuple[str, EndpointParseResponse]:
        return self.__endpoint_manager.parse(endpoints)

    def emit(self, event: str, data: sendable):
        """
        Emit function for sending data to the client.

        :param event: The client side event to send the data to.
        :param data: The data to be sent to the client(s).
        :return:
        """
        if not isinstance(event, str):
            raise TypeError("'event' must be of type str")

        if not self.socket.websocket_closed:
            self.logger.debug("Sending a message for event '", event, "' with type: '", type(data), "'")

            self.socket.send(self.encoder.encode(event, data))
            self.manager.log_update(self, event, data)

    def join(self, room: str, **kwargs):
        """
        Have the client join the specified room.

        :param room: ID of the room to be joined as a string
        :return:
        """
        if not kwargs.pop("called_by_manager", False):
            self.manager.join(self, room, called_by_client=True)

        self.__rooms.append(room)

    def leave(self, room: str, **kwargs):
        """
        Have the client leave the specified room.

        :param room: ID of the room to be left as a string
        :return:
        """
        if not kwargs.pop("called_by_manager", False):
            self.manager.leave(self, room, called_by_client=True)

        self.__rooms.remove(room)
