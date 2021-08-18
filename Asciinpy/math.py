from __future__ import division

from itertools import chain
from .utils import caches
from math import cos, sin

GRADIENT = caches(
    lambda P1, P2: None if P2[0] - P1[0] == 0 else (P2[1] - P1[1]) / (P2[0] - P1[0])
)

PROJE_MATRIX = caches(
    lambda a, f, q, near: M(
        [a * f, 0, 0, 0], [0, f, 0, 0], [0, 0, q, 1], [0, 0, -near * q, 0]
    )
)


class Matrix:
    """
    A matrix class that supports up to 10x10 matrixes.

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
                self.layers[i] = roundi(l)
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

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self._gradient = GRADIENT(
            p1, p2
        ), (p1, p2)
        self._equation = (
            self._get_equation()
        ), (p1, p2)
        self._inverse_equation = (
            self._get_inverse_equation()
        ), (p1, p2)
        self._points = None

    def __getitem__(self, x):
        return self.equation(x)

    @property
    def gradient(self):
        """
        Gradient of the line

        :type class:`float`:
        """
        if (self.p1, self.p2) != self._gradient[1]:
            self._gradient = GRADIENT(self.p1, self.p2), (self.p1[:], self.p2[:])
        return self._gradient[0]

    @property
    def equation(self):
        """
        f(x) of the line that takes in x to return the (x,y) at that point

        :type Callable[[:class:`int`], Tuple[:class:`int`, :class:`int`]]:
        """
        if (self.p1, self.p2) != self._equation[1]:
            self._equation = self._get_equation(), (self.p1[:], self.p2[:])
        return self._equation[0]

    @property
    def inverse_equation(self):
        """
        inverse f(x) of the line that takes in y to return the (x,y) at that point

        :type Callable[[:class:`int`], Tuple[:class:`int`, :class:`int`]]:
        """
        if (self.p1, self.p2) != self._inverse_equation[1]:
            self._inverse_equation = self._get_inverse_equation(), (self.p1[:], self.p2[:])
        return self._inverse_equation[0]

    @property
    def points(self):
        """
        The points that join p1 to p2.

        :type: List[Tuple[:class:`int`, :class:`int`]]
        """
        if self._points is None or self._points[1] != [self.p1, self.p2]:
            self._points = self._get_points(), [self.p1[:], self.p2[:]]
        return self._points[0]

    def _get_points(self):
        maps_inverse = []
        if self.gradient is not None:
            maps_inverse = map(
                self.equation,
                range(
                    *(
                        (self.p1[0], self.p2[0] + 1)
                        if self.p1[0] - self.p2[0] < 0
                        else (self.p2[0], self.p1[0] + 1)
                    )
                ),
            )
        return chain(
            maps_inverse,
            (
                map(
                    self.inverse_equation,
                    range(
                        *(
                            (self.p1[1], self.p2[1] + 1)
                            if self.p1[1] - self.p2[1] < 0
                            else (self.p2[1], self.p1[1] + 1)
                        )
                    ),
                )
            ),
        )

    def _get_equation(self):
        if self.p1[1] - self.p2[1] == 0:
            return lambda x: (x, self.p1[1])
        elif self.gradient is None or self.gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda x: (
                x,
                (self.gradient * x) - (self.gradient * self.p1[0]) + self.p1[1],
            )

    def _get_inverse_equation(self):
        if self.gradient is None or self.gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda y: (((y - self.p1[1]) / self.gradient) + self.p1[0], y)


class MatrixFactory:
    def __getitem__(self, layers):
        return Matrix(*layers)

    def __call__(self, *layers):
        return Matrix(*layers)


M = MatrixFactory()

X_ROTO_MATRIX = caches(
    lambda l: M([1, 0, 0], [0, cos(l), -sin(l)], [0, sin(l), cos(l)])
)
Y_ROTO_MATRIX = caches(
    lambda l: M([cos(l), 0, sin(l)], [0, 1, 0], [-sin(l), 0, cos(l)])
)
Z_ROTO_MATRIX = caches(
    lambda l: M([cos(l), -sin(l), 0], [sin(l), cos(l), 0], [0, 0, 1])
)
"""
Input: [ x ]
       | y |
       [ z ]

RoX: [1  0     0    ] RoY = [cos0  0  sin0] RoZ = [cos0  -sin0  0]
     |0  cos0  -sin0|       |0     1  0   |       |sin0  cos0   0|
     [0  sin0  cos0 ]       [-sin0 0  cos0]       [0     0      1]
"""


def project_3D(m, aspect_ratio, fov):
    # type: (Matrix, int, int) -> Matrix
    fnear = 0.1
    ffar = 10000

    q = ffar / (ffar - fnear)
    m = [m[0], m[1], m[2], 1]
    resultant = Matrix.fast_4x4_mul(m, PROJE_MATRIX(aspect_ratio, fov, q, fnear))

    if resultant.k != 0:
        resultant.x /= resultant.k
        resultant.y /= resultant.k
        resultant.z /= resultant.k

    return resultant


def rotate_3D(m, angle, axis):
    roto_mat = (
        X_ROTO_MATRIX
        if axis.lower() == "x"
        else Z_ROTO_MATRIX
        if axis.lower() == "z"
        else Y_ROTO_MATRIX
    )
    resultant = Matrix.fast_3x3_mul(m, roto_mat(angle))

    return resultant.layers


def roundi(num, ndigits=0):
    return int(round(num, ndigits))
    coeff = 10 ** ndigits
    try:
        norm = num / num * (0.5 / coeff)
    except ZeroDivisionError:
        norm = 0.5 / coeff
    return int(((num + norm) * coeff) / coeff)
