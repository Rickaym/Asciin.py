import itertools
import numpy as np
import sys

from typing import Callable, Dict, Mapping, Set, Tuple, List, Union

sys.path.append("D:/Programming/Python/Projects/PyAscii/")

from Asciinpy.types import AnyInt
from Asciinpy.objects import Blitable
from Asciinpy.utils import Color
from Asciinpy.values import ANSI, Resolutions
from Asciinpy.geometry import rotate

# Helper lambdas

e_1 = lambda e: e[0]
e_2 = lambda e: e[1]
round_collection = lambda e: tuple(map(round, e))

#
# Types
#
OccupancySetType = Set[Tuple[AnyInt, AnyInt]]
CharacterMappingType = Mapping[str, OccupancySetType]
ImageType = List[str]
MaskPixelMapping =  Dict[str, np.ndarray]
# ---


class Collidable:
    r"""
    An collidable object that exists in 2D space.
    """

    __slots__ = ("occupancy",)

    def __init__(self, occupancy: OccupancySetType = set()):
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
        # never collides with itself
        if model is self:
            return False
        return bool(self.occupancy.intersection(model.occupancy))


class Plane(Collidable, Blitable):
    r"""
    A Plane is a static container for a pre-defined image that adheres only to linear motion. Throughout the life-time of a plane, it will
    never alter the image and thus reducing unecessary calculations where unecessary.
    This is the most basic structure and objects like Tiles and backgrounds are subclasses of Plane.

    Planes cannot rotate, scale, transform etc.. A mask is a more complex form of a Plane.
    """

    def __init__(
        self, image: str, coordinate: List[AnyInt] = [0, 0], color: Color = None
    ):
        super().__init__()
        self.image = image
        self.color = color
        self.topleft = list(coordinate)
        self.dimension = tuple((len(max(image.split("\n"), key=lambda e: len(e))), len(image.split("\n"))))

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
            return self.rasterize(self.image, self.color)
        else:
            return self.image

    @staticmethod
    def rasterize(image: str, color: Color) -> ImageType:
        mended_pixels = list(image)
        is_coloring = False
        for i, char in enumerate(image):
            if char == "\n":
                continue

            if is_coloring is False:
                mended_pixels[i] = "".join((str(color), char))
                is_coloring = True
            elif i + 1 == len(image) or image[i + 1] in (" ", "\n"):
                mended_pixels[i] += ANSI.RESET
                is_coloring = False

        return mended_pixels

    def blit(self, resolution: Resolutions, draw: Callable[[int, int, str], None]):
        x, y = self.x, self.y
        self.occupancy = []
        for char in self.pixels:
            if char == "\n":
                x = self.x
                y += 1
                continue

            if isinstance(x, float) or isinstance(y, float):
                x, y = round(x), round(y)

            if x >= 0 and x <= resolution.width and y >= 0 and y <= resolution.height:
                self.occupancy.append((x, y))
                draw(x, y, char)
            x += 1
        self.occupancy = np.array(set(self.occupancy))


class Mask(Collidable, Blitable):
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

    __slots__ = ("_coordinate", "_mappings")

    def __init__(self, coordinate: List[int], image: str):
        self._mappings = self.derive_mapping(coordinate, image)
        self._coordinate = coordinate

    @staticmethod
    def derive_mapping(coordinate: List[int], image: str) -> MaskPixelMapping:
        depth_x = 0
        mappings = {}
        x, y = round(coordinate[0]), round(coordinate[1])

        for pixel in image:
            if pixel == "\n":
                depth_x = 0
                y += 1
                continue

            if mappings.get(pixel) is None:
                mappings[pixel] = []

            mappings[pixel].append(np.array((round(x) + depth_x, y)))
            depth_x += 1
        mappings = {k:np.array(v) for k, v in mappings.items()}
        return mappings

    @property
    def dimension(self) -> np.ndarray:
        floor, ceil = np.min(self.occupancy, axis=0), np.max(self.occupancy, axis=0)
        # we're counting pixels, not calculating distance
        # therefore we must increment the ceil by one
        return ceil + 1 - floor

    @property
    def midpoint(self) -> np.ndarray:
        r"""
        Midpoint of the object - otherwise can be taken as the median.
        """
        return self.occupancy.sum(axis=0) / len(self.occupancy)

    @property
    def occupancy(self) -> np.ndarray:
        r"""
        An array of all the coordinates that this structure occupies.
        """
        return np.array(list(itertools.chain.from_iterable(self._mappings.values()))).round()

    @property
    def x(self) -> AnyInt:
        return self._coordinate[0]

    @x.setter
    def x(self, value: AnyInt):
        translates = value - self._coordinate[0]
        self._coordinate = (value, self._coordinate[1])
        self.transform(lambda coord: coord + [translates, 0])

    @property
    def y(self) -> AnyInt:
        return self._coordinate[1]

    @y.setter
    def y(self, value: AnyInt):
        translates = value - self._coordinate[1]
        self._coordinate = (self._coordinate[0], value)
        self.transform(lambda coord: (coord + [0, translates]))

    def transform(
        self, equation: Callable[[np.ndarray], Union[Tuple[int, int], np.ndarray, List[int]]]
    ):
        for k, presences in self._mappings.items():
            self._mappings[k] = np.array(list(map(equation, presences)))

    def rotate(self, theta: AnyInt):
        self.transform(lambda coord: rotate(coord, theta, self.midpoint))
        self._coordinate = np.min(self.occupancy, axis=0)

    def blit(self, r: Resolutions, draw: Callable[[np.ndarray, str], None]):
        for char, presences in self._mappings.items():
            for i in presences:
                draw(i.round(), char)

if __name__ == "__main__":
    obj = Mask([0, 0], "###\n###\n###")
    print(obj._mappings)
    obj.transform(lambda e: [e[0]+1, e[1]+1])

