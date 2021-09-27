from itertools import chain
from functools import lru_cache
from math import cos, sin
from typing import Tuple, Union

GRADIENT = lru_cache(maxsize=64)(
    lambda P1, P2: None if P2[0] -
    P1[0] == 0 else (P2[1] - P1[1]) / (P2[0] - P1[0])
)


class Matrix:
    r"""
    A matrix class that supports up to 5x5 matrixes.

    Supports scalar multiplication, pretty printing, equality checks,
    matrix multiplication and alias references such as x for element 0 and
    y for element 1.

    :param layers:
        The layers of the Matrix, a matrix can contain other matrixes.
    :type layers: Union[Tuple[:class:`int`], :class:`Matrix`]
    """

    NAME_SPACE = ("x", "y", "z", "k", "w")
    NAME_MAP = dict(zip(NAME_SPACE, range(len(NAME_SPACE))))

    def __init__(self, *layers):
        self.layers = [
            layer if not isinstance(layer, (tuple, list)) else Matrix(*layer)
            for layer in layers
        ]
        self.__dict__.update(dict(zip(self.NAME_SPACE, self.layers)))

    def __eq__(self, o):
        return all(
            self.__dict__.get(attr) == o.__dict__.get(attr) for attr in self.NAME_SPACE
        )

    def __ne__(self, o):
        return not self.__eq__(o)

    def __repr__(self):
        return (
            "["
            + " ".join(
                (
                    str(val)
                    if not isinstance(val, Matrix)
                    else ("\n " if i != 0 else "") + val.__repr__()
                )
                for i, val in enumerate(self.layers)
            )
            + "]"
        )

    def __len__(self):
        return len(self.dimension)

    def __mul__(self, other):
        # type: (Union[Matrix, int]) -> Matrix
        """
        The number of columns of the 1st matrix must equal the number of rows of the 2nd matrix in multiplicatioon.
        And the result will have the same number of rows as the 1st matrix, and the same number of columns as the 2nd matrix.
        Matrix Multiplication,
            Scalar multiplication just multiplies every component of a matrix with the multiplier

            In a matrix to matrix multiplication, consider their sizes,
                in format :: row x column

            Matrix A: MA = 1x2 [[1 1]   Matrix B: MB = 2x1 [[0 0]
                                [1 1]]                      [1 1]]

            Col of MA == Row of MB or is incompatible
            that means MA(1x2) MB(2x1)
                          \ \_EA__/ /
                           \____EB_/

            expression A: EA = column(MA) == row(MB) represents the comparison expression needed to be true for compatibility
            expression B: EB =  row(MA), column(MB)  represents the dimension of the resultant matrix
        """
        if isinstance(other, Matrix):
            # self columns must equal other rows
            if len(self.dimension) != len(other.dimension["x"]):
                raise TypeError("uncompatible to multiple these matrixes")
            else:
                self_vals = list(self.layers)
                other_vals = list(other.layers)

                pass
        else:
            # scalar multiplication
            return M(*[val * other for val in list(self.dimension.values())])

    def __getitem__(self, item):
        try:
            return self.layers[item]
        except TypeError:
            return self.layers[self.NAME_MAP[item]]

    def rounds(self):
        for i, l in enumerate(self.layers):
            if isinstance(l, Matrix):
                self.layers[i] = l.rounds()
            else:
                self.layers[i] = round(l)
        return self.layers

    @staticmethod
    def fast_4x4_mul(coord, other):
        coord = [coord[0], coord[1], coord[2], 1]
        res = [0, 0, 0, 0]

        for i in range(len(coord)):
            res[i] = (
                coord[0] * other[0][i]
                + coord[1] * other[1][i]
                + coord[2] * other[2][i]
                + coord[3] * other[3][i]
            )

        return M(res[0], res[1], res[2], res[3])

    @staticmethod
    def fast_3x3_mul(coord, other):
        coord = [coord[0], coord[1], coord[2]]
        res = [0, 0, 0]

        for i in range(len(coord)):
            res[i] = (
                coord[0] * other[0][i] + coord[1] *
                other[1][i] + coord[2] * other[2][i]
            )

        return M(res[0], res[1], res[2])


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
        r"""
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
        return f"< --- Line: {self.p1}, {self.p2}>"


def X_ROTO(theta): return Matrix(cos(theta), -sin(theta))
def Y_ROTO(theta): return Matrix(sin(theta), cos(theta))


def rotate(coordinate, theta, cor):
    r_x, r_y = X_ROTO(theta), Y_ROTO(theta)
    x, y = coordinate[0]-cor[0], coordinate[1]-cor[1]
    return (x*r_x[0] + y*r_x[1])+cor[0], (x*r_y[0] + y*r_y[1])+cor[1]


del lru_cache
