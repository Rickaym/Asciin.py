class Characters:
    ramp = r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?<>i!lI;:-_+~,"^`". """
    miniramp = r"""@%#*+=-:. """


class Resolutions:
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

    _50c = (50, 25)
    _60c = (60, 30)
    _100c = (100, 50)
    _240c = (352, 240)
    _360c = (480, 360)
    _480c = (858, 480)
    _720c = (1280, 720)
    _768c = (1366, 768)
    _1080c = (1980, 1080)

    def __init__(self, val):
        self.value = val
        self.pixels = val[0] * val[1]
        self.width = val[0]
        self.height = val[1]


class ANSI:
    # these are intended to be sent to the stdout so they are strings, encode when necessary
    BEL = "\x07" # bell
    BS = "\x08" # backspace
    HT = "\x09" # horizontal tab
    LF = "\x0A" # line feed
    VT = "\x0B" # vertical tab
    FF = "\x0C" # formfeed
    CR = "\x0D" # carriage return
    ESC = "\x1B" # escape char ^[
    CSI = "\x1B[" # Control Sequence Initiator
    WIN_INTERUPT = "\x03"
    RESET = "\x1B[0m"
