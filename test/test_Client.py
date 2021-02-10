from unittest import TestCase
from flask import Flask
from iotio import IoTManager, IoTClient
from iotio.PacketEncoder import DefaultPacketEncoder
from iotio.types import sendable
from eventlet.websocket import WebSocket
from typing import List


# used for testing TestIotClient, pretends to be a functioning IoTManager
class TestIoTManager(IoTManager):
    def __init__(self):
        app = Flask("")
        super().__init__(app)

    def log_update(self, client: IoTClient, event: str, data: sendable):
        pass


# used for testing TestIoTClient, pretends to be a functioning eventlet WebSocket object
class TestWebSocket(WebSocket):
    def __init__(self, messages: List[str] = None):
        self.messages = []
        self.closed = False

        if messages is None:
            messages = ["abc", "def", "ghi"]

        messages.append("stop")

        for m in messages:
            self.messages.append(DefaultPacketEncoder.encode("test", m))

        super().__init__(None, {})

    @property
    def websocket_closed(self):
        return self.closed

    @websocket_closed.setter
    def websocket_closed(self, data: bool):
        self.closed = data

    def send(self, data: bytearray):
        pass

    def wait(self):
        return self.messages.pop(0)


class TestIoTClient(TestCase):
    c_socket = TestWebSocket()
    c_id = "test_client"
    c_type = "test"
    c_data = {
        "count": 5
    }
    c_endpoints = []

    client = IoTClient(c_socket, c_id, c_type, c_data, TestIoTManager())

    def test_id(self):
        self.assertEqual(self.client.id, self.c_id)

    def test_type(self):
        self.assertEqual(self.client.type, self.c_type)

    def test_data(self):
        self.assertEqual(self.client.data, self.c_data)

    # noinspection PyBroadException
    def test_send(self):
        try:
            self.client.emit("test", "data")
        except Exception:
            self.fail()

        self.c_socket.websocket_closed = True
        try:
            self.client.emit("test", "data")
            self.fail()
        except Exception:
            pass
        self.c_socket.websocket_closed = False
