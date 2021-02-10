from unittest import TestCase
from iotio.Endpoint import ValidationResponse, EndpointType, AbstractEndpointValidator, BooleanEndpointValidator, \
    IntegerEndpointValidator, StringEndpointValidator, EnumEndpointValidator, EndpointParseResponse


class TestAbstractEndpointValidator(TestCase):
    validator = AbstractEndpointValidator("abc", "def", "ghi")

    def test_validate(self):
        self.assertIsNone(self.validator.validate(None))

    def test_parse(self):
        val_1 = self.validator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c"
        })
        val_1: AbstractEndpointValidator

        self.assertIsNotNone(val_1)
        self.assertEqual(val_1.id, "a")
        self.assertEqual(val_1.name, "b")
        self.assertEqual(val_1.special_id, "c")

        val_2 = self.validator.parse({
            "id": "d",
            "name": "e",
            "specialId": None
        })
        val_2: AbstractEndpointValidator

        self.assertIsNotNone(val_2)
        self.assertEqual(val_2.id, "d")
        self.assertEqual(val_2.name, "e")
        self.assertEqual(val_2.special_id, None)

        self.assertEqual(self.validator.parse({
            "id": 1,
            "name": "b",
            "specialId": "c"
        }), EndpointParseResponse.ID_MUST_BE_STRING)

        self.assertEqual(self.validator.parse({
            "id": "a",
            "name": 1,
            "specialId": "c"
        }), EndpointParseResponse.NAME_MUST_BE_STRING)

        self.assertEqual(self.validator.parse({
            "id": "",
            "name": "b",
            "specialId": 1
        }), EndpointParseResponse.SPECIAL_ID_MUST_BE_STRING)

    def test__dict__(self):
        data = self.validator.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("specialId", None), "ghi")


class TestBooleanEndpointValidator(TestCase):
    validator = BooleanEndpointValidator("abc", "def", "ghi")

    def test_validate(self):
        self.assertEqual(self.validator.validate(True), ValidationResponse.VALID)
        self.assertEqual(self.validator.validate("test"), ValidationResponse.INVALID_TYPE)

    def test_parse(self):
        val_1 = self.validator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c"
        })

        self.assertIsNotNone(val_1)
        self.assertEqual(val_1.id, "a")
        self.assertEqual(val_1.name, "b")
        self.assertEqual(val_1.special_id, "c")

        val_2 = self.validator.parse({
            "id": "d",
            "name": "e",
            "specialId": None
        })

        self.assertIsNotNone(val_2)
        self.assertEqual(val_2.id, "d")
        self.assertEqual(val_2.name, "e")
        self.assertIsNone(val_2.special_id)

        self.assertEqual(self.validator.parse({
            "id": 1,
            "name": "b",
            "specialId": "c"
        }), EndpointParseResponse.ID_MUST_BE_STRING)

        self.assertEqual(self.validator.parse({
            "id": "a",
            "name": 1,
            "specialId": "c"
        }), EndpointParseResponse.NAME_MUST_BE_STRING)

        self.assertEqual(self.validator.parse({
            "id": "",
            "name": "b",
            "specialId": 1
        }), EndpointParseResponse.SPECIAL_ID_MUST_BE_STRING)

    def test__dict__(self):
        data = self.validator.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.BOOLEAN.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNone(data.get("constraints", ""))


class TestNumberEndpointValidator(TestCase):
    validator_1 = IntegerEndpointValidator("abc", "def", "ghi", 5, 10)
    validator_2 = IntegerEndpointValidator("abc", "def", "ghi", 5)
    validator_3 = IntegerEndpointValidator("abc", "def", "ghi", None, 10)
    validator_4 = IntegerEndpointValidator("abc", "def", "ghi", 5, 10, 1)
    validator_5 = IntegerEndpointValidator("abc", "def", "ghi")

    def test_validate(self):
        self.assertEqual(self.validator_1.validate(7), ValidationResponse.VALID)
        self.assertEqual(self.validator_1.validate(3), ValidationResponse.LOWER_THAN_MIN)
        self.assertEqual(self.validator_1.validate(12), ValidationResponse.HIGHER_THAN_MAX)
        self.assertEqual(self.validator_1.validate(""), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_2.validate(7), ValidationResponse.VALID)
        self.assertEqual(self.validator_2.validate(3), ValidationResponse.LOWER_THAN_MIN)
        self.assertEqual(self.validator_2.validate(12), ValidationResponse.VALID)
        self.assertEqual(self.validator_2.validate(""), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_3.validate(7), ValidationResponse.VALID)
        self.assertEqual(self.validator_3.validate(3), ValidationResponse.VALID)
        self.assertEqual(self.validator_3.validate(12), ValidationResponse.HIGHER_THAN_MAX)
        self.assertEqual(self.validator_3.validate(""), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_4.validate(7), ValidationResponse.VALID)
        self.assertEqual(self.validator_4.validate(3), ValidationResponse.LOWER_THAN_MIN)
        self.assertEqual(self.validator_4.validate(12), ValidationResponse.HIGHER_THAN_MAX)
        self.assertEqual(self.validator_4.validate(""), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_5.validate(7), ValidationResponse.VALID)
        self.assertEqual(self.validator_5.validate(3), ValidationResponse.VALID)
        self.assertEqual(self.validator_5.validate(12), ValidationResponse.VALID)
        self.assertEqual(self.validator_5.validate(""), ValidationResponse.INVALID_TYPE)

    def test_parse(self):
        val_1 = self.validator_1.parse(self.validator_1.__dict__())
        val_1: IntegerEndpointValidator

        self.assertEqual(val_1.id, self.validator_1.id)
        self.assertEqual(val_1.name, self.validator_1.name)
        self.assertEqual(val_1.special_id, self.validator_1.special_id)
        self.assertEqual(val_1.min, self.validator_1.min)
        self.assertEqual(val_1.max, self.validator_1.max)
        self.assertEqual(val_1.increment, self.validator_1.increment)

        val_2 = self.validator_2.parse(self.validator_2.__dict__())
        val_2: IntegerEndpointValidator

        self.assertEqual(val_2.id, self.validator_2.id)
        self.assertEqual(val_2.name, self.validator_2.name)
        self.assertEqual(val_2.special_id, self.validator_2.special_id)
        self.assertEqual(val_2.min, self.validator_2.min)
        self.assertEqual(val_2.max, self.validator_2.max)
        self.assertEqual(val_2.increment, self.validator_2.increment)

        val_3 = self.validator_3.parse(self.validator_3.__dict__())
        val_3: IntegerEndpointValidator

        self.assertEqual(val_3.id, self.validator_3.id)
        self.assertEqual(val_3.name, self.validator_3.name)
        self.assertEqual(val_3.special_id, self.validator_3.special_id)
        self.assertEqual(val_3.min, self.validator_3.min)
        self.assertEqual(val_3.max, self.validator_3.max)
        self.assertEqual(val_3.increment, self.validator_3.increment)

        val_4 = self.validator_4.parse(self.validator_4.__dict__())
        val_4: IntegerEndpointValidator

        self.assertEqual(val_4.id, self.validator_4.id)
        self.assertEqual(val_4.name, self.validator_4.name)
        self.assertEqual(val_4.special_id, self.validator_4.special_id)
        self.assertEqual(val_4.min, self.validator_4.min)
        self.assertEqual(val_4.max, self.validator_4.max)
        self.assertEqual(val_4.increment, self.validator_4.increment)

        val_5 = self.validator_5.parse(self.validator_5.__dict__())
        val_5: IntegerEndpointValidator

        self.assertEqual(val_5.id, self.validator_5.id)
        self.assertEqual(val_5.name, self.validator_5.name)
        self.assertEqual(val_5.special_id, self.validator_5.special_id)
        self.assertEqual(val_5.min, self.validator_5.min)
        self.assertEqual(val_5.max, self.validator_5.max)
        self.assertEqual(val_5.increment, self.validator_5.increment)

        self.assertEqual(IntegerEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "min": "",
                "max": 10,
                "increment": None
            }
        }), EndpointParseResponse.CONSTRAINT_MIN_MUST_BE_INT)

        self.assertEqual(IntegerEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "min": 5,
                "max": "",
                "increment": None
            }
        }), EndpointParseResponse.CONSTRAINT_MAX_MUST_BE_INT)

        self.assertEqual(IntegerEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "min": 5,
                "max": 10,
                "increment": ""
            }
        }), EndpointParseResponse.CONSTRAINT_INCREMENT_MUST_BE_INT)

    def test__dict__(self):
        data = self.validator_1.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.INTEGER.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("min", None), 5)
        self.assertEqual(data.get("constraints").get("max", None), 10)
        self.assertIsNone(data.get("constraints").get("increment", ""))

        data = self.validator_2.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.INTEGER.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("min", None), 5)
        self.assertIsNone(data.get("constraints").get("max", ""))
        self.assertIsNone(data.get("constraints").get("increment", None))

        data = self.validator_3.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.INTEGER.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertIsNone(data.get("constraints").get("min", ""))
        self.assertEqual(data.get("constraints").get("max", None), 10)
        self.assertIsNone(data.get("constraints").get("increment", ""))

        data = self.validator_4.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.INTEGER.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("min", None), 5)
        self.assertEqual(data.get("constraints").get("max", None), 10)
        self.assertEqual(data.get("constraints").get("increment", None), 1)

        data = self.validator_5.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.INTEGER.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertIsNone(data.get("constraints").get("min", ""))
        self.assertIsNone(data.get("constraints").get("max", ""))
        self.assertIsNone(data.get("constraints").get("increment", ""))


class TestStringEndpointValidator(TestCase):
    validator_1 = StringEndpointValidator("abc", "def", "ghi", 3, "abc")
    validator_2 = StringEndpointValidator("abc", "def", "ghi", 3, None, "abc")
    validator_3 = StringEndpointValidator("abc", "def", "ghi", 3, ["one", "two", "thr"])
    validator_4 = StringEndpointValidator("abc", "def", "ghi", 3, None, ["one", "two", "thr"])
    validator_5 = StringEndpointValidator("abc", "def", "ghi")

    def test_validate(self):
        self.assertEqual(self.validator_1.validate("abc"), ValidationResponse.VALID)
        self.assertEqual(self.validator_1.validate("a"), ValidationResponse.INVALID_LENGTH)
        self.assertEqual(self.validator_1.validate("def"), ValidationResponse.VIOLATES_ALLOW_LIST)
        self.assertEqual(self.validator_1.validate(1), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_2.validate("def"), ValidationResponse.VALID)
        self.assertEqual(self.validator_2.validate("a"), ValidationResponse.INVALID_LENGTH)
        self.assertEqual(self.validator_2.validate("abc"), ValidationResponse.VIOLATES_DENY_LIST)
        self.assertEqual(self.validator_2.validate(1), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_3.validate("one"), ValidationResponse.VALID)
        self.assertEqual(self.validator_3.validate("two"), ValidationResponse.VALID)
        self.assertEqual(self.validator_3.validate("thr"), ValidationResponse.VALID)
        self.assertEqual(self.validator_3.validate("one_two"), ValidationResponse.INVALID_LENGTH)
        self.assertEqual(self.validator_3.validate("foo"), ValidationResponse.VIOLATES_ALLOW_LIST)
        self.assertEqual(self.validator_3.validate(1), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_4.validate("foo"), ValidationResponse.VALID)
        self.assertEqual(self.validator_4.validate("one_two"), ValidationResponse.INVALID_LENGTH)
        self.assertEqual(self.validator_4.validate("one"), ValidationResponse.VIOLATES_DENY_LIST)
        self.assertEqual(self.validator_4.validate("two"), ValidationResponse.VIOLATES_DENY_LIST)
        self.assertEqual(self.validator_4.validate("thr"), ValidationResponse.VIOLATES_DENY_LIST)
        self.assertEqual(self.validator_4.validate(1), ValidationResponse.INVALID_TYPE)

        self.assertEqual(self.validator_5.validate("abc_def_ghi_jkl_mno"), ValidationResponse.VALID)
        self.assertEqual(self.validator_5.validate("qwe_rty_uio"), ValidationResponse.VALID)
        self.assertEqual(self.validator_5.validate(1), ValidationResponse.INVALID_TYPE)

    def test_parse(self):
        val_1 = self.validator_1.parse(self.validator_1.__dict__())
        val_1: StringEndpointValidator

        self.assertEqual(val_1.id, self.validator_1.id)
        self.assertEqual(val_1.name, self.validator_1.name)
        self.assertEqual(val_1.special_id, self.validator_1.special_id)
        self.assertEqual(val_1.length, self.validator_1.length)
        self.assertEqual(val_1.allow_list, self.validator_1.allow_list)
        self.assertEqual(val_1.deny_list, self.validator_1.deny_list)

        val_2 = self.validator_2.parse(self.validator_2.__dict__())
        val_2: StringEndpointValidator

        self.assertEqual(val_2.id, self.validator_2.id)
        self.assertEqual(val_2.name, self.validator_2.name)
        self.assertEqual(val_2.special_id, self.validator_2.special_id)
        self.assertEqual(val_2.length, self.validator_2.length)
        self.assertEqual(val_2.allow_list, self.validator_2.allow_list)
        self.assertEqual(val_2.deny_list, self.validator_2.deny_list)

        val_3 = self.validator_3.parse(self.validator_3.__dict__())
        val_3: StringEndpointValidator

        self.assertEqual(val_3.id, self.validator_3.id)
        self.assertEqual(val_3.name, self.validator_3.name)
        self.assertEqual(val_3.special_id, self.validator_3.special_id)
        self.assertEqual(val_3.length, self.validator_3.length)
        self.assertEqual(val_3.allow_list, self.validator_3.allow_list)
        self.assertEqual(val_3.deny_list, self.validator_3.deny_list)

        val_4 = self.validator_4.parse(self.validator_4.__dict__())
        val_4: StringEndpointValidator

        self.assertEqual(val_4.id, self.validator_4.id)
        self.assertEqual(val_4.name, self.validator_4.name)
        self.assertEqual(val_4.special_id, self.validator_4.special_id)
        self.assertEqual(val_4.length, self.validator_4.length)
        self.assertEqual(val_4.allow_list, self.validator_4.allow_list)
        self.assertEqual(val_4.deny_list, self.validator_4.deny_list)

        val_5 = self.validator_5.parse(self.validator_5.__dict__())
        val_5: StringEndpointValidator

        self.assertEqual(val_5.id, self.validator_5.id)
        self.assertEqual(val_5.name, self.validator_5.name)
        self.assertEqual(val_5.special_id, self.validator_5.special_id)
        self.assertEqual(val_5.length, self.validator_5.length)
        self.assertEqual(val_5.allow_list, self.validator_5.allow_list)
        self.assertEqual(val_5.deny_list, self.validator_5.deny_list)

        self.assertEqual(StringEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "length": "",
                "allowList": None,
                "denyList": None
            }
        }), EndpointParseResponse.CONSTRAINT_LENGTH_MUST_BE_INT)

        self.assertEqual(StringEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "length": 5,
                "allowList": "abc",
                "denyList": "edf"
            }
        }), EndpointParseResponse.CONSTRAINT_BOTH_ALLOW_LIST_AND_DENY_LIST_SPECIFIED)

        self.assertEqual(StringEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "length": 5,
                "allowList": 2,
                "denyList": None
            }
        }), EndpointParseResponse.CONSTRAINT_LIST_MUST_BE_STRING_OR_LIST)

        self.assertEqual(StringEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "length": 5,
                "allowList": None,
                "denyList": 5
            }
        }), EndpointParseResponse.CONSTRAINT_LIST_MUST_BE_STRING_OR_LIST)

        self.assertEqual(StringEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "length": 5,
                "allowList": ["a", 4],
                "denyList": None
            }
        }), EndpointParseResponse.CONSTRAINT_LIST_MUST_ONLY_CONTAIN_STRINGS)

        self.assertEqual(StringEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "length": 5,
                "allowList": None,
                "denyList": ["a", 5]
            }
        }), EndpointParseResponse.CONSTRAINT_LIST_MUST_ONLY_CONTAIN_STRINGS)

    def test__dict__(self):
        data = self.validator_1.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.STRING.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("length", None), 3)
        self.assertEqual(data.get("constraints").get("allowList", None), "abc")
        self.assertIsNone(data.get("constraints").get("denyList", ""))

        data = self.validator_2.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.STRING.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("length", None), 3)
        self.assertIsNone(data.get("constraints").get("allowList", ""))
        self.assertEqual(data.get("constraints").get("denyList", None), "abc")

        data = self.validator_3.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.STRING.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("length", None), 3)
        self.assertEqual(data.get("constraints").get("allowList", None), ["one", "two", "thr"])
        self.assertIsNone(data.get("constraints").get("denyList", ""))

        data = self.validator_4.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.STRING.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("length", None), 3)
        self.assertIsNone(data.get("constraints").get("allowList", ""))
        self.assertEqual(data.get("constraints").get("denyList", None), ["one", "two", "thr"])

        data = self.validator_5.__dict__()

        self.assertEqual(data.get("id", None), "abc")
        self.assertEqual(data.get("name", None), "def")
        self.assertEqual(data.get("type", None), EndpointType.STRING.value)
        self.assertEqual(data.get("specialId", None), "ghi")
        self.assertIsNotNone(data.get("constraints", None))
        self.assertIsNone(data.get("constraints").get("length", ""))
        self.assertIsNone(data.get("constraints").get("allowList", ""))
        self.assertIsNone(data.get("constraints").get("denyList", ""))


class TestEnumEndpointValidator(TestCase):
    validator = EnumEndpointValidator("abc", "def", "ghi", {
        "a": "Apple",
        "b": "Banana",
        "c": "Cucumber"
    })

    def test_validate(self):
        self.assertEqual(self.validator.validate("a"), ValidationResponse.VALID)
        self.assertEqual(self.validator.validate("b"), ValidationResponse.VALID)
        self.assertEqual(self.validator.validate("c"), ValidationResponse.VALID)
        self.assertEqual(self.validator.validate("d"), ValidationResponse.INVALID_ENUM_VALUE)
        self.assertEqual(self.validator.validate("abc"), ValidationResponse.INVALID_ENUM_VALUE)
        self.assertEqual(self.validator.validate(1), ValidationResponse.INVALID_TYPE)

    def test_parse(self):
        val = self.validator.parse(self.validator.__dict__())

        self.assertEqual(val.id, self.validator.id)
        self.assertEqual(val.name, self.validator.name)
        self.assertEqual(val.special_id, self.validator.special_id)
        self.assertEqual(val.values, self.validator.values)

        self.assertEqual(EnumEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": None
        }), EndpointParseResponse.ENUM_TYPE_REQUIRES_VALUES_CONSTRAINT)

        self.assertEqual(EnumEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c"
        }), EndpointParseResponse.ENUM_TYPE_REQUIRES_VALUES_CONSTRAINT)

        self.assertEqual(EnumEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "values": {
                    "a": "Apple",
                    "b": 5,
                    "c": "Cucumber"
                }
            }
        }), EndpointParseResponse.CONSTRAINT_VALUES_VALUES_MUST_BE_STRINGS)

        self.assertEqual(EnumEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "values": {
                    "a": "Apple",
                    "b": "Banana",
                    5: "Cucumber"
                }
            }
        }), EndpointParseResponse.CONSTRAINT_VALUES_KEYS_MUST_BE_STRINGS)

        self.assertEqual(EnumEndpointValidator.parse({
            "id": "a",
            "name": "b",
            "specialId": "c",
            "constraints": {
                "values": 5
            }
        }), EndpointParseResponse.CONSTRAINT_VALUES_MUST_BE_DICT)

    def test__dict__(self):
        data = self.validator.__dict__()

        self.assertEqual(data.get("id", None), self.validator.id)
        self.assertEqual(data.get("name", None), self.validator.name)
        self.assertEqual(data.get("type", None), EndpointType.ENUM.value)
        self.assertEqual(data.get("specialId", None), self.validator.special_id)
        self.assertIsNotNone(data.get("constraints", None))
        self.assertEqual(data.get("constraints").get("values", None), self.validator.values)
