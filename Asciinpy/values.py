from enum import Enum
from random import randint
from typing import Tuple


class Color(Enum):
    Initial = None
    Black = 0x000000
    Gray = 0x767676
    Grey = 0x767676
    Blue = 0x0037DA
    Green = 0x13A10E
    Aqua = 0x3B78FF
    Red = 0xC50F1F
    Purple = 0x881798
    Yellow = 0xC19C00

    LightBlue = 0x3A96DD
    LightGreen = 0x16C60C
    LightAqua = 0x61D6D6
    LightRed = 0xE74856
    LightPurple = 0xB4009E
    LightYellow = 0xF9F1A5

    White = 0xF2F2F2
    BrightWhite = 0xFFFFFF

    """
    Color management class.
    """

    @staticmethod
    def rgb_foreground(r, g, b):
        return ANSI.CSI + "38;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def rgb_background(r, g, b):
        return ANSI.CSI + "48;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def foreground(r: int, g: int, b: int):
        """
        Colors the foreground with a given RGB value.
        """
        return Color.rgb_foreground(r, g, b)

    @staticmethod
    def background(r: int, g: int, b: int):
        """
        Colors the background with a given RGB value.
        """
        return Color.rgb_background(r, g, b)

    @staticmethod
    def foreground_random(grayscale=False):
        """
        Random foreground color.
        """
        if grayscale:
            rgb = (randint(0, 255),) * 3
        else:
            rgb = (randint(0, 255), randint(0, 255), randint(0, 255))

        return Color.foreground(*rgb)

    @staticmethod
    def background_random(grayscale=False):
        """
        Random backgroun color.
        """
        if grayscale:
            rgb = (randint(0, 255),) * 3
        else:
            rgb = (randint(0, 255), randint(0, 255), randint(0, 255))

        return Color.background(*rgb)


# A mapping to singular "identifiers" used for command prompt
# background/foreground color
WINDOW_COLOR_HEXES = {
    Color.Black: 0,
    Color.Blue: 1,
    Color.Green: 2,
    Color.Aqua: 3,
    Color.Red: 4,
    Color.Purple: 5,
    Color.Yellow: 6,
    Color.White: 7,
    Color.Gray: 8,
    Color.Grey: 8,
    Color.LightBlue: 9,
    Color.LightGreen: "a",
    Color.LightAqua: "b",
    Color.LightRed: "c",
    Color.LightPurple: "d",
    Color.LightYellow: "e",
    Color.BrightWhite: "f",
}


class Characters:
    all = r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?<>i!lI;:-_+~,"^`". """
    some = r"""@%#*+=-:. """


class Resolutions(Enum):
    """
    The preset resolutions class that contains static variable for usage and transformation.

    Members:
        **Basic** = (50, 25)

        **Medium** = (60, 30)

        **Large** = (100, 50)

        **HD** = (352, 240)
    """
    Basic = (50, 25)
    Medium = (60, 30)
    Large = (100, 50)
    HD = (352, 240)
    Custom = (0, 0)

    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._value_ = args
        return obj

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pixels = width*height

    @staticmethod
    def custom(dimensions: Tuple[int, int]):
        Resolutions.Custom.width = dimensions[0]
        Resolutions.Custom.height = dimensions[1]
        return Resolutions.Custom

class ANSI:
    """
    ANSI control codes for terminal control.
    """
    BEL = "\x07"  # bell
    BS = "\x08"  # backspace
    HT = "\x09"  # horizontal tab
    LF = "\x0A"  # line feed
    VT = "\x0B"  # vertical tab
    FF = "\x0C"  # formfeed
    CR = "\x0D"  # carriage return
    ESC = "\x1B"  # escape char ^[
    CSI = "\x1B["  # Control Sequence Initiator
    WIN_INTERUPT = "\x03"
    RESET = "\x1B[0m"
