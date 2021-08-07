from uuid import uuid4

try:
    from typing import Tuple, Any
except ImportError:
    pass


class Rectable:
    """
    A parent class for all models that are required to get a rect attribute
    automatically without user assignment.
    """

    def get_rect(self, coordinate=None, dimension=None):
        # type: (Tuple[int, int], Tuple[int, int], str) -> Rect
        """
        Builds a rect object from scratch. If neither coordinate or dimension
        is given, the coordinate is assumed to be the origin and the dimension is fetched
        from the parent Object.

        This only creates a new rectangle object if none is present.
        If present returns what it already has.
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


        Args:
            coordinate (Tuple[int, int]): The top left coordinate of the rect.
            dimension (Tuple[int, int]): A tuple width it's width and height.

        Returns:
            Rect: The rect object made.
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

    Attributes
    ===========
        x (int): Top left x position

        y (int): Top left y position

        width (int): The width of the rect. This is the horizontal difference.

        height (int): The height of the rect (or length) this is the vertical difference.

        parent (Model): A Parent object that the rect is assigned under.

        texture (str): The outline texture of the rect.
    """

    def __init__(self, coordinate, dimension, parent):
        # type: (Tuple[int, int], Tuple[int, int], Any) -> None
        self.x = coordinate[0]
        self.y = coordinate[1]
        self.width = dimension[0]
        self.height = dimension[1]
        self.parent = parent
        self.texture = ""

        self._id = str(uuid4())[:5]

    @property
    def top(self):
        # type: () -> int
        """
        Uppermost y value.

        Returns:
            int
        """
        return self.y

    @property
    def bottom(self):
        # type: () -> int
        """
        Bottomost y value.

        Returns:
            int
        """
        return self.y + self.height

    @property
    def right(self):
        # type: () -> int
        """
        Right-most x value.

        Returns:
            int
        """
        return self.x + self.width

    @property
    def left(self):
        # type: () -> int
        """
        Left-most x value.

        Returns:
            int
        """
        return self.x
