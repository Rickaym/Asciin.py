from uuid import uuid4

from ..screen import Color

try:
    from typing import Tuple, Any
except ImportError:
    pass


class Rectable(object):
    """
    A simple parent class for all models that can be translated into a rect.
    """

    def get_rect(self, coordinate=None, dimension=None):
        # type: (Tuple[int, int], Tuple[int, int]) -> Rect
        """
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

    @staticmethod
    def make_rect(self, coordinate, dimension):
        # type: (Tuple[int, int], Tuple[int, int], str) -> Rect
        """
        Builds a rect object from the given arguments.

        :param coordinate:
            The top left coordinate of the rect.
        :type coordinate: Tuple[:class:`int`, :class:`int`]
        :param dimension:
            A tuple width it's width and height.
        :type dimension: Tuple[:class:`int`, :class:`int`]

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

    def __init__(self, coordinate, dimension, parent):
        # type: (Tuple[int, int], Tuple[int, int], Any) -> None
        self.x = coordinate[0]  #: :class:`int`: Top left x position
        self.y = coordinate[1]  #: :class:`int`: Top left y position
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
        self._id = str(uuid4())[:5]

    @property
    def top(self):
        # type: () -> int
        """
        Uppermost y value.

        :type: :class:`int`
        """
        return self.y

    @property
    def bottom(self):
        # type: () -> int
        """
        Bottomost y value.

        :type: :class:`int`
        """
        return self.y + self.height

    @property
    def right(self):
        # type: () -> int
        """
        Right-most x value.

        :type: :class:`int`
        """
        return self.x + self.width

    @property
    def left(self):
        # type: () -> int
        """
        Left-most x value.

        :type: :class:`int`
        """
        return self.x
