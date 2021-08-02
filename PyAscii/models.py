from .methods.renders import rect_and_charpos, rect_and_modelen, slice_fit
from .methods.collisions import collides_with as collide_check
from .rect import Rectable, Rect

try:
    from typing import Tuple
except ImportError:
    pass

__all__ = ["Model", "Square"]

DEFAULT_BRICK = "#"


class Model(Rectable):
    def __init__(self, path=None, image=None, rect=None, texture=None, coordinate=None):
        # type: (str, str, Rect, str, Tuple[int, int]) -> None
        """
        Parent class of for all shapes and models.

        When subclassing under Model, the blit method can be overriden,
        just make sure to accept a single parameter for the screen.

        Can also add extra args and kwargs.
        """
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
        self.rect = rect or self.get_rect(
            coordinate=coordinate, dimension=self.dimension
        )

    def collides_with(self, *rects):
        # type: (Rect) -> bool
        return collide_check(self, *rects)

    def blit(self, screen, **kwargs):
        return (
            rect_and_charpos(self, screen, **kwargs)
            if "\n" in self.image
            else rect_and_modelen(self, screen, **kwargs)
        )


class SimpleText(Model):
    def __init__(self, coordinate, text) -> None:
        """
        A Simple text model that houses normal text objects paired with a slice fit render method.
        """
        super().__init__(image=str(text), coordinate=coordinate)

    def blit(self, screen):
        return slice_fit(self, screen)


class AsciiText(Model):
    def __init__(self, coordinate, text) -> None:
        """
        An ascii text model that turns normal text into ascii text before rendering it.
        """

    def blit(self, screen):
        pass


class Square(Model):
    def __init__(self, coordinate, length, texture=None):
        # type: (Tuple[int, int], Tuple[int, int], str) -> None
        """
        A Square Model.
        """
        self.length = length

        super().__init__(
            image=(((texture * length) + "\n") * (length // 2)).strip(),
            rect=self.get_rect(coordinate, (length, length // 2)),
            texture=texture,
        )
