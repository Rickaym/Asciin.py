import itertools

from typing import Any, Callable, Iterable, Mapping, Set, Tuple, List, Union
from functools import lru_cache

from ..screen import Screen
from ..utils import Color
from ..values import ANSI
from ..geometry import rotate

# Helper lambdas

e_1 = lambda e: e[0]
e_2 = lambda e: e[1]
round_collection = lambda e: (round(e[0]), round(e[1]))

#
# Types
#

AnyInt = Union[int, float]
OccupancySetType = Set[Tuple[AnyInt, AnyInt]]
CharacterMappingType = Mapping[str, OccupancySetType]
ImageType = List[str]

# ---


class Collidable:
    r"""
    An abstract 2D object that is known to occupy an area in space, collisions are based on the
    overlaps between the occupations.
    """

    __slots__ = ("occupancy",)

    def __init__(self, occupancy: OccupancySetType=set()):
        self.occupancy = occupancy

    def collides_with(self, model: "Collidable") -> bool:
        r"""
        Returns True if there are any intersections between the occupation of the collidable itself
        and the collidable being compared.

        :param model:
            The collidable to be compared with.
        :type model: :class:`Collidable`
        :returns: (:class:`bool`) Whether if the current model is in collision with the opposite model.
        """
        if model is self: # the object will not collide with itself
            return False
        return bool(self.occupancy.intersection(model.occupancy))


class Plane(Collidable):
    r"""
    A Plane is a static container for a pre-defined image that adheres only to linear motion. Throughout the life-time of a plane, it will
    never alter the image and thus reducing unecessary calculations where unecessary.
    This is the most basic structure and objects like Tiles and backgrounds are subclasses of Plane.

    Planes cannot rotate, scale, transform etc.. A mask is a more complex form of a Plane.
    """

    def __init__(self, image: str, coordinate: Tuple[int, int]=(1, 1), color: Color=None):
        super().__init__()
        self.image = image
        self.color = color
        self.x = coordinate[0]
        self.y = coordinate[1]

    @staticmethod
    @lru_cache()
    def get_dimension(image):
        return len(max(image.split("\n"), key=lambda e: len(e))), len(image.split("\n"))

    @property
    def dimension(self):
        return Plane.get_dimension(self.image)

    @property
    def pixels(self):
        if self.color is not None:
            return self.rasterize(self.image, self.color)
        else:
            return self.image

    @staticmethod
    def rasterize(image: str, color: Color) -> ImageType:
        mended_pixels = list(image)
        is_coloring = False
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

    def blit(self, screen: Screen, **kwargs) -> OccupancySetType:
        r"""
        Internal blitting method of a general Plane that draws itself onto the screen.
        This method is called implicitely when using :obj:`Screen.blit` and should never be used explicitly.
        It is also important to return the set of occupancy for the Plane in space as an interna blitting method.

        When blitting any Planes it is assumed that the shallow image/pixels are always perfectly rectangular and monotonic
        in it's texture and color.
        """
        x, y = self.x, self.y
        occupancy = []
        for char in self.pixels:
            if char == '\n':
                x = self.x
                y += 1
                continue

            if isinstance(x, float) or isinstance(y, float):
                x, y = round(x), round(y)

            if x >= 0 and x <= screen.width and y >= 0 and y <= screen.height:
                screen.draw((x, y), char)
                occupancy.append((x, y))
            x += 1
        return set(occupancy)


class Mask(Collidable):
    r"""
    A container for a flexible object. Masks procedurally generate the image of a described object, but the first image is obtained from a
    character mapping drived from the first image provided, and thereby giving substance to each and every pixel of the image.
    Furthermore a mask tries to determine a representative point in cartesian space (top left) as a Plane would but the accuracy
    cannot be depended on.

    There is a great difference between Planes and Masks, because Planes are completely dependent on it's representative point and
    the image provided, a limitation is placed on the operations you can do with individual pixels.
    Masks primarily extends this image construction by simply using mappings instead of shallow images for rasterization and therefore
    extending the operations you can do on Masks.
    """

    __slots__ = ("_coordinate", "mappings")

    def __init__(self, coordinate: Tuple[int, int], image: str):
        self.mappings = self.derive_mapping(coordinate, image)
        self._coordinate = coordinate

    @staticmethod
    def derive_mapping(coordinate: Tuple[int, int], image: str) -> CharacterMappingType:
        depth_x = 0
        mappings = {}
        x, y = round(coordinate[0]), round(coordinate[1])

        for pixel in image:
            if pixel == '\n':
                depth_x = 0
                y += 1
                continue

            if mappings.get(pixel) is None:
                mappings[pixel] = []

            mappings[pixel].append((round(x)+depth_x, y))
            depth_x += 1

        return mappings

    @property
    def right(self) -> int:
        return self.x + self.dimension[0]

    @property
    def left(self) -> int:
        return self.x

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + self.dimension[1]

    @property
    def dimension(self) -> Tuple[int, int]:
        floor, ceil = self.get_min_point(self.occupancy), self.get_max_point(self.occupancy)
        return ceil[0]-floor[0]+1, ceil[1]-floor[1]+1

    @property
    def midpoint(self) -> Tuple[int, int]:
        return self.get_midpoint(self._coordinate, self.dimension)

    @property
    def occupancy(self) -> OccupancySetType:
        return self.get_occupancy(self.mappings.values())

    @occupancy.setter
    def occupancy(self, value: Any):
        pass

    @property
    def x(self) -> AnyInt:
        return self._coordinate[0]

    @x.setter
    def x(self, value: AnyInt):
        translates = value - self._coordinate[0]
        self._coordinate = (value, self._coordinate[1])
        self.transform(lambda coord: (coord[0]+translates, coord[1]))

    @property
    def y(self) -> AnyInt:
        return self._coordinate[1]

    @y.setter
    def y(self, value: AnyInt):
        translates = value - self._coordinate[1]
        self._coordinate = (self._coordinate[0], value)
        self.transform(lambda coord: (coord[0], coord[1]+translates))

    @staticmethod
    def get_midpoint(coordinate: Tuple[int, int], dimension: Tuple[int, int]) -> Tuple[int, int]:
        return round(coordinate[0]+(dimension[0]/2)), round(coordinate[1]+(dimension[1]/2))

    @staticmethod
    def get_min_point(occupancy: OccupancySetType) -> Tuple[int, int]:
        return round(min(occupancy, key=e_1)[0]), round(min(occupancy, key=e_2)[1])

    @staticmethod
    def get_max_point(occupancy: OccupancySetType) -> Tuple[int, int]:
        return round(max(occupancy, key=e_1)[0]), round(max(occupancy, key=e_2)[1])

    @staticmethod
    def get_occupancy(mapping: Iterable[OccupancySetType]) -> OccupancySetType:
        return set(map(round_collection, itertools.chain.from_iterable(mapping)))

    def transform(self, equation: Callable[[Tuple[AnyInt, AnyInt]], Tuple[AnyInt, AnyInt]]):
        for char, presences in self.mappings.items():
            self.mappings[char] = tuple(map(equation, presences))

    def rotate(self, theta: AnyInt):
        self.transform(lambda coord: tuple(rotate(coord, theta, self.midpoint)))
        self._coordinate = self.get_min_point(self.occupancy)

    def blit(self, screen: Screen) -> OccupancySetType:
        for char, presences in self.mappings.items():
            for i in presences:
                screen.draw(i, char)

        return self.occupancy
