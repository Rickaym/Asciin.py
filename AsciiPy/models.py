from .methods.renders import rect_and_charpos, rect_and_modelen, slice_fit
from .methods.collisions import coord_collides_with as collide_check
from .rect import Rectable, Rect

try:
    from typing import Tuple, List, str, Any, Dict
except ImportError:
    pass

DEFAULT_BRICK = "#"


class Model(Rectable):
    def __init__(self, path=None, image=None, rect=None, texture=None, coordinate=None):
        # type: (str, str, Rect, str, Tuple[int, int]) -> None
        """
        Defines the integral structure for a model.

        It is used to provide basic inheritance for prerequisites in subsystem interactions.
        For example the model's texture attribute is accessed in a certain
        rendering method and the image attribute is used to analyze it's dimension when none is provided etc..

        When subclassing, overidding the defined methods are operable - so long as it is in awareness of their consequences.
        Overidding those methods require you to follow a strict format as provided by the abstract methods - it is encouraged to
        avoid this unless perfectly necessary.

        Attributes
        ===========
            dimension
        """
        tmp_model = None
        if path is not None:
            with open(path, "r", encoding="utf-8") as f:
                tmp_model = f.read()
        elif image is not None:
            tmp_model = image
        else:
            return
        split_model = tmp_model.split("\n")
        self.dimension = (
            len(max(split_model, key=lambda e: len(e))),
            len(split_model),
        )
        self.image = str(tmp_model)
        self.texture = texture or max(
            tmp_model,
            key=lambda element: tmp_model.count(element) and element != " ",
        )
        self.rect = rect or self.get_rect(
            coordinate=coordinate, dimension=self.dimension
        )
        self.occupancy = []

    def collides_with(self, model):
        # type: (Model) -> bool
        return collide_check(self, model)

    def blit(self, screen, **kwargs):
        # type: (Any, Dict[str, Any]) -> None
        return (
            rect_and_charpos(self, screen, **kwargs)
            if "\n" in self.image
            else rect_and_modelen(self, screen, **kwargs)
        )


class SimpleText(Model):
    def __init__(self, coordinate, text) -> None:
        """
        A Simple text model that stores normal text objects in it's image attribute.

        Uses the slice-fit render method that native menus for the screen uses in a
        system level.
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


class PixelPainter(Model):
    def __init__(self, screen, coordinate=None, dimension=None):
        # type: (Displayable, Tuple(int, int), Tuple(int, int)) -> None
        """
        A model that takes in a coordinate and a dimension to create an empty canvas that is imprinted
        onto the frame at the exact coordinate when blitted onto screen.

        If not obvious, it doesn't directly create an imprint onto the frame - so when drawing onto the canvas
        the distance units and x, y values are relative to the dimensions of the canvas, not the screen.

        Args:
            coordinate (Tuple(int, int)): The (x, y) coordinates that defines the top right of the canvas relative to the screen.
            dimension (Tuple(int, int)): The width and height of the canvas.
        """
        self.coordinate = coordinate or (0, 0)
        self.dimension = dimension or (screen.width, screen.height)
        self.rect = self.get_rect(coordinate=coordinate, dimension=dimension)
        self.image = [" "] * (self.dimension[0] * self.dimension[1])

    def draw(self, *pixels, xy=None, distance=None):
        # type: (List(str), Tuple(int, int), int) -> None
        """
        A gateway to directly editing the pixels in the canvas based on the distance from the origin or
        through coordinates.

        You must pass in either a `xy` or a `distance` kwarg to work.
        Args:
            xy (Optional[Tuple[int, int]]): The x and y position of the pixels to be drawn - Defaults to None.
            distance ([type], optional): The distance of the pixels relative to the origin - Defaults to None.

        Raises:
            TypeError: Raised when neither xy or distance is passed in.
            IndexError: Raised when the coordinate of the pixel is out of bounds.
        """
        if xy is None and distance is None:
            raise TypeError("draw needs either xy or distance point")
        elif xy is not None:
            x, y = xy
            distance = round(x) + (round(y) * self.dimension[0])

        for i, pix in enumerate(pixels):
            try:
                self.image[distance + i] = pix
            except IndexError:
                raise IndexError("list index %d is out of range" % distance)

    def blit(self, screen, **kwargs):
        return rect_and_charpos(self, screen, **kwargs)


class Square(Model):
    def __init__(self, coordinate, length, texture=DEFAULT_BRICK):
        # type: (Tuple[int, int], int, str) -> None
        """
        A Square Model.
        """
        self.length = length

        super().__init__(
            image=(((texture * length) + "\n") * (length // 2)).strip(),
            rect=self.get_rect(coordinate, (length, length // 2)),
            texture=texture,
        )


class Rectangle(Model):
    def __init__(self, coordinate, dimension, texture=DEFAULT_BRICK):
        # type: (Tuple[int, int], Tuple[int, int], str) -> None
        """
        A Rectangle Model.
        """
        super().__init__(
            image=(((texture * dimension[0]) + "\n") * (dimension[1])).strip(),
            rect=self.get_rect(coordinate, dimension),
            texture=texture,
        )
