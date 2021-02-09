# iot error base
class IoTError(Exception):
    """
    Base Exception for all iot.io errors
    """
    def __init__(self, message: str = "Base exception class for the iot.io library."):
        super().__init__(message)


# error when a client has its connection ended
class ConnectionEnded(IoTError):
    """
    Exception thrown when an operation attempts to use a socket but the connection is no longer alive.
    """
    def __init__(self, message: str = "Client socket no longer alive."):
        super().__init__(message)


# generic connection failed error for when client does something wrong while first connecting
class ConnectionFailed(IoTError):
    """
    Exception thrown when a client does something wrong while connecting, this is usually caused by missing or
    invalid HTTP Headers. Should not normally be seen unless you are modifying the IoTManager or IoTManagerMiddleware
    classes directly.
    """
    def __init__(self, message: str = "Client failed to connect to the server."):
        super().__init__(message)


# error when client does not provide an Id when connecting
class ClientNoId(ConnectionFailed):
    """
    Exception thrown when a connecting client does not provide an ID.
    """
    def __init__(self, message: str = "Client failed to provide the IoT-IO-Id header field."):
        super().__init__(message)


# error when client does not provide a Type when connecting
class ClientNoType(ConnectionFailed):
    """
    Exception thrown when a connecting client does not provide a Type.
    """
    def __init__(self, message: str = "Client failed to provide the IoT-IO-Type header field."):
        super().__init__(message)


# error when client provides an invalid Type when connecting
class ClientInvalidType(ConnectionFailed):
    """
    Exception thrown when a connecting client does not provide a Type which the server can handle.
    """
    def __init__(self, message: str = "Client provided an invalid value for the IoT-IO-Type header field."):
        super().__init__(message)


# error when client provides invalid json in the IoT-IO-Data field
class ClientInvalidData(ConnectionFailed):
    """
    Exception thrown when a connecting client does not provide Data which the server can deserialize.
    """
    def __init__(self, message: str = "Client provided an invalid json data for the IoT-IO-Data header field."):
        super().__init__(message)


# error when client provides invalid data in the IoT-IO-Endpoints field
class ClientInvalidEndpoints(ConnectionFailed):
    """
    Exception thrown when a connecting client does not provide Endpoints which the server can understand.
    """
    def __init__(self, message: str = "Client provided an invalid value for the IoT-IO-Endpoints header field."):
        super().__init__(message)


# error when client does not provide a protocol version
class ClientNoProtocolVersion(ConnectionFailed):
    """
    Exception thrown when a connecting client does not provide it's protocol version.
    """

    def __init__(self, message: str = "Client did not provide the IoT-IO-ProtocolVersion header field."):
        super().__init__(message)


# error when client provides invalid data in the IoT-IO-Endpoints field
class ClientIncompatibleProtocolVersion(ConnectionFailed):
    """
    Exception thrown when a connecting client's protocol version is incompatible with that of the server's.
    """

    def __init__(self, message: str = "The version of the client's protocol is incompatible with that of the server."):
        super().__init__(message)
