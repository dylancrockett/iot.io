import enum


# enumerator for errors between client and server
class Errors(enum.Enum):
    CLIENT_NO_ID = "client_no_id"
    CLIENT_NO_TYPE = "client_no_type"
    CLIENT_INVALID_TYPE = "client_invalid_type"
    CLIENT_INVALID_DATA = "client_invalid_data"
    CLIENT_INVALID_ENDPOINTS = "client_invalid_endpoints"
    CLIENT_NO_PROTOCOL_VERSION = "client_no_protocol_version"
    CLIENT_INCOMPATIBLE_PROTOCOL_VERSION = "client_incompatible_protocol_version"
    CLIENT_INVALID_PACKET = "client_invalid_packet"
