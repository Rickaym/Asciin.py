import itertools

from os import name as platform

from .rect import Rectable, Rect

from ..geometry import Line, roundi
from ..screen import Color
from ..utils import beautify, caches
from ..values import ANSI

try:
    from typing import Tuple, List, Any, Dict
except ImportError:
    pass


DEFAULT_BRICK = "\u2588" if platform != "nt" else "#"

class Pixels(object):
    """
    Assumes children classes to inherit from :class:`Plane` for rasterization of colored pixels.
    """
    def __init__(self):
        self._color_artf = None
        self._image_artf = None
        self._raster_cache = None

    @property
    def colored_pixels(self):
        """
        Re-rasterize when color or image is changed or altered in any way.
        """
        if self._color_artf is None:
            self._color_artf = self.color
            self._image_artf = self.image

            self._raster_cache = self._rasterize(self.image, self.color)

        if (self.color, self.image) != (self._color_artf, self._image_artf):
            self._raster_cache = self._rasterize(self.image, self.color)

        return self._raster_cache

    def _rasterize(self, image, color):
        mended_pixels = list(image)
        if color is not None:
            is_coloring = False # this is used to track whether if we need to add a color code in front of our character
            for i, char in enumerate(image):
                if char == '\n':
                    continue

                if is_coloring is False:
                    mended_pixels[i] = ''.join((color, char))
                    is_coloring = True
                elif i+1 == len(image) or image[i+1] in (' ', '\n'):
                    mended_pixels[i] += ANSI.RESET
                    is_coloring = False
        return mended_pixels


class Plane(Rectable, Pixels):
    """
    Defines the integral structure for a model on a 2D plane.

    It is used to provide basic inheritance for prerequisites in subsystem interactions.
    For example the model's texture attribute is accessed in a certain
    rendering method and the image attribute is used to analyze it's dimension when none is provided etc..

    When subclassing, overidding the defined methods are operable - so long as it is in awareness of their consequences.
    Overidding those methods require you to follow a strict format as provided by the abstract methods - it is encouraged to
    avoid this unless perfectly necessary.
    """

    def __init__(self, coordinate=None, dimension=None, image=None, rect=None, texture=None, color=None):
        # type: (str, Tuple[int, int], str, Rect, str, str, Color) -> None
        super(Plane, self).__init__()

        self.dimension = dimension  #: Tuple[:class:`int`, :class:`int`]: The dimensions of the model. (Width, Height)
        self.coordinate = coordinate
        self.image = image  #: :class:`str`: The model's image/structure/shape.
        self.color = color #: :class:`Color`: The color of the plane
        self.texture = texture #: :class:`str`: The generalized texture of the entire model. It is the most common character from the image.
        self.rect = rect  #: :class:`Rect`: The rect boundary of the class.
        self.occupancy = []  #: List[:class:`int`]: A list of coordinates that the image would be at when blitted. This is used for collision detection.

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
        if model is self: # colliding to itself?
            return False
        intersections = itertools.chain(model.occupancy, self.occupancy)
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
        pixels = self.colored_pixels
        frame = list(screen._frame)
        # gets the starting index of the image in a straight line screen
        loc = screen._to_distance(self.rect.x, self.rect.y)
        occupancy = [] # the occupancy of this image, used for basic collision checking

        for char in pixels:
            if loc < 0 or loc > screen.resolution.pixels:
                continue

            if char == '\n':
                loc += screen.width - self.dimension[0]
                continue

            try:
                frame[loc] = char
            except IndexError:
                continue
            else:
                occupancy.append(screen._to_coordinate(loc))
                loc += 1
        #raise KeyboardInterrupt(occupancy)
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
        super(SimpleText, self).__init__(image=str(text), coordinate=coordinate, rect=self.get_rect(coordinate, (len(text), 1)))

    def blit(self, screen):
        """
        Fits text onto the current frame.
        An adaptation of how the screen blits it's menubar etc natively.

        Extremely optimized.

        Time Complexity: O(n) where n is len(TEXT)
        """
        point = roundi(self.rect.x) + (screen.resolution.width * roundi(self.rect.y))

        frame = list(screen._frame)
        for char in self.image:
            frame[point] = char
            point += 1

        return frame, set(range(point, point + len(self.image)))


class AsciiText(Plane):
    def __init__(self, coordinate, text):
        pass

    def blit(self, screen, **kwargs):
        pass


class Triangle(Plane):
    """
    A triangle model.


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

    def __init__(self, p1, p2, p3, texture=None, color=None):
        # type: (Tuple[int, int], Tuple[int, int], Tuple[int, int], str, str) -> None
        super(Triangle, self).__init__()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        self.texture = texture or DEFAULT_BRICK
        self.color = color

        min_grp, max_grp = self._get_square_dimension(self.p1, self.p2, self.p3)
        self.dimension = min_grp[0] - max_grp[0], min_grp[1] - max_grp[1]

        self.rect = self.get_rect(dimension=self.dimension)
        self.vertices = (
            Line(self.p1, self.p2),
            Line(self.p2, self.p3),
            Line(self.p1, self.p3),
        )

    def blit(self, screen):
        min_grp, max_grp = self._get_square_dimension(self.p1, self.p2, self.p3)
        self.dimension = max_grp[0]-min_grp[0], max_grp[1]-min_grp[1]
        self.rect.x, self.rect.y = min_grp
        self.image = ([' '] * (self.dimension[0] * self.dimension[1]))
        for vert in self.vertices:
            for p in vert.points:
                loc = abs(p[0]-min_grp[0]) + (abs(p[1]-min_grp[1])*self.dimension[0])
                # TODO: triangle image is either terrible or the rasterize method is broken
                raise KeyboardInterrupt(loc, p)
                self.image[roundi(loc)] = self.texture

        raise KeyboardInterrupt("".join(self.colored_pixels))
        return super(Triangle, self).blit(screen)

    @caches
    def _get_square_dimension(self, p1, p2, p3):
        return (min((p1, p2, p3), key=lambda e: e[0])[0], min((p1, p2, p3), key=lambda e: e[1])[1]), (max((p1, p2, p3), key=lambda e: e[0])[0], max((p1, p2, p3), key=lambda e: e[1])[1])


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
        super(PixelPainter, self).__init__()
        self.coordinate = coordinate or 0, 0
        self.screen = screen
        self.dimension = dimension or (screen.width, screen.height)
        self.rect = self.get_rect(coordinate=coordinate, dimension=dimension)
        self.image = [" "] * (self.dimension[0] * self.dimension[1])

    def draw(self, pixels, coordinate, color=None):
        # type: (List(str), Tuple(int, int), Color) -> None
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
        :param color:
            The color of the pixel.
        :type color: :class:`Color`

        :raises TypeError: Raised when neither xy or distance is passed in.
        :raises IndexError: Raised when the coordinate of the pixel is out of bounds.
        """
        distance = self.screen._to_distance(coordinate[0], coordinate[1])

        for i, pix in enumerate(pixels):
            try:
                self.image[distance + i] = pix if color is None else ''.join((color, pix, ANSI.RESET))
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
        self.color = color
        self.image = image
        self.rect = self.get_rect(coordinate, (length, length // 2))
        self.length = length

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