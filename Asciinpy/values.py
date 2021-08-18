from functools import wraps

class ABCEnum:
    """
    Simple enum constructor written for version compatibility
    """
    def __init__(self, cls):
        wraps(cls)
        self.cls = cls
        for attr in self.cls.__dict__:
            value = getattr(self.cls, attr)
            if not isinstance(value, (property)) and not attr.startswith("__"):
                inst = self.cls(value)
                setattr(self.cls, attr, inst)

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)

class Characters:
    ramp = r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?<>i!lI;:-_+~,"^`'. """
    miniramp = r"""@%#*+=-:. """

@ABCEnum
class Resolutions:
    """
    The preset resolutions class that contains static variable for usage and transformation.

    Static-variables
    -----------------
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

    @property
    def width(self):
        # type: () -> int
        """
        The width of the resolution

        :type: :class:`int`
        """
        return self.value[0]

    @property
    def height(self):
        # type: () -> int
        """
        The height of the resolution.

        :type: :class:`int`
        """
        return self.value[1]

    @property
    def pixels(self):
        # type: () -> int
        """
        The sum of pixels present in a resolution configuration.

        :type: :class:`int`
        """
        return self.value[0] * self.value[1]

class ANSI:
    BEL = '\x07' # bell
    BS = '\x08' # backspace
    HT = '\x09' # horizontal tab
    LF = '\x0A' # line feed
    VT = '\x0B' # vertical tab
    FF = '\x0C' # formfeed
    CR = '\x0D' # carriage return
    ESC = '\x1B' # escape char ^[
    CSI = ESC+'[' # Control Sequence Initiator