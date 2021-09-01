from typing import Callable, List, Literal
from weakref import WeakKeyDictionary
from platform import system
from os import getcwd

SINGLE_PRINT_FLAG: bool = False
PLATFORM: Literal["Windows", "Linux", "Darwin"] = system()
ASSET_CACHE: WeakKeyDictionary = WeakKeyDictionary()
FINISHED_ONCE_TASKS: List[Callable] = []
CWD: str = getcwd()

del Callable, List, Literal
del WeakKeyDictionary
del system
del getcwd