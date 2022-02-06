import sys

from io import BytesIO
from typing import Callable, Optional
from enum import Enum

from Asciinpy.globals import Platform

from .utils import praised
from .events import ON_KEY_PRESS, ON_KEY_RELEASE
from .values import ANSI

CharacterGetter = Callable[[], Optional[bytes]]


@praised("0.4.0")
class RawMouseInput:
    pass


class RawKeyInput:
    """
    A raw key buffer before it gets filtered into the main keyboard class.
    """

    cmd_buffer: Optional[BytesIO] = None  # keeps track of any escape sequences
    line_buffer: Optional[
        BytesIO
    ] = None  # keeps track of a record until return is pressed


def is_alphanumeric(bytes):
    denary_val = int.from_bytes(bytes, byteorder=sys.byteorder)
    if (denary_val < 32 or denary_val > 126) and denary_val != 10:
        return False
    return True


def get_getch() -> CharacterGetter:
    """
    Getch gets us a key press focused in the console, since python doesn't have a default method for that
    nor an OS independent one for that matter, we will have to make the getch method based on the OS.
    """
    if Platform.is_window:
        # Windows machine
        import msvcrt

        def _win_getch():
            key = None
            if msvcrt.kbhit():
                key = msvcrt.getch()
            return key

        return _win_getch
    else:
        import termios
        import tty

        def _unix_getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)  # type: ignore
            try:
                tty.setraw(fd)  # type: ignore
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # type: ignore
            return ch.encode()

        return _unix_getch


def warp_buffer_getch(getch_method: Callable):
    """
    Wraps the getch method with necessary buffering
    """
    def wrapped(*args, **kwargs) -> Optional[bytes]:
        ch = getch_method(*args, **kwargs)
        if ch is None:
            return

        if ch == ANSI.WIN_INTERUPT.encode():
            raise KeyboardInterrupt

        if RawKeyInput.cmd_buffer is not None:
            past = RawKeyInput.cmd_buffer.getvalue()
            RawKeyInput.cmd_buffer = None
            try:
                return past+ch
            except:
                raise RuntimeError(past + ch)
        elif not is_alphanumeric(ch):
            if RawKeyInput.cmd_buffer is None:
                RawKeyInput.cmd_buffer = BytesIO()
                RawKeyInput.cmd_buffer.write(ch)
            return

        if RawKeyInput.line_buffer is not None:
            past = RawKeyInput.line_buffer.getvalue()
            RawKeyInput.line_buffer.write(ch)
            if ch in b"\n\r":
                l_buf = RawKeyInput.line_buffer.getvalue()
                RawKeyInput.line_buffer = None
                return l_buf
        elif RawKeyInput.line_buffer is None:  # start a line buffer
            RawKeyInput.line_buffer = BytesIO()
            RawKeyInput.line_buffer.write(ch)

        return ch

    return wrapped


class Keyboard:
    # is_pressed and is_released are universal flags under `Keyboard` but they exist as a flag
    # under each `Key`
    is_pressed = False
    pressed = None
    _thread = None
    _getch = warp_buffer_getch(get_getch())

    @staticmethod
    def getch(*args, **kwargs):
        ch = Keyboard._getch(*args, **kwargs)

        if ch is not None:
            Keyboard.pressed = Keyboard.Keys._value2member_map_.get(ch, Keyboard.Keys.NullByte)
            Keyboard.is_pressed = True
            ON_KEY_PRESS.emit(Keyboard.pressed)
        else:
            if Keyboard.is_pressed:
                ON_KEY_RELEASE.emit(Keyboard.pressed)
            Keyboard.pressed = None
            Keyboard.is_pressed = False
        return Keyboard.pressed

    class Keys(Enum):
        # the general byte representation of each keys
        A = b"a"
        B = b"b"
        C = b"c"
        D = b"d"
        E = b"e"
        F = b"f"
        G = b"g"
        H = b"h"
        I = b"i"
        J = b"j"
        K = b"k"
        L = b"l"
        M = b"m"
        N = b"n"
        O = b"o"
        P = b"p"
        Q = b"q"
        R = b"r"
        S = b"s"
        T = b"t"
        U = b"u"
        V = b"v"
        W = b"w"
        X = b"x"
        Y = b"y"
        Z = b"z"
        Zero = b"0"
        One = b"1"
        Two = b"2"
        Three = b"3"
        Four = b"4"
        Five = b"5"
        Six = b"6"
        Seven = b"7"
        Eight = b"8"
        Nine = b"9"
        Space = b"  "
        Minus = b"-"
        Plus = b"+"
        Equal = b"="
        Underscore = b"_"
        RightBracket = b"("
        LeftBracket = b")"
        SquareRightBracket = b"["
        SquareLeftBracket = b"]"
        WigglyRightBracket = b"{"
        WigglyLeftBracket = b"}"
        RightAngleBracket = b"<"
        LeftAngleBracket = b">"
        ForwardSlash = b"/"
        BackwardSlash = b"\\"
        Pipe = b"|"
        SingleQuote = b"'"
        DoubleQuote = b'"'
        Colon = b":"
        SemiColon = b";"
        Period = b"."
        Comma = b","
        QuestionMark = b"?"
        And = b"&"
        Percent = b"%"
        Hash = b"#"
        Exclaim = b"!"
        NullByte = b"\x00"  # 0
        TTF = b"\xe0"  # 224
        F1 = NullByte + b";"
        F2 = NullByte + b"<"
        F3 = NullByte + b"="
        F4 = NullByte + b">"
        F5 = NullByte + b"?"
        F6 = NullByte + b"@"
        F7 = NullByte + b"A"
        F8 = NullByte + b"B"
        F9 = NullByte + b"C"
        F10 = NullByte + b"D"
        F11 = TTF + b"\x85"
        F12 = TTF + b"\x86"
        UpArrow = TTF + b"H"
        LeftArrow = TTF + b"K"
        RightArrow = TTF + b"M"
        DownArrow = TTF + b"P"
        PageUp = TTF + b"I"
        PageDown = TTF + b"Q"
        Tab = b"\t"
        Return = b"\r\r"
        Home = TTF + b"G"
        End = TTF + b"O"
        Backspace = b"\x08"
        Insert = TTF + b"R"
        Delete = TTF + b"S"
        PrtScr = "UNDEFINED-1"
        Break = "UNDEFINED-2"


@praised("0.4.0")
class Microphone:
    pass


@praised("0.4.0")
class Audio:
    pass


@praised("0.4.0")
class Mouse:
    class Keys(Enum):
        Left = 0
        Right = 1
        Scroll = 2