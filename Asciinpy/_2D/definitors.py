import itertools

from typing import Callable, Dict, Mapping, Optional, Sequence, Set, Tuple, List

from Asciinpy.utils import get_floor, get_floor_ceil

from ..screen import Screen
from ..types import AnyInt, AnyIntCoordinate
from ..objects import Blitable
from ..values import Color, ANSI
from ..geometry import rotate


OccupancySetType = Set[Tuple[AnyInt, AnyInt]]
CharacterMappingType = Mapping[str, OccupancySetType]
ImageType = List[str]
Transformer = Callable[[AnyIntCoordinate], AnyIntCoordinate]
MaskPixmap = Dict[str, List[AnyIntCoordinate]]


class Collidable:
    """
    An collidable object that exists in 2D space.
    """

    __slots__ = ("occupancy",)

    def __init__(self, occupancy: OccupancySetType = set()):
        self.occupancy = occupancy

    def collides_with(self, model: "Collidable") -> bool:
        """
        Returns True if there are any intersections between the occupation of the collidable itself
        and the collidable being compared.

        :param model:
            The collidable to be compared with.
        :type model: :class:`Collidable`
        :returns: (:class:`bool`) Whether if the current model is in collision with the opposite model.
        """
        # never collides with itself
        if model is self:
            return False
        return bool(self.occupancy.intersection(model.occupancy))


class Plane(Collidable, Blitable):
    """
    A Plane is a static object for a pre-defined image that applies
    to linear motion.

    Throughout the life-time of a plane, it's image is constant - and thus
    reducing unecessary calculations where unecessary.

    This is the most basic structure and objects like Tiles and backgrounds
    are subclasses of Plane.

    Planes cannot rotate, scale, transform etc..
    A mask should be a more preferred object.
    """

    def __init__(
        self, image: str, coordinate: Sequence[AnyInt] = [0, 0], color: Optional[Color] = None
    ):
        super().__init__()
        self.image = image
        self.color = color
        self.topleft = list(coordinate)
        self.dimension = tuple(
            (len(max(image.split("\n"), key=lambda e: len(e))), len(image.split("\n")))
        )

    @property
    def x(self):
        return self.topleft[0]

    @x.setter
    def x(self, value: AnyInt):
        self.topleft[0] = value

    @property
    def y(self):
        return self.topleft[1]

    @y.setter
    def y(self, value: AnyInt):
        self.topleft[1] = value

    @property
    def pixels(self):
        if self.color is not None:
            return self.rasterize()
        else:
            return self.image

    def rasterize(self):
        is_coloring = False
        ammended_pix = list(self.image)
        for i, char in enumerate(self.image):
            if char == "\n":
                continue

            if not is_coloring:
                ammended_pix[i] = "".join((str(self.color), char))
                is_coloring = True
            if i + 1 == len(self.image) or self.image[i + 1] in (" ", "\n"):
                ammended_pix[i] += ANSI.RESET
        return ammended_pix

    def blit(self, screen: Screen):
        x, y = self.x, self.y
        res_width, res_height = screen.resolution.value
        self.occupancy = set()
        for char in self.pixels:
            if char == "\n":
                x = self.x
                y += 1
                continue

            if isinstance(x, float) or isinstance(y, float):
                x, y = round(x), round(y)

            if x >= 0 and x <= res_width and y >= 0 and y <= res_height:
                self.occupancy.add((x, y))
                screen.draw((x, y), char)
            x += 1


class Mask(Collidable, Blitable):
    """
    A masks is a rasterizable object.

    A mask determines a top left point in cartesian space by getting
    the top-most and left-most coordinates of the object regardless of it's shape
    or form.

    Masks rasterizes objects by constructing simply a mappings of pixels instead of shallow images for rasterization and therefore
    extending the operations you can do on Masks.
    """

    __slots__ = ("color", "_coordinate", "_pixmap")

    def __init__(self, image: str, coordinate: Sequence[AnyInt] = [1, 1], color: Optional[Color]=None):
        self.color = color
        self._pixmap = self.get_pixmap(coordinate, image)
        self._topleft = coordinate

    @staticmethod
    def get_pixmap(coordinate: Sequence[AnyInt], image: str) -> MaskPixmap:
        """
        Acquire a pixmap with relative coordinates of the image on the screen.
        """
        x_depth = 0
        pixmap = {}
        x, y = round(coordinate[0]), round(coordinate[1])

        for pixel in image:
            if pixel == "\n":
                x_depth = 0
                y += 1
                continue

            if pixel not in pixmap:
                pixmap[pixel] = []

            pixmap[pixel].append((round(x) + x_depth, y))
            x_depth += 1
        return pixmap

    @property
    def dimension(self) -> AnyIntCoordinate:
        floor, ceil = get_floor_ceil(self.occupancy)
        # we're counting pixels, not calculating distance
        # hence thee increment of ceil by one
        return ceil[0] + 1 - floor[0], ceil[1] + 1 - floor[1]

    @property
    def midpoint(self) -> Tuple[AnyInt, AnyInt]:
        """
        Midpoint of the object - otherwise can be taken as the median.
        """
        size = 0
        sum_x, sum_y = 0, 0
        for _x, _y in self.occupancy:
            sum_x += _x
            sum_y += _y
            size += 1
        return (sum_x / size, sum_y / size)

    @property
    def occupancy(self) -> Set[Tuple[int, int]]:
        """
        A set of all the coordinates that this structure occupies.
        """
        return set(
            map(
                lambda z: (round(z[0]), round(z[1])),
                itertools.chain.from_iterable(self._pixmap.values()),
            )
        )

    @property
    def x(self) -> AnyInt:
        return self._topleft[0]

    @x.setter
    def x(self, value: AnyInt):
        translates = value - self._topleft[0]
        self._topleft = (value, self._topleft[1])
        self.transform(lambda coord: (coord[0] + translates, coord[1]))

    @property
    def y(self) -> AnyInt:
        return self._topleft[1]

    @y.setter
    def y(self, value: AnyInt):
        translates = value - self._topleft[1]
        self._topleft = (self._topleft[0], value)
        self.transform(lambda coord: (coord[0], coord[1] + translates))

    def transform(self, equation: Transformer):
        for k, presences in self._pixmap.items():
            self._pixmap[k] = list(map(equation, presences))

    def rotate(self, theta: AnyInt):
        self.transform(lambda coord: rotate(coord, theta, self.midpoint))
        self._topleft = get_floor(self.occupancy)

    def blit(self, screen: Screen):
        for char, presences in self._pixmap.items():
            for x, y in presences:
                screen.draw((round(x), round(y)), char)
