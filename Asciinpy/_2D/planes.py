import itertools

from .rect import Rectable, Rect
from ..geometry import Line
from ..utils import AssetCached, Color, asset, beautify
from ..screen import Screen
from ..values import ANSI
from ..globals import PLATFORM

from typing import Set, Tuple, List, Union

"""
TODO: Fix triangle blitting
      Add 2D rotation and scaling
      Make a :class:`Polygon` for n amount of vertices
      Filter out type comments
"""

DEFAULT_BRICK = "\u2588" if PLATFORM != "Windows" else "#"


class Rasterizer(AssetCached):
    """
    Rasterizes any rectangular image of a plane to be colorized.
    """
    def __init__(self, image: str=None, color: Color = None):
        self.image = image
        self.color = color

    @property
    def colored_pixels(self):
        if self.color is not None:
            return self._get_rasterized()
        else:
            return self.image

    @asset(lambda: ("self.image", "self.color"))
    def _get_rasterized(self) -> List[str]:
        mended_pixels = list(self.image)
        is_coloring = False # this is used to track whether if we need to add a color code in front of our character
        for i, char in enumerate(self.image):
            if char == '\n':
                continue

            if is_coloring is False:
                mended_pixels[i] = ''.join((self.color, char))
                is_coloring = True
            elif i+1 == len(self.image) or self.image[i+1] in (' ', '\n'):
                mended_pixels[i] += ANSI.RESET
                is_coloring = False
        return mended_pixels


class Collidable:
    """
    An abstract 2D object that is known to occupy an area in space, collisions are based on the
    overlaps between the occupations.
    """
    def __init__(self, occupancy: List[Tuple[int, int]]=[]):
        self.occupancy = occupancy

    def collides_with(self, model: "Collidable") -> bool:
        """
        Checks whether if the current model is in collision with the provided
        model.

        :param model:
            The opposing model.
        :type model: :class:`Collidable`
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


class Plane(Rectable, Collidable, Rasterizer):
    r"""
    Defines the integral structure for a model on a 2D plane.

    It is used to provide basic inheritance for prerequisites in subsystem interactions.
    For example the model's texture attribute is accessed in a certain
    rendering method and the image attribute is used to analyze it's dimension when none is provided etc..

    When subclassing, overidding the defined methods are operable - so long as it is in awareness of their consequences.
    Overidding those methods require you to follow a strict format as provided by the abstract methods - it is encouraged to
    avoid this unless perfectly necessary.
    """

    __slots__ = ("dimension", "coordinate", "image", "color", "text", "rect", "occupancy")

    def __init__(self, coordinate: Tuple[int, int]=None, dimension: Tuple[int, int]=None, image: str=None, rect: Rect=None, texture: str=None, color: Color=None):
        self.dimension = dimension  #: Tuple[:class:`int`, :class:`int`]: The dimensions of the model. (Width, Height)
        self.coordinate = coordinate
        self.image = image  #: :class:`str`: The model's image/structure/shape.
        self.color = color #: :class:`Color`: The color of the plane
        self.texture = texture #: :class:`str`: The generalized texture of the entire model. It is the most common character from the image.
        self.rect = rect  #: :class:`Rect`: The rect boundary of the class.
        self.occupancy = []  #: List[:class:`int`]: A list of coordinates that the image would be at when blitted. This is used for collision detection.

    def blit(self, screen: Screen, **kwargs) -> Set[Tuple[Union[float, int], Union[float, int]]]:
        r"""
        Figures out the position of the characters based on the temporal position and
        the position of the character in the model image.

        Time Complexity of this method is O(n) where n is
        the total amount of characters in a model image.

        :param screen:
            This is passed in the subsystem call inside the :obj:`Screen.blit`.
        :type screen: :class:`Screen`
        """
        pixels = self.colored_pixels

        x, y = self.rect.x, self.rect.y
        occupancy = []
        for char in pixels:
            if char == '\n':
                x = self.rect.x
                y += 1
                continue

            if isinstance(x, float) or isinstance(y, float):
                x, y = round(x), round(y)

            if x >= 0 and x <= screen.width and y >= 0 and y <= screen.height:
                # frame is type CartesianList therefore cartesian coordinates are oll korrect
                screen.draw((x, y), char)
                occupancy.append((x, y))
            x += 1
        return set(occupancy)


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

    def __init__(self, coordinate: Tuple[int, int], text: str):
        super(SimpleText, self).__init__(image=str(text), coordinate=coordinate, rect=self.get_rect(coordinate, (len(text), 1)))

    def blit(self, screen: Screen):
        """
        Fits text onto the current frame.
        An adaptation of how the screen blits it's menubar etc natively.

        Extremely optimized.

        Time Complexity: O(n) where n is len(TEXT)
        """
        point = round(self.rect.x) + (screen.resolution.width * round(self.rect.y))

        frame = list(screen._frame)
        for char in self.image:
            frame[point] = char
            point += 1

        return frame, set(range(point, point + len(self.image)))


class Polygon(Plane):
    __slots__ = ("vertices")
    def __init__(self, edges: int, coordinates: List[Tuple[int, int]]):
        if edges != len(coordinates):
            raise TypeError("lengths and coordinates must have the size equal to it's edges")
        self.vertices = []
        c = 0
        while c > edges:
            self.vertices.append(Line(coordinates[c], coordinates[c+1]))
            c += 2
        self.vertices.append(Line(coordinates[0], coordinates[-1]))


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
        self.image = [[' ']* (self.dimension[0]+1)] * (self.dimension[1]+1)
        for vert in self.vertices:
            for p in vert.points:
                p = round(p[0] - min_grp[0]), round(p[1] - min_grp[1])
                try:
                    self.image[p[1]][p[0]] = self.texture
                except IndexError:
                    raise IndexError(p, min_grp, max_grp)
        raise KeyboardInterrupt(beautify(self.dimension, itertools.chain.from_iterable(self.image)))
        return super().blit(screen)

    def _get_square_dimension(self, p1, p2, p3):
        return (min((p1, p2, p3), key=lambda e: e[0])[0], min((p1, p2, p3), key=lambda e: e[1])[1]), (max((p1, p2, p3), key=lambda e: e[0])[0], max((p1, p2, p3), key=lambda e: e[1])[1])


class Mask(Plane):
    r"""
    A model that takes in a coordinate and a dimension to create an empty mask imprinted
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

    def __init__(self, screen: Screen, coordinate: Tuple[int, int]=None, dimension: Tuple[int, int]=None):
        self.coordinate = coordinate or 0, 0
        self.screen = screen
        self.dimension = dimension or (screen.width, screen.height)
        self.rect = self.get_rect(coordinate=coordinate, dimension=dimension)
        self.color = None
        self.image = [" "] * (self.dimension[0] * self.dimension[1])

    def draw(self, pixels: List[str], coordinate: Tuple[int, int], color: Color=None):
        r"""
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
            self.image[distance + i] = pix if color is None else ''.join((color, pix, ANSI.RESET))


class Square(Plane):
    r"""
    A Square Model ~ is neither derived from Polygon nor line for optimization.

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
        super().__init__()
        self.texture = texture or DEFAULT_BRICK
        self.occupancy = []
        self.dimension = (length, length//2) if isinstance(length, int) else length
        image = (((self.texture * self.dimension[0]) + "\n") * (self.dimension[1])).strip()
        if color is not None:
            pass
            #image = color + image + ANSI.RESET
        self.color = color
        self.image = image
        self.rect = self.get_rect(coordinate, self.dimension)
        self.length = length
