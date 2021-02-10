# default
from typing import Union, Dict, List, Tuple
import enum

filter_list = Union[str, List[str]]
enum_list = Dict[str, str]


class ValidationResponse(enum.Enum):
    VALID = "valid"
    INVALID_TYPE = "invalid_data_type"
    LOWER_THAN_MIN = "lower_than_min"
    HIGHER_THAN_MAX = "higher_than_max"
    INVALID_INCREMENT = "invalid_increment"
    INVALID_LENGTH = "invalid_length"
    VIOLATES_ALLOW_LIST = "violates_allow_list"
    VIOLATES_DENY_LIST = "violates_deny_list"
    INVALID_ENUM_VALUE = "invalid_enum_value"
    ENDPOINT_NOT_DEFINED_BY_CLIENT = "endpoint_not_defined_by_client"
    CLIENT_ENDPOINTS_NOT_INITIALIZED = "client_endpoints_not_initialized"
    CLIENT_NOT_CONNECTED = "client_not_connected"


class EndpointParseResponse(enum.Enum):
    VALID = "valid"
    NO_ID_SPECIFIED = "no_id_specified"
    NO_TYPE_SPECIFIED = "no_type_specified"
    NO_NAME_SPECIFIED = "no_name_specified"
    INVALID_TYPE_SPECIFIED = "invalid_type_specified"
    ID_MUST_BE_STRING = "id_must_be_string"
    TYPE_MUST_BE_STRING = "type_must_be_string"
    NAME_MUST_BE_STRING = "name_must_be_string"
    SPECIAL_ID_MUST_BE_STRING = "special_id_must_be_string"
    CONSTRAINT_MIN_MUST_BE_INT = "constraint_min_must_be_integer"
    CONSTRAINT_MAX_MUST_BE_INT = "constraint_max_must_be_integer"
    CONSTRAINT_INCREMENT_MUST_BE_INT = "constraint_increment_must_be_integer"
    CONSTRAINT_LENGTH_MUST_BE_INT = "constraint_length_must_be_integer"
    CONSTRAINT_BOTH_ALLOW_LIST_AND_DENY_LIST_SPECIFIED = "constraint_both_allow_list_and_deny_list_specified"
    CONSTRAINT_LIST_MUST_BE_STRING_OR_LIST = "constraint_list_must_be_string_or_list"
    CONSTRAINT_LIST_MUST_ONLY_CONTAIN_STRINGS = "constraint_list_must_only_contain_strings"
    ENUM_TYPE_REQUIRES_VALUES_CONSTRAINT = "enum_type_requires_values_constraint"
    CONSTRAINT_VALUES_MUST_BE_DICT = "constraint_values_must_be_dict"
    CONSTRAINT_VALUES_KEYS_MUST_BE_STRINGS = "constraint_values_keys_must_be_strings"
    CONSTRAINT_VALUES_VALUES_MUST_BE_STRINGS = "constraint_values_values_must_be_strings"


class EndpointType(enum.Enum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"
    ENUM = "enum"


# abstract validator class
class AbstractEndpointValidator:
    def __init__(self, endpoint_id: str, name: str, special_id: Union[str, None]):
        self.id = endpoint_id
        self.name = name
        self.special_id = special_id
        self.type = None

    def validate(self, data) -> ValidationResponse:
        pass

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "specialId": self.special_id
        }

    @staticmethod
    def parse(endpoint_data: dict) -> Union['AbstractEndpointValidator', EndpointParseResponse]:
        if "id" not in endpoint_data:
            return EndpointParseResponse.NO_ID_SPECIFIED
        elif "name" not in endpoint_data:
            return EndpointParseResponse.NO_NAME_SPECIFIED

        # ensure valid types for id, name, and specialId
        if not isinstance(endpoint_data.get("id", ""), str):
            return EndpointParseResponse.ID_MUST_BE_STRING

        if not isinstance(endpoint_data.get("name", ""), str):
            return EndpointParseResponse.NAME_MUST_BE_STRING

        if not isinstance(endpoint_data.get("specialId", ""), str) and not endpoint_data.get("specialId", None) is None:
            return EndpointParseResponse.SPECIAL_ID_MUST_BE_STRING

        return AbstractEndpointValidator(
            endpoint_data["id"],
            endpoint_data["name"],
            endpoint_data.get("specialId", None)
        )


class BooleanEndpointValidator(AbstractEndpointValidator):
    def __init__(self, endpoint_id: str, name: str, special_id: Union[str, None]):
        super().__init__(endpoint_id, name, special_id)
        self.type = EndpointType.BOOLEAN

    def validate(self, data) -> ValidationResponse:
        # check that data is a boolean value
        if not isinstance(data, bool):
            return ValidationResponse.INVALID_TYPE

        return ValidationResponse.VALID

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "specialId": self.special_id,
            "constraints": None
        }

    @staticmethod
    def parse(endpoint_data: dict) -> Union['BooleanEndpointValidator', EndpointParseResponse]:
        validator = AbstractEndpointValidator.parse(endpoint_data)

        # if the parse failed then return the EndpointParseResponse
        if not isinstance(validator, AbstractEndpointValidator):
            return validator

        # return the validator
        return BooleanEndpointValidator(
            validator.id,
            validator.name,
            validator.special_id
        )


class IntegerEndpointValidator(AbstractEndpointValidator):
    def __init__(self, endpoint_id: str, name: str, special_id: Union[str, None],
                 min_v: Union[None, int] = None, max_v: Union[None, int] = None,
                 increment: Union[None, int] = None):
        super().__init__(endpoint_id, name, special_id)
        self.type = EndpointType.INTEGER
        self.min = min_v
        self.max = max_v
        self.increment = increment

    def validate(self, data) -> ValidationResponse:
        # check if it is a number
        if not isinstance(data, int):
            return ValidationResponse.INVALID_TYPE

        # check if a minimum value was provided
        if self.min is not None:
            # check if it is less than the minimum
            if data < self.min:
                return ValidationResponse.LOWER_THAN_MIN

        # check if a maximum value was provided
        if self.max is not None:
            # check if it is more than the maximum
            if data > self.max:
                return ValidationResponse.HIGHER_THAN_MAX

        return ValidationResponse.VALID

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "specialId": self.special_id,
            "constraints": {
                "min": self.min,
                "max": self.max,
                "increment": self.increment
            }
        }

    @staticmethod
    def parse(endpoint_data: dict) -> Union['IntegerEndpointValidator', EndpointParseResponse]:
        validator = AbstractEndpointValidator.parse(endpoint_data)

        # if the parse failed then return the EndpointParseResponse
        if not isinstance(validator, AbstractEndpointValidator):
            return validator

        # check that constraints were provided
        if endpoint_data.get("constraints", None) is None:
            constraints = {}
        else:
            constraints = endpoint_data.get("constraints", {})

            # check that the min, max, and increment constraints are all integers or None
            if constraints.get("min", None) is not None:
                if not isinstance(constraints.get("min", 0), int):
                    return EndpointParseResponse.CONSTRAINT_MIN_MUST_BE_INT

            if constraints.get("max", None) is not None:
                if not isinstance(constraints.get("max", 0), int):
                    return EndpointParseResponse.CONSTRAINT_MAX_MUST_BE_INT

            if constraints.get("increment", None) is not None:
                if not isinstance(constraints.get("increment", 0), int):
                    return EndpointParseResponse.CONSTRAINT_INCREMENT_MUST_BE_INT

        # return the validator
        return IntegerEndpointValidator(
            endpoint_id=validator.id,
            name=validator.name,
            special_id=validator.special_id,
            min_v=constraints.get("min", None),
            max_v=constraints.get("max", None),
            increment=constraints.get("increment", None)
        )


class StringEndpointValidator(AbstractEndpointValidator):
    def __init__(self, endpoint_id: str, name: str, special_id: Union[str, None],
                 length: Union[None, int] = None, allow_list: Union[None, filter_list] = None,
                 deny_list: Union[None, filter_list] = None):
        super().__init__(endpoint_id, name, special_id)
        self.type = EndpointType.STRING
        self.length = length
        self.allow_list = allow_list
        self.deny_list = deny_list

    def validate(self, data) -> ValidationResponse:
        # check if it is a string
        if not isinstance(data, str):
            return ValidationResponse.INVALID_TYPE

        # check if the length constraint was provided
        if self.length is not None:
            # check if the length is correct
            if len(data) != self.length:
                return ValidationResponse.INVALID_LENGTH

        # check if allow_list is provided
        if self.allow_list is not None:
            if isinstance(self.allow_list, str):
                # for each char in the provided string
                for char in data:
                    # check if it is not in the allow_list
                    if char not in self.allow_list:
                        return ValidationResponse.VIOLATES_ALLOW_LIST
            # if the allow_list is an array of strings
            else:
                # if allow_list is a list of strings check if provided string matches one of those strings
                if data not in self.allow_list:
                    return ValidationResponse.VIOLATES_ALLOW_LIST

        # check if deny_list is provided
        if self.deny_list is not None:
            if isinstance(self.deny_list, str):
                # for each char in the deny list
                for char in self.deny_list:
                    # check if the deny_list contains that char
                    if char in data:
                        return ValidationResponse.VIOLATES_DENY_LIST
            else:
                if data in self.deny_list:
                    return ValidationResponse.VIOLATES_DENY_LIST

        return ValidationResponse.VALID

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "specialId": self.special_id,
            "constraints": {
                "length": self.length,
                "allowList": self.allow_list,
                "denyList": self.deny_list
            }
        }

    @staticmethod
    def parse(endpoint_data: dict) -> Union['StringEndpointValidator', EndpointParseResponse]:
        # define check list func
        def check_list(data: dict, list_name: str) -> EndpointParseResponse:
            if data.get(list_name, "") is None:
                return EndpointParseResponse.VALID

            if isinstance(data.get(list_name, ""), str) or isinstance(data.get(list_name, []), list):
                if isinstance(data.get(list_name, None), list):
                    for item in data.get(list_name, []):
                        if not isinstance(item, str):
                            return EndpointParseResponse.CONSTRAINT_LIST_MUST_ONLY_CONTAIN_STRINGS
            else:
                return EndpointParseResponse.CONSTRAINT_LIST_MUST_BE_STRING_OR_LIST

            return EndpointParseResponse.VALID

        validator = AbstractEndpointValidator.parse(endpoint_data)

        # if the parse failed then return the EndpointParseResponse
        if not isinstance(validator, AbstractEndpointValidator):
            return validator

        # check that constraints were provided
        if endpoint_data.get("constraints", None) is None:
            constraints = {}
        else:
            constraints = endpoint_data.get("constraints", {})

            # check that the length field is an int or none
            if constraints.get("length", None) is not None:
                if not isinstance(constraints.get("length", 0), int):
                    return EndpointParseResponse.CONSTRAINT_LENGTH_MUST_BE_INT

            # ensure that allow_list and deny_list are not provided at the same time
            if constraints.get("allowList", None) is not None and constraints.get("denyList", None) is not None:
                return EndpointParseResponse.CONSTRAINT_BOTH_ALLOW_LIST_AND_DENY_LIST_SPECIFIED

            # check if allow_list and deny_list are formatted correctly
            result = check_list(constraints, "allowList")

            if result is not EndpointParseResponse.VALID:
                return result

            result = check_list(constraints, "denyList")

            if result is not EndpointParseResponse.VALID:
                return result

        # return the validator
        return StringEndpointValidator(
            endpoint_id=validator.id,
            name=validator.name,
            special_id=validator.special_id,
            length=constraints.get("length", None),
            allow_list=constraints.get("allowList", None),
            deny_list=constraints.get("denyList", None)
        )


class EnumEndpointValidator(AbstractEndpointValidator):
    def __init__(self, endpoint_id: str, name: str, special_id: Union[str, None],
                 values: Dict[str, str]):
        super().__init__(endpoint_id, name, special_id)
        self.type = EndpointType.ENUM
        self.values = values

    def validate(self, data) -> ValidationResponse:
        # check if it is a string
        if not isinstance(data, str):
            return ValidationResponse.INVALID_TYPE

        # check if the value is a valid enum for this endpoint
        if data not in self.values.keys():
            return ValidationResponse.INVALID_ENUM_VALUE

        return ValidationResponse.VALID

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "specialId": self.special_id,
            "constraints": {
                "values": self.values
            }
        }

    @staticmethod
    def parse(endpoint_data: dict) -> Union['EnumEndpointValidator', EndpointParseResponse]:
        validator = AbstractEndpointValidator.parse(endpoint_data)

        # if the parse failed then return the EndpointParseResponse
        if not isinstance(validator, AbstractEndpointValidator):
            return validator

        # check that constraints were provided
        if endpoint_data.get("constraints", None) is None:
            return EndpointParseResponse.ENUM_TYPE_REQUIRES_VALUES_CONSTRAINT
        else:
            constraints = endpoint_data.get("constraints")
            constraints: dict

            # ensure the "values" value exists
            if constraints.get("values", None) is None:
                return EndpointParseResponse.ENUM_TYPE_REQUIRES_VALUES_CONSTRAINT
            else:
                # ensure it is a dictionary
                if not isinstance(constraints.get("values"), dict):
                    return EndpointParseResponse.CONSTRAINT_VALUES_MUST_BE_DICT

            # ensure that both the key and value for each entry in the "values" key are strings
            for key, val in constraints.get("values").items():
                if not isinstance(key, str):
                    return EndpointParseResponse.CONSTRAINT_VALUES_KEYS_MUST_BE_STRINGS
                elif not isinstance(val, str):
                    return EndpointParseResponse.CONSTRAINT_VALUES_VALUES_MUST_BE_STRINGS

        # return the validator
        return EnumEndpointValidator(
            endpoint_id=validator.id,
            name=validator.name,
            special_id=validator.special_id,
            values=constraints.get("values")
        )


class EndpointManager:
    def __init__(self):
        self.__endpoints = {}
        self.__initialized = False

    @property
    def initialized(self):
        return self.__initialized

    def __add_endpoint(self, validator: AbstractEndpointValidator):
        self.__endpoints[validator.id] = validator

    def get_validator(self, endpoint_id: str) -> Union[AbstractEndpointValidator, ValidationResponse]:
        self.__endpoints: Dict[str, AbstractEndpointValidator]

        try:
            return self.__endpoints[endpoint_id]
        except KeyError:
            return ValidationResponse.ENDPOINT_NOT_DEFINED_BY_CLIENT

    def parse(self, endpoints: List[dict]) -> Tuple[str, EndpointParseResponse]:
        for endpoint in endpoints:
            # parse the endpoint
            if endpoint.get("type", None) is None:
                return endpoint.get("id", "no_id_provided"), EndpointParseResponse.NO_TYPE_SPECIFIED

            # get validator based on type
            if endpoint["type"] == EndpointType.BOOLEAN.value:
                validator = BooleanEndpointValidator.parse(endpoint)
            elif endpoint["type"] == EndpointType.INTEGER.value:
                validator = IntegerEndpointValidator.parse(endpoint)
            elif endpoint["type"] == EndpointType.STRING.value:
                validator = StringEndpointValidator.parse(endpoint)
            elif endpoint["type"] == EndpointType.ENUM.value:
                validator = EnumEndpointValidator.parse(endpoint)
            else:
                # if an invalid type was specified
                return endpoint.get("id", "no_id_provided"), EndpointParseResponse.INVALID_TYPE_SPECIFIED

            # if the parse failed then return the EndpointParseResponse
            if not isinstance(validator, AbstractEndpointValidator):
                return endpoint.get("id", "no_id_provided"), validator

            # if parse was successful then add the validator to the manager
            self.__add_endpoint(validator)

        # set initialized flag
        self.__initialized = True

        return "", EndpointParseResponse.VALID
