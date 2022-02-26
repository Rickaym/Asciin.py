from enum import Enum
from random import randint
from typing import Tuple, Union


class ColorLayer(Enum):
    Foreground = 0
    Background = 1
    Unknown = 2


class Color:
    __slots__ = ("rgb", "layer")

    def __init__(self, r: int, g: int, b: int, layer: ColorLayer=ColorLayer.Unknown) -> None:
        self.rgb = r, g, b
        self.layer = layer

    def ansi(self):
        if self.layer is ColorLayer.Foreground:
            return ANSI.CSI + "38;2;{};{};{}m".format(*self.rgb)
        elif self.layer is ColorLayer.Background:
            return ANSI.CSI + "48;2;{};{};{}m".format(*self.rgb)
        else:
            raise TypeError(f"color layer {self.layer} is invalid")

    def as_layer(self, layer: ColorLayer):
        if layer is ColorLayer.Unknown:
            raise TypeError(f"color layer {self.layer} is invalid")
        else:
            self.layer = layer
            return self

    @staticmethod
    def foreground(r: int, g: int, b: int):
        return Color(r, g, b, ColorLayer.Foreground)

    @staticmethod
    def background(r: int, g: int, b: int):
        return Color(r, g, b, ColorLayer.Background)

    @staticmethod
    def from_hex(hex_int: Union[str, int], layer: ColorLayer):
        if isinstance(hex_int, int):
            hex_str = str(hex(hex_int))[2:].rjust(6, "0")
        else:
            hex_str = hex_int[2:].rjust(6, "0")

        return Color(*(int(hex_str[i : i + 2], 16) for i in (0, 2, 4)), layer=layer)

    @staticmethod
    def foreground_random(grayscale=False):
        """
        Random foreground color.
        """
        if grayscale:
            rgb = (randint(0, 255),) * 3
        else:
            rgb = (randint(0, 255), randint(0, 255), randint(0, 255))

        return Color(*rgb, layer=ColorLayer.Foreground)

    @staticmethod
    def background_random(grayscale=False):
        """
        Random backgroun color.
        """
        if grayscale:
            rgb = (randint(0, 255),) * 3
        else:
            rgb = (randint(0, 255), randint(0, 255), randint(0, 255))

        return Color(*rgb, layer=ColorLayer.Foreground)

    Black: "Color"
    Green: "Color"
    Blue: "Color"
    Aqua: "Color"
    Red: "Color"
    Purple: "Color"
    Yellow: "Color"
    Gray: "Color"
    Grey: "Color"

    LightBlue: "Color"
    LightGreen: "Color"
    LightAqua: "Color"
    LightRed: "Color"
    LightPurple: "Color"
    LightYellow: "Color"

    White: "Color"
    BrightWhite: "Color"


# Preset colors
Color.Black = Color.from_hex(0x000000, ColorLayer.Unknown)
Color.Green = Color.from_hex(0x13A10E, ColorLayer.Unknown)
Color.Blue = Color.from_hex(0x0037DA, ColorLayer.Unknown)
Color.Aqua = Color.from_hex(0x3B78FF, ColorLayer.Unknown)
Color.Red = Color.from_hex(0xC50F1F, ColorLayer.Unknown)
Color.Purple = Color.from_hex(0x881798, ColorLayer.Unknown)
Color.Yellow = Color.from_hex(0xC19C00, ColorLayer.Unknown)
Color.Gray = Color.from_hex(0x767676, ColorLayer.Unknown)
Color.Grey = Color.Gray

Color.LightBlue = Color.from_hex(0x3A96DD, ColorLayer.Unknown)
Color.LightGreen = Color.from_hex(0x16C60C, ColorLayer.Unknown)
Color.LightAqua = Color.from_hex(0x61D6D6, ColorLayer.Unknown)
Color.LightRed = Color.from_hex(0xE74856, ColorLayer.Unknown)
Color.LightPurple = Color.from_hex(0xB4009E, ColorLayer.Unknown)
Color.LightYellow = Color.from_hex(0xF9F1A5, ColorLayer.Unknown)

Color.White = Color.from_hex(0xF2F2F2, ColorLayer.Unknown)
Color.BrightWhite = Color.from_hex(0xFFFFFF, ColorLayer.Unknown)


# A mapping to "identifiers" used for command prompt
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
        self.pixels = width * height

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
