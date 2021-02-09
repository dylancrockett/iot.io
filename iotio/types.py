from typing import Union, Tuple

# define the sendable type (Union of types which can be sent to clients)
sendable = Union[bytes, bytearray, bool, int, str, list, dict]

# define the event_pair type
event_pair = Union[Tuple[None, None], Tuple[str, sendable]]
