class Matrix:
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


class MatrixFactory:
    def __getitem__(self, layers):
        return Matrix(*layers)

    def __call__(self, *layers):
        return Matrix(*layers)


M = MatrixFactory()
