# default
import enum
import json
from .types import sendable
from abc import abstractmethod
from typing import Tuple


class PacketDataType(enum.IntEnum):
    # default data types supported
    BINARY = 0
    BOOLEAN = 1
    INTEGER = 2
    STRING = 3
    JSON = 4

    @staticmethod
    def type_to_byte(message: sendable) -> bytearray:
        byte = [0]

        if isinstance(message, bytearray) or isinstance(message, bytes):
            byte = PacketDataType.BINARY.to_bytes(1, "big")
        elif isinstance(message, bool):
            byte = PacketDataType.BOOLEAN.to_bytes(1, "big")
        elif isinstance(message, int):
            byte = PacketDataType.INTEGER.to_bytes(1, "big")
        elif isinstance(message, str):
            byte = PacketDataType.STRING.to_bytes(1, "big")
        elif isinstance(message, dict) or isinstance(message, list):
            byte = PacketDataType.JSON.to_bytes(1, "big")

        return bytearray(byte)


class AbstractPacketEncoder:
    """
    Abstract implementation of a PacketEncoder. Should be used as the base class for any custom PacketEncoder classes.
    """
    @staticmethod
    @abstractmethod
    def encode(event: str, message: sendable) -> bytearray:
        return bytearray([])

    @staticmethod
    @abstractmethod
    def decode(data: bytearray) -> Tuple[str, sendable]:
        return "", ""


# packet object used to encode and decode messages over the iot.io protocol, can be overwritten if desired
class DefaultPacketEncoder(AbstractPacketEncoder):
    """
    The default PackedEncoder used by the iot.io protocol. Can be changed if a custom implementation is desired.
    """
    @staticmethod
    def encode(event: str, message: sendable) -> bytearray:
        # get the message type
        message_type = PacketDataType.type_to_byte(message)

        # serialize event
        event = event.encode("UTF-8", "ignore")

        # serialize message as json if it is a dict or list
        if isinstance(message, dict) or isinstance(message, list):
            message = json.dumps(message).encode("UTF-8", "ignore")
        # serialize message if it is a boolean
        elif isinstance(message, bool):
            message = message.to_bytes(1, byteorder="big", signed=False)
        # serialize message if it is an int
        elif isinstance(message, int):
            message = message.to_bytes(8, byteorder="big", signed=True)
        # serialize message using utf8 if it is a string
        elif isinstance(message, str):
            message = bytearray(str(message).encode("UTF-8", "ignore"))
        elif isinstance(message, bytearray) or isinstance(message, bytes):
            message = bytearray(message)
        else:
            raise ValueError("Cannot encode message of type '" + type(message)
                             + "'. Please only use the default supported types: [bytes, bytearray, int, string, "
                               "list, dict]. If you would like to support other types then please create and provide "
                               "your own PacketEncoder.")

        # get the size of each
        event_size = len(event).to_bytes(2, byteorder="big", signed=False)
        message_size = len(message).to_bytes(4, byteorder="big", signed=False)

        # return the fully encoded packet
        return message_type + event_size + event + message_size + message

    @staticmethod
    def decode(data: bytearray) -> Tuple[str, sendable]:
        # get the type byte
        message_type = data[0]

        # get event size
        event_size = int.from_bytes(data[1:3], byteorder="big", signed=False)

        # get the event
        event = data[3:event_size + 3].decode("UTF-8", "ignore")

        # get the message size
        message_size = int.from_bytes(data[event_size + 3:event_size + 7], byteorder="big", signed=False)

        # get the message bytes
        message_bytes = data[event_size + 7: event_size + message_size + 7]

        # deserialize json
        if message_type == PacketDataType.JSON:
            message = json.loads(message_bytes.decode("UTF-8", "ignore"))
        # deserialize bool
        elif message_type == PacketDataType.BOOLEAN:
            message = bool.from_bytes(message_bytes, byteorder="big", signed=False)
        # deserialize int
        elif message_type == PacketDataType.INTEGER:
            message = int.from_bytes(message_bytes, byteorder="big", signed=True)
        # deserialize string
        elif message_type == PacketDataType.STRING:
            message = message_bytes.decode("UTF-8", "ignore")
        else:
            message = message_bytes

        # return decoded event and message as a pair
        return event, message
