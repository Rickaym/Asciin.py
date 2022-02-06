from abc import abstractmethod
from abc import ABCMeta
from typing import List, Tuple

Pixel = Tuple[int, int, str, str]

class Blitable(metaclass=ABCMeta):
    """
    Any object except pixels that can be shown on the screen.
    """

    @abstractmethod
    def blit(self, screen) -> List[Pixel]:
        """
        Internal blitting method the blitable.
        """
