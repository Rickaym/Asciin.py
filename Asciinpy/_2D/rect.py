from typing import Tuple, Union

from ..utils import Color

AnyInt = Union[int, float]

class Rectable:
    r"""
    A simple parent class for all models that can be translated into a rect.
    """

    def get_rect(self, coordinate: Tuple[int, int]=None, dimension: Tuple[int, int]=[0, 0]) -> "Rect":
        r"""
        Builds a rect object from scratch. If neither coordinate or dimension
        is given, the coordinate is assumed to be the origin and the dimension is fetched
        from the parent Object.

        This only creates a new rectangle object if none is present.
        If present returns what it already has.

        :param coordinate:
            The top-left coordinate for the rect.
        :type coordinate: Tuple[:class:`int`, :class:`int`]
        :param dimension:
            The dimension of the rect.
        :type coordinate: Tuple[:class:`int`, :class:`int`]

        :return: (:class:`Rect`) The rectangle made or acquired.
        """
        if self.__dict__.get("rect") is None:
            coordinate = coordinate or (0, 0)
            dimension = dimension or self.dimension
            self.rect = Rect(coordinate, dimension, self)
        return self.rect


class Rect:
    """
    An abstract quadrilateral boundary for Rectable objects.

    Provides temporal positions of the given model's boundary.

    This can be an erroneous measurement of collisions when sections of the model
    exceeds the given boundary or an object is moving extremely fast.
    """

    def __init__(self, coordinate: Tuple[AnyInt, AnyInt], dimension: Tuple[int, int], parent):
        self._x = coordinate[0]  #: :class:`int`: Top left x position
        self._y = coordinate[1]  #: :class:`int`: Top left y position
        self.width = dimension[
            0
        ]  #: :class:`int`: The width of the rect. This is the horizontal difference.
        self.height = dimension[
            1
        ]  #: :class:`int`: The height of the rect (or length) this is the vertical difference.
        self.parent = (
            parent
        ) #: :class:`Model`: A Parent object that the rect is assigned under.
        self.texture = ""  #: :class:`str`: The outline texture of the rect. None by default.
        self.color = Color.FORE(255, 255, 255) #: :class:`Color`: The color of the plane
        self.degree = 0

    @property
    def top(self) -> int:
        """
        Uppermost y value.

        :type: :class:`int`
        """
        return self.y

    @property
    def bottom(self) -> int:
        """
        Bottomost y value.

        :type: :class:`int`
        """
        return self.y + self.height

    @property
    def right(self) -> int:
        """
        Right-most x value.

        :type: :class:`int`
        """
        return self.x + self.width

    @property
    def left(self) -> int:
        """
        Left-most x value.

        :type: :class:`int`
        """
        return self.x
