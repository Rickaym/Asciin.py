from enum import Enum
from random import randint
from typing import Tuple


class Color(Enum):
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
    def RGB_FOREGROUND(r, g, b):
        return ANSI.CSI + "38;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def RGB_BACKGROUND(r, g, b):
        return ANSI.CSI + "48;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def FORE(r: int, g: int, b: int):
        """
        Colors the foreground with a given RGB value.
        """
        return Color.RGB_FOREGROUND(r, g, b)

    @staticmethod
    def BACK(r: int, g: int, b: int):
        """
        Colors the background with a given RGB value.
        """
        return Color.RGB_BACKGROUND(r, g, b)

    @staticmethod
    def FORErandom():
        """
        Random foreground color.
        """
        return Color.FORE(randint(0, 255), randint(0, 255), randint(0, 255))

    @staticmethod
    def BACKrandom():
        """
        Random backgroun color.
        """
        return Color.BACK(randint(0, 255), randint(0, 255), randint(0, 255))


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
    ramp = r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?<>i!lI;:-_+~,"^`". """
    miniramp = r"""@%#*+=-:. """


class Resolutions(Enum):
    """
    The preset resolutions class that contains static variable for usage and transformation.

    :cvar _50c: (50, 25):
    :cvar _60c: (60, 30):
    :cvar _100c: (100, 50):
    :cvar _240c: (352, 240):
    :cvar _360c: (480, 360):
    :cvar _480c: (858, 480):
    :cvar _720c: (1280, 720):
    :cvar _768c: (1366, 768):
    :cvar _1080c: (1980, 1080):

    :type: Tuple[:class:`int`, :class:`int`]
    """
    Basic =  (50, 25)
    Medium = (60, 30)
    Large = (100, 50)
    HD = (352, 240)
    Custom = (0, 0)

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args
        return obj

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pixels = width*height

    @staticmethod
    def custom(dimensions: Tuple[int, int]):
        Resolutions.Custom._value_ = dimensions
        return Resolutions.Custom

class ANSI:
    # these are intended to be sent to the stdout so they are strings, encode when necessary
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
