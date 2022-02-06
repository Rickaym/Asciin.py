from typing import Callable, List
from platform import system
from os import getcwd

__all__ = ["Platform"]

SINGLE_PRINT_FLAG: bool = False

class Platform:
    name = system()
    is_window = name == "Windows"
    is_linux = name == "Linux"
    is_darwin = name == "Darwin"

FINISHED_ONCE_TASKS: List[Callable] = []
CWD: str = getcwd()
