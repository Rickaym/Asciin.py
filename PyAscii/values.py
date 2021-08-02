from enum import Enum


class Characters(Enum):
    ramp = r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?<>i!lI;:-_+~,"^`'. """
    miniramp = r"""@%#*+=-:. """


class Resolutions(Enum):
    _50c = (50, 25)
    _60c = (60, 30)
    _100c = (100, 50)
    _240c = (352, 240)
    _360c = (480, 360)
    _480c = (858, 480)
    _720c = (1280, 720)
    _768c = (1366, 768)
    _1080c = (1980, 1080)

    @property
    def width(self):
        # type: () -> int
        return self.value[0]

    @property
    def height(self):
        # type: () -> int
        return self.value[1]

    @property
    def pixels(self):
        # type: () -> int
        return self.value[0] * self.value[1]
