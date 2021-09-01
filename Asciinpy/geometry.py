from itertools import chain
from functools import lru_cache

from .utils import AssetCached, asset


GRADIENT = lru_cache(maxsize=64)(
    lambda P1, P2: None if P2[0] - P1[0] == 0 else (P2[1] - P1[1]) / (P2[0] - P1[0])
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
                coord[0] * other[0][i] + coord[1] * other[1][i] + coord[2] * other[2][i]
            )

        return M(res[0], res[1], res[2])


class Line(AssetCached):
    """
    A conceptual line class with simple properties. Basic properties are calculated and recalculated if and when they are needed.

    :param p1:
        Starting point
    :type p1: List[:class:`int`, :class:`int`]
    :param p2:
        Endpoint
    :type p2: List[:class:`int`, :class:`int`]
    """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __getitem__(self, x):
        return self.equation(x)

    @property
    def points(self):
        r"""
        The points that join p1 to p2.

        :type: List[Tuple[:class:`int`, :class:`int`]]
        """
        return self._get_points()

    @asset(lambda: ("self.p1", "self.p2"))
    def _get_points(self):
        gradient = GRADIENT(tuple(self.p1), tuple(self.p2))
        if gradient is not None:
            maps_inverse = map(
                self._get_equation(gradient),
                range(
                    *(
                        (self.p1[0], self.p2[0] + 1)
                        if self.p1[0] - self.p2[0] < 0
                        else (self.p2[0], self.p1[0] + 1)
                    )
                ),
            )
        else:
            maps_inverse = []

        maps = map(
                    self._get_inverse_equation(gradient),
                    range(
                        *(
                            (self.p1[1], self.p2[1] + 1)
                            if self.p1[1] - self.p2[1] < 0
                            else (self.p2[1], self.p1[1] + 1)
                        )
                    ),
                )

        return set(chain(maps_inverse, maps))


    def _get_equation(self, gradient):
        if self.p1[1] - self.p2[1] == 0:
            return lambda x: (x, self.p1[1])
        elif gradient is None or gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda x: (
                x,
                (gradient * x) - (gradient * self.p1[0]) + self.p1[1],
            )

    def _get_inverse_equation(self, gradient):
        if gradient is None or gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda y: (((y - self.p1[1]) / gradient) + self.p1[0], y)

