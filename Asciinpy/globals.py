from typing import Callable, List, Literal, Union
from weakref import WeakKeyDictionary
from platform import system
from os import getcwd

SINGLE_PRINT_FLAG: bool = False
PLATFORM: Union[str, Literal["Windows", "Linux", "Darwin"]] = system()
FINISHED_ONCE_TASKS: List[Callable] = []
CWD: str = getcwd()

del Callable, List, Literal, WeakKeyDictionary, system, getcwd, Union
