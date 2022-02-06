from itertools import chain
from functools import lru_cache
from math import cos, sin
from typing import Tuple

from Asciinpy.types import AnyInt, AnyIntCoordinate

__all__ = ["Line", "rotate"]

GRADIENT = lru_cache(maxsize=64)(
    lambda P1, P2: None if P2[0] -
    P1[0] == 0 else (P2[1] - P1[1]) / (P2[0] - P1[0])
)


class Line:
    """
    A conceptual line class with simple properties. Basic properties are calculated and recalculated if and when they are needed.

    :param p1:
        Starting point
    :type p1: List[:class:`int`, :class:`int`]
    :param p2:
        Endpoint
    :type p2: List[:class:`int`, :class:`int`]
    """

    def __init__(self, p1: Tuple[int, int], p2: Tuple[int, int]):
        self.p1 = p1
        self.p2 = p2

    @property
    def points(self):
        """
        The points that join p1 to p2.

        :type: List[Tuple[:class:`int`, :class:`int`]]
        """
        return self.get_points(self.p1, self.p2)

    @property
    def midpoint(self):
        return ((self.p1[0]+self.p2[0])/2, (self.p1[1]+self.p2[1])/2)

    @staticmethod
    def get_points(p1, p2):
        p1, p2 = (round(p1[0]), round(p1[1])), (round(p2[0]), round(p2[1]))
        gradient = GRADIENT(p1, p2)
        if gradient is not None:
            maps_inverse = map(
                Line.get_equation(gradient, p1, p2),
                range(
                    *(
                        (p1[0], p2[0] + 1)
                        if p1[0] - p2[0] < 0
                        else (p2[0], p1[0] + 1)
                    )
                ),
            )
        else:
            maps_inverse = []

        maps = map(
            Line.get_inverse_equation(gradient, p1),
            range(
                *(
                    (p1[1], p2[1] + 1)
                    if p1[1] - p2[1] < 0
                    else (p2[1], p1[1] + 1)
                )
            ),
        )

        return set(chain(maps_inverse, maps))

    @staticmethod
    def get_equation(gradient, p1, p2):
        if p1[1] - p2[1] == 0:
            return lambda x: (x, p1[1])
        elif gradient is None or gradient == 0:
            return lambda y: (p1[0], y)
        else:
            return lambda x: (
                x,
                (gradient * x) - (gradient * p1[0]) + p1[1],
            )

    @staticmethod
    def get_inverse_equation(gradient, p1):
        if gradient is None or gradient == 0:
            return lambda y: (p1[0], y)
        else:
            return lambda y: (((y - p1[1]) / gradient) + p1[0], y)

    def __repr__(self) -> str:
        return f"<Line x={self.p1} y={self.p2}>"


def rotate(coordinate: AnyIntCoordinate, theta: AnyInt, midpoint: AnyIntCoordinate):
    """
    The rotation of a coordinate at a point in radians.

    Rotation of axes - 0 (theta): (x, y) -> (X, Y)
    X = x cos(0) + y sin(0)
    Y = -x sin(0) + y cos(0)
    """
    r_x, r_y = (cos(theta), sin(theta)), (-sin(theta), cos(theta))
    x, y = coordinate[0]-midpoint[0], coordinate[1]-midpoint[1]
    return (x*r_x[0] + y*r_x[1])+midpoint[0], (x*r_y[0] + y*r_y[1])+midpoint[1]
