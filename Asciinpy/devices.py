import io
import sys

from typing import Optional
from threading import Thread

from .utils import deprecated
from .events import ON_KEY_PRESS
from .values import ANSI


class RawMouseInput:
    pass


class RawKeyInput:
    # these buffers only allow one sequential occupation any given time
    cmd_buffer: Optional[io.BytesIO] = None  # keeps track of any escape sequences
    line_buffer: Optional[
        io.BytesIO
    ] = None  # keeps track of a record until return is pressed

    @staticmethod
    def is_alphanumeric(bytes):
        denary_val = int.from_bytes(bytes, byteorder=sys.byteorder)
        if denary_val < 65 or denary_val > 122:
            return False
        return True

    def _pick_getch():
        r"""
        Getch gets us a key press focused in the console, since python doesn't have a default method for that
        nor an OS independent one for that matter, we will have to make the getch method based on the OS.
        """
        try:
            import termios
        except ImportError:  # windows machine
            import msvcrt

            def _getch():
                key = None
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                return key

        else:
            import tty

            def _getch():
                fd = sys.stdin.fileno()  # usually 0 but whatever
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch

        return _getch

    def _filter(getch_method):
        r"""
        Wraps the getch method with necessary buffering
        """

        def wrapper(*args, **kwargs):
            ch = getch_method(*args, **kwargs)
            if ch is None:
                return

            if ch == ANSI.WIN_INTERUPT.encode():
                raise KeyboardInterrupt

            if RawKeyInput.cmd_buffer is not None:
                past = RawKeyInput.cmd_buffer.getvalue()
                RawKeyInput.cmd_buffer = None
                return past + ch
            elif not RawKeyInput.is_alphanumeric(ch):  # must be some escape sequence
                if RawKeyInput.cmd_buffer is None:
                    RawKeyInput.cmd_buffer = io.BytesIO()
                    RawKeyInput.cmd_buffer.write(ch)
                return

            if RawKeyInput.line_buffer is not None:
                past = RawKeyInput.line_buffer.getvalue()
                RawKeyInput.line_buffer.write(ch)
                if ch in ("\n".encode(), "\r".encode()):
                    l_buf = RawKeyInput.line_buffer.getvalue()
                    RawKeyInput.line_buffer = None
                    return l_buf
            elif RawKeyInput.line_buffer is None:  # start a line buffer
                RawKeyInput.line_buffer = io.BytesIO()
                RawKeyInput.line_buffer.write(ch)
            return ch

        return wrapper

    getch = _filter(_pick_getch())  # final getch product


class Keyboard:
    # is_pressed and is_released are universal flags under `Keyboard` but they exist as a flag
    # under each `Key`
    last_pressed = None
    is_pressed = False
    pressed = None

    _thread = None

    def change_flag(getch_method):
        def wrapped(*args, **kwargs):
            ch = getch_method(*args, **kwargs)
            if ch is not None:
                Keyboard.pressed = ch
                Keyboard.last_pressed = ch
                Keyboard.is_pressed = True
                ON_KEY_PRESS.emit(Keyboard.pressed)
            else:
                Keyboard.pressed = None
                Keyboard.is_pressed = False
            return ch

        return wrapped

    # wraps the raw input getch method
    getch = change_flag(RawKeyInput.getch)

    @deprecated
    def start_backend():
        # backend doesn't stay sync with the main caller loop
        # that can be problamatic
        def loop():
            while True:
                Keyboard.getch()

        Keyboard._thread = Thread(target=loop)
        Keyboard._thread.start()

    # the general byte representation of each keys
    class Keys:
        B_ZERO = b"\x00" # 0
        B_TTF = b"\xe0" # 224

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
        ZERO = b"0"
        ONE = b"1"
        TWO = b"2"
        THREE = b"3"
        FOUR = b"4"
        FIVE = b"5"
        SIX = b"6"
        SEVEN = b"7"
        EIGHT = b"8"
        NINE = b"9"
        SPACE = b"  "
        MINUS = b"-"
        PLUS = b"+"
        EQUAL = b"="
        UNDERSCORE = b"_"
        RIGHT_BRACKET = b"("
        LEFT_BRACKET = b")"
        SQUARE_RIGHT_BRACKET = b"["
        SQUARE_LEFT_BRACKET = b"]"
        WIGGLY_RIGHT_BRACKET = b"{"
        WIGGLY_LEFT_BRACKET = b"}"
        RIGHT_ANGLE_BRACKET = b"<"
        LEFT_ANGLE_BRACKET = b">"
        FORWARD_SLASH = b"/"
        BACKWARD_SLASH = b"\\"
        PIPE = b"|"
        SINGLE_QUOTE = b"'"
        DOUBLE_QUOTE = b'"'
        COLON = b":"
        SEMI_COLON = b";"
        PERIOD = b"."
        COMMA = b","
        QUESTION_MARK = b"?"
        AND = b"&"
        PERCENT = b"%"
        HASH = b"#"
        EXCLM = b"!"
        F1 = B_ZERO + b";"
        F2 = B_ZERO + b"<"
        F3 = B_ZERO + b"="
        F4 = B_ZERO + b">"
        F5 = B_ZERO + b"?"
        F6 = B_ZERO + b"@"
        F7 = B_ZERO + b"A"
        F8 = B_ZERO + b"B"
        F9 = B_ZERO + b"C"
        F10 = B_ZERO + b"D"
        F11 = B_TTF + b"\x85"
        F12 = B_TTF + b"\x86"
        HOME = B_TTF + b"G"
        UP_ARROW = B_TTF + b"H"
        PAGE_UP = B_TTF + b"I"
        LEFT_ARROW = B_TTF + b"K"
        RIGHT_ARROW = B_TTF + b"M"
        END = B_TTF + b"O"
        DOWN_ARROW = B_TTF + b"P"
        PAGE_DOWN = B_TTF + b"Q"
        INSERT = B_TTF + b"R"
        DELETE = B_TTF + b"S"
        PRT_SCR = "UNDEFINED-1"
        BREAK = "UNDEFINED-2"
        BACKSPACE = b"\x08"
        RETURN = b"\n"
        TAB = b"\t"
        NULL = ZERO + b"\x03"


class Microphone:
    pass


class Audio:
    pass


class Mouse:
    pass

