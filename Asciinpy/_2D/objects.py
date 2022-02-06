import itertools

from functools import lru_cache

from ..utils import get_floor
from .definitors import OccupancySetType, Plane, Mask
from ..geometry import Line
from ..values import Color
from ..screen import Screen
from ..types import AnyInt, IntCoordinate
from ..globals import Platform

from typing import Tuple, List, Union

DEFAULT_BRICK = "#" if Platform.is_window else "\u2588"

class Tile(Plane):
    """
    An plane for rectangle/square like objects.
    """

    def __init__(
        self,
        coordinate: Tuple[int, int],
        length: Union[Tuple[int, int], int],
        texture: str = DEFAULT_BRICK,
        color=None,
    ):
        dimension = (length, length // 2) if isinstance(length, int) else length
        image = (((texture * dimension[0]) + "\n") * (dimension[1])).strip()
        super().__init__(image=image, coordinate=coordinate, color=color)


class Text(Plane):
    """
    A plane for rendering text.
    """

    def __init__(self, coordinate: Tuple[int, int], text: str):
        super().__init__(image=str(text), coordinate=coordinate)
        self.text = str(text)


class Polygon(Mask):
    """
    A mask for n verticies constructed using the :class:`~Asciinpy.geometry.Line`
    objects.
    """

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
        self._coordinate = get_floor(self.occupancy)

    @staticmethod
    @lru_cache(maxsize=64)
    def get_edge_mapping(edges: List[Line]) -> OccupancySetType:
        return set(itertools.chain.from_iterable(e.points for e in edges))

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

    @property
    def edges(self):
        return self.get_edges(self.coordinates) # type: ignore

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

    def blit(self, screen: Screen):
        self.mappings[self.texture] = self.get_edge_mapping(self.edges)
        return super().blit(screen)


class Square(Mask):
    """
    A mask for square/rectangle like objects with complex transformations.
    """

    def __init__(
        self,
        coordinate: IntCoordinate,
        length: int,
        texture: str = DEFAULT_BRICK,
        color=None,
    ):
        dimension = (length, length // 2) if isinstance(length, int) else length
        image = (((texture * dimension[0]) + "\n") * (dimension[1])).strip()
        self.length = length
        super().__init__(image=image, coordinate=coordinate)

    @property
    def right(self):
        return self.x+self.length+1

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y+self.length+1
