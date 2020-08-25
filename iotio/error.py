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
