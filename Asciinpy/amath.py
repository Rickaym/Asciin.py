from __future__ import division

GRADIENT = (
    lambda P1, P2: None if P2[0] - P1[0] == 0 else (P2[1] - P1[1]) / (P2[0] - P1[0])
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

    NAME_SPACE = ("x", "y", "z", "k", "a", "e", "i", "o", "u")

    def __init__(self, *layers):
        self.dimension = dict(
            zip(
                self.NAME_SPACE,
                (
                    layer if not isinstance(layer, (tuple, list)) else Matrix(*layer)
                    for layer in layers
                ),
            )
        )
        self.__dict__.update(self.dimension)

    def __eq__(self, o):
        to_cmpr = []
        to_cmpr.extend(list(self.dimension.keys()))
        to_cmpr.extend(list(o.dimension.keys()))
        to_cmpr = set(to_cmpr)
        return all(self.__dict__.get(attr) == o.__dict__.get(attr) for attr in to_cmpr)

    def __ne__(self, o):
        return not self.__eq__(o)

    def __repr__(self):
        return (
            "["
            + " ".join(
                (
                    val
                    if not isinstance(val, Matrix)
                    else ("\n " if i != 0 else "") + val.__repr__()
                )
                for i, val in enumerate(self.dimension.values())
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
                self_vals = list(self.dimension.values())
                other_vals = list(other.dimension.values())

                pass
        else:
            # scalar multiplication
            return M(*[val * other for val in list(self.dimension.values())])


class Line:
    """
    A conceptual line class with simple properties.

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

        self.gradient = GRADIENT(
            p1, p2
        )  #: Union[:class:`int`, :class:`int`]: The gradient of the line
        self.equation = (
            self._get_equation()
        )  #: Callable[[:class:`int`], Tuple[:class:`int`, :class:`int`]]: f(x) of the line that takes in x to return the (x,y) at that point
        self.inverse_equation = (
            self._get_inverse_equation()
        )  #: Callable[[:class:`int`], Tuple[:class:`int`, :class:`int`]]: inverse f(x) of the line that takes in y to return the (x,y) at that point
        self._points = None

    def __getitem__(self, x):
        return self.equation(x)

    @property
    def points(self):
        """
        The points that join p1 to p2.

        :type: :class:`int`
        """
        if self._points is None or self._points[1] != [self.p1, self.p2]:
            self._points = self._get_points(), [self.p1[:], self.p2[:]]
        return self._points[0]

    def _get_points(self):
        points_set = []
        if self.gradient is not None:
            points_set.extend(
                [
                    self.equation(x)
                    for x in range(
                        *(
                            (self.p1[0], self.p2[0] + 1)
                            if self.p1[0] - self.p2[0] < 0
                            else (self.p2[0], self.p1[0] + 1)
                        )
                    )
                ]
            )

        points_set.extend(
            [
                self.inverse_equation(y)
                for y in range(
                    *(
                        (self.p1[1], self.p2[1] + 1)
                        if self.p1[1] - self.p2[1] < 0
                        else (self.p2[1], self.p1[1] + 1)
                    )
                )
            ]
        )

        return set(points_set)

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
