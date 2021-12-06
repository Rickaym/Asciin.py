from abc import abstractmethod
from abc import ABCMeta
from typing import Callable, List, Tuple
from .values import Resolutions

Pixel = Tuple[int, int, str, str]

class Blitable(metaclass=ABCMeta):
    r"""
    Any object except pixels that can be shown on the screen.
    """

    @abstractmethod
    def blit(self, resolution: Resolutions, draw: Callable[[int, int, str], None]) -> List[Pixel]:
        r"""
        Internal blitting method the blitable.
        """



