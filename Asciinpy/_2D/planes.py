from Asciinpy.utils import caches
from Asciinpy.values import ANSI
from os import name as platform

from .rect import Rectable, Rect

from ..geometry import Line, roundi
from ..screen import Color

try:
    from typing import Tuple, List, Any, Dict
except ImportError:
    pass


DEFAULT_BRICK = "\u2588" if platform != "nt" else "#"
DEFAULT_FILL = "\u2588" if platform != "nt" else "#"

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
        self.color = color #: :class:`Color`: The color of the plane
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
        # type: (Plane) -> bool
        """
        Checks whether if the current model is in collision with the provided
        model.

        :param model:
            The opposing model.
        :type model: :class:`Model`
        :returns: (:class:`bool`) Whether if the current model is in collision with the opposite model.
        """
        if model is self:
            return False
        intersections = []
        intersections.extend(model.occupancy)
        intersections.extend(self.occupancy)
        if len(set(intersections)) < (
            len(model.occupancy) + len(self.occupancy)
        ):
            return True
        else:
            return False

    def blit(self, screen, **kwargs):
        # type: (Screen, Dict[str, Any]) -> None
        """
        Figures out the position of the characters based on the temporal position and
        the position of the character in the model image.

        Time Complexity of this method is O(n) where n is
        the total amount of characters in a model image.

        :param screen:
            This is passed in the subsystem call inside the :obj:`Screen.blit`.
        :type screen: :class:`Screen`
        """
        pixels = list(self.image)
        frame = list(screen._frame)

        # gets the starting index of the image in a straight line screen
        loc = roundi(self.rect.x) + (roundi(self.rect.y) * screen.resolution.width)

        # the real depth of any pixel in time relative to the image
        x_depth = 0
        y_depth = 0

        # Smart coloring, we don't really want the console to color each and ever character without necessity
        is_coloring = False # this is used to track whether if we need to add a color code in front of our character
        texture_resets = True # a one time flag that helps keep track of reseting color mode after newlines (only relevant to outlines)
        occupancy = [] # the occupancy of this image

        for i, char in enumerate(pixels):
            color = self.color
            if loc < 0 or loc > screen.pixels:
                continue

            # rects don't have their own rasterizing methods so we have to do it as a part
            # of the model rendering routine if a texture is present
            if self.rect.texture:
                # because this is the "rect's rasterizing" method, we only do it on edges and verticies
                if char == '\n':
                    # this is a one time flag so that texture and coloring is reset every newline
                    texture_resets = True
                elif self.is_margin(x_depth, y_depth, i, pixels):
                    char = self.rect.texture
                    color = self.rect.color
                else:
                    if is_coloring is True and texture_resets:
                        is_coloring = False
                        texture_resets = False

            if char == '\n':
                frame[loc-1] += ANSI.RESET
                loc += screen.width - x_depth
                is_coloring = False
                x_depth = 0
                y_depth += 1
                continue
            elif char == ' ':
                continue

            if color is not None:
                if is_coloring is False:
                    char = ''.join((color, char))
                    is_coloring = True
                elif i+1 == len(pixels) or pixels[i+1] == ' ' or (self.rect.texture is not None and self.is_margin(x_depth+1, y_depth, i, pixels) and not self.is_y_margin(y_depth)):
                    char += ANSI.RESET
                    is_coloring = False
            try:
                frame[loc] = char
            except IndexError:
                continue
            else:
                occupancy.append(loc)
                loc += 1
                x_depth += 1

        if False:
            raise KeyboardInterrupt(repr(''.join(frame)[:-1].strip().replace("\x1b[38;2;0;255;0m", "G", -1).replace("\x1b[38;2;255;0;0m", "R", -1).replace("\x1b[0m", "T", -1)))
        return frame, set(occupancy)


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
        """
        Fits text onto the current frame.
        An adaptation of how the screen blits it's menubar etc natively.

        Extremely optimized.

        Time Complexity: O(n) where n is len(TEXT)
        """
        point = roundi(self.rect.x) + (screen.resolution.width * roundi(self.rect.y))
        if point < 0:
            point = screen.resolution.width + point

        frame = list(screen._frame[:point])
        frame.extend(list(self.image))
        frame.extend(screen._frame[point + len(self.image) :])

        return frame, set(range(point, point + len(self.image)))


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
    :type screen: :class:`Screen`
    :param coordinate:
        The (x, y) coordinates that defines the top right of the canvas relative to the screen.
    :type coordinate: Tuple[:class:`int`, :class:`int`]
    :param dimension:
        The width and height of the canvas.
    :type dimension: Tuple[:class:`int`, :class:`int`]
    """

    def __init__(self, screen, coordinate=None, dimension=None):
        # type: (Screen, Tuple(int, int), Tuple(int, int)) -> None
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
        distance = self.screen.to_distance(coordinate)

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

    def __init__(self, coordinate, length, texture=None, color=None):
        # type: (Tuple[int, int], int, str, str) -> None
        super(Square, self).__init__(color=color)
        self.texture = texture or DEFAULT_BRICK
        self.occupancy = []
        self.dimension = (length, length//2)
        image = ((( self.texture * length) + "\n") * (length // 2)).strip()
        if color is not None:
            pass
            #image = color + image + ANSI.RESET
        self.image = image
        self.rect = self.get_rect(coordinate, (length, length // 2))
        self.length = length
        self.color = color

        self.is_y_margin = caches(lambda y: y == 0 or y == (self.dimension[1]-1))
        self.is_x_margin = caches(lambda x: x == 0 or  x == (self.dimension[0]-1))
        self.is_lst_margin = caches(lambda count, pixels: count == (len(pixels) - 1))
        self.is_margin = caches(lambda x, y, count, pixels: self.is_x_margin(x) or self.is_y_margin(y) or self.is_lst_margin(count, pixels))


def rect_and_modelen(model, screen, empty=False):
    # type: (Plane, Screen, bool) -> Tuple[List[str], Set[int]]
    """
    Figures out the positions of characters by using the position of the character in the model
    image and it's desired dimensions to guess where it is on the screen.

    The only time you would want to use this is if you somehow cannot have newline characters in your image.

    Time Complexity of this method is O(n) where n is
    the total amount of characters in a model image.

    Kept for referencing purposes.
    """
    frame = list(screen._frame) if not empty else list(screen.emptyframe)
    occupancy = []

    for row in range(model.rect.dimension[1]):
        for col in range(model.rect.dimension[0]):
            loc = (
                round(model.rect.x)
                + col
                + (screen.resolution.width * row)
                + round(model.rect.y) * screen.resolution.width
            )
            occupancy.append(loc)
            try:
                frame[loc] = model.texture
            except IndexError:
                pass

    return frame, set(occupancy)