"""
A collection of special types that are shared throughout
the library - those private are locally defined.
"""

from typing import List, TypeVar, Union, Tuple

AnyInt = Union[int, float]
T = TypeVar("T")
Coordinate = Union[List[T], Tuple[T, T]]
IntCoordinate = Coordinate[int]
AnyIntCoordinate = Coordinate[AnyInt]
