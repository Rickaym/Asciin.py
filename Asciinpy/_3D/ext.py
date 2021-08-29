from functools import lru_cache
from math import cos, sin

from ..geometry import Matrix

class MatrixFactory:
    def __getitem__(self, layers):
        return Matrix(*layers)

    def __call__(self, *layers):
        return Matrix(*layers)

PROJE_MATRIX = lru_cache(maxsize=64)(
    lambda a, f, q, near: M(
        [a * f, 0, 0, 0], [0, f, 0, 0], [0, 0, q, 1], [0, 0, -near * q, 0]
    )
)


M = MatrixFactory()

X_ROTO_MATRIX = lru_cache(maxsize=64)(
    lambda l: M([1, 0, 0], [0, cos(l), -sin(l)], [0, sin(l), cos(l)])
)
Y_ROTO_MATRIX = lru_cache(maxsize=64)(
    lambda l: M([cos(l), 0, sin(l)], [0, 1, 0], [-sin(l), 0, cos(l)])
)
Z_ROTO_MATRIX = lru_cache(maxsize=64)(
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
