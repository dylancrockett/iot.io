from unittest import TestCase
from iotio.PacketEncoder import PacketDataType, DefaultPacketEncoder


class TestPacketDataType(TestCase):
    def test_type_to_byte(self):
        self.assertEqual(PacketDataType.type_to_byte(b'\xFF'), PacketDataType.BINARY.to_bytes(1, "big"))
        self.assertEqual(PacketDataType.type_to_byte(True), PacketDataType.BOOLEAN.to_bytes(1, "big"))
        self.assertEqual(PacketDataType.type_to_byte(20), PacketDataType.INTEGER.to_bytes(1, "big"))
        self.assertEqual(PacketDataType.type_to_byte("data"), PacketDataType.STRING.to_bytes(1, "big"))
        self.assertEqual(PacketDataType.type_to_byte({"a": 5}), PacketDataType.JSON.to_bytes(1, "big"))


class TestDefaultPacketEncoder(TestCase):
    binary = b'\x45\x0F\x24'
    binary_enc = None

    boolean = True
    boolean_enc = None

    integer_1 = 15409255571
    integer_1_enc = None

    integer_2 = -1204519556
    integer_2_enc = None

    string = "some_data"
    string_enc = None

    json = {
        "test": 5,
        "a": ["a", 2, False, {"a": None}],
        "b": None,
        "c": True
    }
    json_enc = None

    def test_encode(self):
        try:
            self.binary_enc = DefaultPacketEncoder.encode("test", self.binary)
            self.boolean_enc = DefaultPacketEncoder.encode("test", self.boolean)
            self.integer_1_enc = DefaultPacketEncoder.encode("test", self.integer_1)
            self.integer_2_enc = DefaultPacketEncoder.encode("test", self.integer_2)
            self.string_enc = DefaultPacketEncoder.encode("test", self.string)
            self.json_enc = DefaultPacketEncoder.encode("test", self.json)
        except ValueError:
            self.fail()

    def test_decode(self):
        # ensure encoding is completed for test decoding is done
        self.test_encode()

        self.assertEqual(self.binary, DefaultPacketEncoder.decode(self.binary_enc)[1])
        self.assertEqual(self.boolean, DefaultPacketEncoder.decode(self.boolean_enc)[1])
        self.assertEqual(self.integer_1, DefaultPacketEncoder.decode(self.integer_1_enc)[1])
        self.assertEqual(self.integer_2, DefaultPacketEncoder.decode(self.integer_2_enc)[1])
        self.assertEqual(self.string, DefaultPacketEncoder.decode(self.string_enc)[1])
        self.assertEqual(self.json, DefaultPacketEncoder.decode(self.json_enc)[1])
