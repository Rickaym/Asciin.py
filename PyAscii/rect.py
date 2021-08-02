from uuid import uuid4

try:
    from typing import Tuple, Any
except ImportError:
    pass


__all__ = ["Rectable"]


class Rectable:
    """
    A parent class for all models that are allowed to get a rect attribute
    automatically without user assignment.
    """

    def get_rect(self, coordinate=None, dimension=None):
        # type: (Tuple[int, int], Tuple[int, int], str) -> Rect
        """
        Builds a rect object from scratch with what it's got.
        This only creates a new rectangle object if none is present.

        If present returns `self.rect`
        """
        if self.__dict__.get("rect") is None:
            coordinate = coordinate or (0, 0)
            dimension = dimension or self.dimension
            self.rect = Rect(coordinate, dimension, self)
        return self.rect


class Rect:
    def __init__(self, coordinate, dimension, parent):
        # type: (Tuple[int, int], Tuple[int, int], Any) -> None
        """
        An abstract quadrilateral boundary for Rectable models.

        Provides temporal positions of the given model's boundary.

        This can be an erroneous measurement of collisions when sections of the model
        exceeds the given boundary or an object is moving extremely fast.

        Args:
            coordinate (Tuple[int, int]): starting point of this rectangle
            dimension (Tuple[int, int]): quadrilateral dimension of the rect
            parent (Model): parent model that is being bound by the rect
        """
        self.x = coordinate[0]
        self.y = coordinate[1]

        self.dimension = dimension
        self.parent = parent

        self._id = str(uuid4())[:5]

    @property
    def top(self):
        # type: () -> Tuple[int, int]
        return self.y

    @property
    def bottom(self):
        # type: () -> Tuple[int, int]
        return self.y + self.dimension[1]

    @property
    def right(self):
        # type: () -> Tuple[int, int]
        return self.x + self.dimension[0]

    @property
    def left(self):
        # type: () -> Tuple[int, int]
        return self.x
