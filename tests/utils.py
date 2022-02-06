import operator

from random import choice, randint
from typing import Any, Callable, Collection, Optional
from Asciinpy._2D.definitors import Mask


def move_somewhere(obj: Mask):
    traverses = randint(-500, 500)
    x, y = randint(0, 1), randint(0, 1)
    if not y and not x:
        x = 1
    moved = x * traverses, y * traverses
    obj.x += moved[0]
    obj.y += moved[1]
    return moved


def transform_somewhere(obj: Mask) -> Callable:
    r"""
    Transforms an object with a random operation and returns the
    operation used.
    """
    op = choice((operator.pow, operator.sub, operator.add, operator.mul))
    coeff = randint(-500, 500)
    if op == operator.pow:
        coeff = randint(0, 10)
    operation = lambda tk: [op(tk[0], coeff), op(tk[1], coeff)]
    obj.transform(operation)
    return operation


def change_summation(before: Collection[Any], distance:  tuple[int, int]) -> list[Any]:
    r"""
    A type of change calculated by the difference in summation of an object's
    occupancy after it has gone through a given change.
    """
    sz = len(before)
    return list((distance[0] * sz, distance[1] * sz))


def change_each(
    before: list[Any], equation: Callable, distance: Optional[tuple[int, int]] = None
) -> list[Any]:
    r"""
    A type of change calculated by the difference in each and every point that
    an object occupies after it has gone through a given change.
    """
    if distance is None:
        return list(map(lambda coord: equation(coord), before))
    else:
        # positional change
        return list(map(lambda coord: equation(coord, distance), before))
