from functools import lru_cache
import itertools

from .definitors import OccupancySetType, Plane, Mask

from ..geometry import Line
from ..utils import Color
from ..screen import Screen
from ..globals import PLATFORM

from typing import Tuple, List, Union

DEFAULT_BRICK = "\u2588" if PLATFORM != "Windows" else "#"

#
# Types
#

AnyInt = Union[int, float]

# ---


class Tile(Plane):
    def __init__(
        self,
        coordinate: Tuple[int, int],
        length: Union[Tuple[int, int], int],
        texture: str = DEFAULT_BRICK,
        color=None,
    ):
        dimension = (length, length // 2) if isinstance(length, int) else length
        image = (((texture * dimension[0]) + "\n") * (dimension[1])).strip()
        super().__init__(image, coordinate, color)


class Text(Plane):
    def __init__(self, coordinate: Tuple[int, int], text: str):
        super().__init__(image=str(text), coordinate=coordinate)
        self.text = str(text)


class Polygon(Mask):
    def __init__(
        self,
        coordinates: List[Tuple[int, int]],
        texture: str = None,
        color: Color = None,
    ):
        self.coordinates = coordinates
        self.texture = texture or DEFAULT_BRICK
        self.color = color

        self.mappings = {self.texture: self.get_edge_mapping(self.edges)}
        self._coordinate = self.get_min_point(self.occupancy)

    @staticmethod
    @lru_cache(maxsize=64)
    def get_edge_mapping(edges: List[Line]) -> OccupancySetType:
        return set(itertools.chain.from_iterable(e.points for e in edges))

    @property
    def edges(self):
        return self.get_edges(self.coordinates)

    @property
    def x(self) -> AnyInt:
        return self._coordinate[0]

    @x.setter
    def x(self, value: AnyInt):
        translates = value - self._coordinate[0]
        self._coordinate = (value, self._coordinate[1])
        self.coordinates = list(
            map(lambda coord: (coord[0] + translates, coord[1]), self.coordinates)
        )

    @property
    def y(self) -> AnyInt:
        return self._coordinate[1]

    @y.setter
    def y(self, value: AnyInt):
        translates = value - self._coordinate[1]
        self._coordinate = (self._coordinate[0], value)
        self.coordinates = list(
            map(lambda coord: (coord[0], coord[1] + translates), self.coordinates)
        )

    @staticmethod
    @lru_cache(maxsize=64)
    def get_edges(coordinates: List[Tuple[int, int]]) -> Tuple[Line]:
        ends = len(coordinates) - 1
        edges = [
            Line(coordinates[i], coordinates[i + 1])
            for i in range(len(coordinates))
            if i != ends
        ]
        edges.append(Line(coordinates[0], coordinates[-1]))
        return tuple(edges)

    def blit(self, screen: Screen):
        self.mappings[self.texture] = self.get_edge_mapping(self.edges)
        return super().blit(screen)


class Square(Mask):
    def __init__(
        self,
        coordinate: Tuple[int, int],
        length: Union[Tuple[int, int], int],
        texture: str = DEFAULT_BRICK,
        color=None,
    ):
        dimension = (length, length // 2) if isinstance(length, int) else length
        image = (((texture * dimension[0]) + "\n") * (dimension[1])).strip()
        super().__init__(coordinate, image)
        self.length = length
