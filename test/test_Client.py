from unittest import TestCase
from iotio import IoTClient
from iotio.PacketEncoder import DefaultPacketEncoder
from iotio.exceptions import ConnectionEnded
from eventlet.websocket import WebSocket
from typing import List


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

    client = IoTClient(c_socket, c_id, c_type, c_data, c_endpoints)

    def test_id(self):
        self.assertEqual(self.client.id, self.c_id)

    def test_type(self):
        self.assertEqual(self.client.type, self.c_type)

    def test_data(self):
        self.assertEqual(self.client.data, self.c_data)

    def test_send(self):
        try:
            self.client.send("test", "data")
        except ConnectionEnded:
            self.fail()

        self.c_socket.websocket_closed = True
        try:
            self.client.send("test", "data")
            self.fail()
        except ConnectionEnded:
            pass
        self.c_socket.websocket_closed = False
