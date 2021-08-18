from Asciinpy.screen import Color
from .methods.renders import rect_and_charpos, rect_and_modelen, slice_fit
from .methods.collisions import coord_collides_with
from .rect import Rectable, Rect

from ..math import Line

try:
    from typing import Tuple, List, Any, Dict
except ImportError:
    pass


DEFAULT_BRICK = "@"
DEFAULT_FILL = "&"

class Plane(Rectable):
    """
    Defines the integral structure for a model on a 2D plane.

    It is used to provide basic inheritance for prerequisites in subsystem interactions.
    For example the model's texture attribute is accessed in a certain
    rendering method and the image attribute is used to analyze it's dimension when none is provided etc..

    When subclassing, overidding the defined methods are operable - so long as it is in awareness of their consequences.
    Overidding those methods require you to follow a strict format as provided by the abstract methods - it is encouraged to
    avoid this unless perfectly necessary.
    """

    def __init__(self, path=None, coordinate=None, image=None, rect=None, texture=None, color=None):
        # type: (str, Tuple[int, int], str, Rect, str, str, Color) -> None
        tmp_model = None
        if path is not None:
            with open(path, "r") as f:
                tmp_model = f.read()
        elif image is not None:
            tmp_model = image
        else:
            return
        split_model = tmp_model.split("\n")

        self.dimension = (
            len(max(split_model, key=lambda e: len(e))),
            len(split_model),
        )  #: Tuple[:class:`int`, :class:`int`]: The dimensions of the model. (Width, Height)
        self.image = str(tmp_model)  #: :class:`str`: The model's image/structure/shape.
        self.color = color or Color.FORE(255, 255, 255)
        self.texture = texture or max(
            tmp_model,
            key=lambda element: tmp_model.count(element) and element != " ",
        ) #: :class:`str`: The generalized texture of the entire model. It is the most common character from the image.
        self.rect = rect or self.get_rect(
            coordinate=coordinate, dimension=self.dimension
        )  #: :class:`Rect`: The rect boundary of the class.
        self.occupancy = (
            []
        )  #: List[:class:`int`]: A list of coordinates that the image would be at when blitted. This is used for collision detection.

    def collides_with(self, model):
        # type: (Model) -> bool
        """
        Checks whether if the current model is in collision with the provided
        model.

        :param model:
            The opposing model.
        :type model: :class:`Model`
        :returns: (:class:`bool`) Whether if the current model is in collision with the opposite model.
        """
        return coord_collides_with(self, model)

    def blit(self, screen, **kwargs):
        # type: (Displayable, Dict[str, Any]) -> None
        """
        The inner blitting method of the model. You should not use this yourself.

        :param screen:
            This is passed in the subsystem call inside the :obj:`Displayable.blit`.
        :type screen: :class:`Displayable`
        """
        return (
            rect_and_charpos(self, screen, **kwargs)
            if "\n" in self.image
            else rect_and_modelen(self, screen, **kwargs)
        )


class SimpleText(Plane):
    """
    A Simple text model that stores normal text objects in it's image attribute.

    Uses the slice-fit render method that native menus for the screen uses in a
    system level.

    :param coordinate:
        The top-left coordinate of the text.
    :type coordinate: Tuple[:class:`int`, :class:`int`]

    :param text:
        The text for the model.
    :type text: :class:`str`
    """

    def __init__(self, coordinate, text):
        super(SimpleText, self).__init__(image=str(text), coordinate=coordinate)

    def blit(self, screen):
        return slice_fit(self, screen)


class AsciiText(Plane):
    def __init__(self, coordinate, text):
        pass

    def blit(self, screen, **kwargs):
        pass


class Triangle(Plane):
    """
    A triangle model, this is often used as a 3D primitive.

    :param p1:
        Pivot or starting point
    :type p1: Tuple[:class:`int`, :class:`int`]
    :param p2:
        Certain bottom point
    :type p2: Tuple[:class:`int`, :class:`int`]
    :param p3:
        Certain bottom point
    :type p3: Tuple[:class:`int`, :class:`int`]
    """

    def __init__(self, p1, p2, p3, texture=None, fill=None):
        # type: (Tuple[int, int], Tuple[int, int], Tuple[int, int], str, str) -> None
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        self.texture = texture or DEFAULT_BRICK
        self.fill = fill or DEFAULT_FILL
        self.vertices = (
            Line(self.p1, self.p2),
            Line(self.p2, self.p3),
            Line(self.p1, self.p3),
        )

    def blit(self, screen):
        frame = list(screen._frame)
        blitted = []
        for vert in self.vertices:
            for p in vert.points:
                loc = screen.to_distance(p)
                blitted.append(p)
                try:
                    frame[loc] = self.texture
                except IndexError:
                    pass
                except TypeError:
                    raise TypeError(
                        "list indices must be integers, not {} of value {}".format(
                            type(loc), loc
                        )
                    )
        return frame, set(blitted)


class PixelPainter(Plane):
    """
    A model that takes in a coordinate and a dimension to create an empty canvas that is imprinted
    onto the frame at the exact coordinate when blitted onto screen.

    If not obvious, it doesn't directly create an imprint onto the frame - so when drawing onto the canvas
    the distance units and x, y values are relative to the dimensions of the canvas, not the screen.

    :param screen:
        The screen of which the PixelPainter is attached to.
    :type screen: :class:`Displayable`
    :param coordinate:
        The (x, y) coordinates that defines the top right of the canvas relative to the screen.
    :type coordinate: Tuple[:class:`int`, :class:`int`]
    :param dimension:
        The width and height of the canvas.
    :type dimension: Tuple[:class:`int`, :class:`int`]
    """

    def __init__(self, screen, coordinate=None, dimension=None):
        # type: (Displayable, Tuple(int, int), Tuple(int, int)) -> None
        self.coordinate = coordinate or 0, 0
        self.screen = screen
        self.dimension = dimension or (screen.width, screen.height)
        self.rect = self.get_rect(coordinate=coordinate, dimension=dimension)
        self.image = [" "] * (self.dimension[0] * self.dimension[1])

    def draw(self, pixels, coordinate):
        # type: (List(str), Tuple(int, int)) -> None
        """
        A gateway to directly editing the pixels in the canvas based on the distance from the origin or
        through coordinates.

        You must pass in either a `xy` or a `distance` kwarg to work.

        :param pixels:
            The pixels to be drawn.
        :type pixels: List[:class:`str`]
        :param coordinate:
            The x and y position of the pixels to be drawn - Defaults to None.
        :type coordinate: Tuple[:class:`int`, :class:`int`]

        :raises TypeError: Raised when neither xy or distance is passed in.
        :raises IndexError: Raised when the coordinate of the pixel is out of bounds.
        """
        distance = self.screen.to_distance(coordinate[0], coordinate[1])

        for i, pix in enumerate(pixels):
            try:
                self.image[distance + i] = pix
            except IndexError:
                raise IndexError("list index {} is out of range".format(distance))
            except TypeError:
                raise TypeError(
                    "list indices must be integers, not {} of value {}".format(
                        type(distance), distance
                    )
                )

    def blit(self, screen, **kwargs):
        return rect_and_charpos(self, screen, **kwargs)


class Square(Plane):
    """
    A Square Model.

    :param coordinate:
        The top-left coordiante of the square.
    :type coordinate: Tuple[:class:`int`, :class:`int`]
    :param length:
        The length of the square.
    :type length: :class:`int`
    :param texture:
        The monotone texture of the square.
    :type texture: :class:`str`
    """

    def __init__(self, coordinate, length, texture=None, fill=None):
        # type: (Tuple[int, int], int, str, str) -> None
        self.length = length

        super().__init__(
            image=(((texture * length) + "\n") * (length // 2)).strip(),
            rect=self.get_rect(coordinate, (length, length // 2)),
            texture=texture or DEFAULT_BRICK,
            fill=fill or DEFAULT_FILL,
        )

