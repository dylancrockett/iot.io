# lib imports
from .IoTClient import IoTClient
from .types import event_pair


# superclass for device type definitions
class DeviceType:
    def __init__(self, type_name):
        self.type = type_name

    # calls the specific event handler if it exists
    def call_event_handler(self, event: str, message: str, client: IoTClient) -> event_pair:
        """
        Calls the event handler for the given event if it exists, if it doesnt exist then it does nothing.

        Don't overwrite.

        :param event: The event which is being invoked.
        :param message: The message to pass to the event handler.
        :param client: The client which sent the message.
        :return: None or str
        """
        try:
            # call the handler and check for a response
            response = getattr(self, "on_" + event)(message, client)

            print("response: " + response)

            if response is None:
                return None, None
            else:
                return event, response
        except AttributeError:
            return None, None

    def on_connect(self, client: IoTClient):
        pass

    def on_disconnect(self, client: IoTClient):
        pass
