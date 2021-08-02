from .methods.renders import rect_and_charpos, rect_and_modelen
from .methods.collisions import collides_with as collide_check
from .rect import Rectable, Rect

try:
    from typing import Tuple
except ImportError:
    pass

__all__ = ["Model", "Square"]

DEFAULT_BRICK = "#"


class Model(Rectable):
    """
    Parent class of for all shapes and models.

    The blit method can be overriden - just make sure to accept
    a screen parameter that is passed in during a system call.
    """

    def __init__(self, path=None, image=None, rect=None, texture=None):
        # type: (str, str, Rect, str) -> None
        tmp_model = None
        if path is not None:
            with open(path, "r", encoding="utf-8") as f:
                tmp_model = f.read()
        elif image is not None:
            tmp_model = image
        else:
            return

        self.dimension = (len(tmp_model.split("\n")[0]), len(tmp_model.split("\n")))
        self.image = str(tmp_model)
        self.texture = texture or max(
            tmp_model,
            key=lambda element: tmp_model.count(element) and element != " ",
        )
        self.rect = rect or self.get_rect()

    def collides_with(self, *rects):
        # type: (Rect) -> bool
        return collide_check(self, *rects)

    def blit(self, *args, **kwargs):
        return (
            rect_and_charpos(self, *args, **kwargs)
            if "\n" in self.image
            else rect_and_modelen(self, *args, **kwargs)
        )


class Square(Model):
    """
    Represents a Square shaped Model.
    """

    def __init__(self, coordinate, length, texture=None):
        # type: (Tuple[int, int], Tuple[int, int], str) -> None
        self.length = length

        super().__init__(
            image=(((texture * length) + "\n") * (length // 2)).strip(),
            rect=self.get_rect(coordinate, (length, length // 2)),
            texture=texture,
        )
