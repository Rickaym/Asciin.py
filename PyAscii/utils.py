from platform import version
from threading import Thread
from time import time, sleep

try:
    from typing import Callable, Any, List, Union
except ImportError:
    pass


class HashablePoint:
    pass


def beautify(frame, screen):
    # type: (Union[str, List[str]], Any) -> str
    """
    Maps an uncut frame into different pieces with newline characters to make it
    readable without perfect resolution.
    """
    new_frame = list(frame)
    for i, char in enumerate(frame):
        if (i + 1) % screen.resolution.width == 0:
            new_frame[i] = char + "\n"
    return "".join(new_frame)
