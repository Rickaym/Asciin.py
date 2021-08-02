from __future__ import print_function

import platform

from math import e
from time import time
from os import system

from .values import Characters, Resolutions
from .models import Model
from .rect import Rect
from .globals import SCREENS
from .methods.renders import slice_fit

try:
    from typing import Callable, Tuple, Union, Optional, Dict
except ImportError:
    pass

"""
Use Type comments for backwards compatibility
"""
SIGMOID = lambda x: 1 / (1 + e ** (-x))


class Displayable:
    """
    An abstract class that gives general methods to different OS terminal windows base methods.

    Subclasses must define OS specific system calls to open a terminal, resize it, close it, move it and so on..

    Attributes
    ===========
        resolution (Resolutions): an enum of a window resolution

        debug_area (Tuple[int, int]): approximated area of a debug prompt on the terminal

        max_framerate (Optional[int]): FPS limit

        goto_ramp (List[str]): default list of a characters for test printing and debug styling

        all_models (Dict[Rect, Model]): a rect to model mapping of every model blitted

        emptyframe (str): a base frame used to blit things over when rendering - there is very little reason for it to be changed

        show_fps (bool): shows the FPS in a debug menu when True

        debug (Optional[bool]): enables supervised printing when True

    """

    TPS = 25

    def __init__(self, resolution, max_framerate, forcestop, debug, show_fps):
        # type: (Resolutions, Optional[int], Optional[int], bool, bool) -> None
        self.resolution = resolution
        self.debug_area = [0, self.resolution.height * 0.8]
        self.max_framerate = max_framerate
        self.goto_ramp = Characters.miniramp.value
        self.all_models = {}  # type: Dict[Rect, Model]
        self.emptyframe = [" "] * self.resolution.pixels
        self.show_fps = show_fps
        self.debug = debug

        # pre-rendered
        self._infotext = (
            "||"
            + (
                " FPS: [%s]" + " " * (resolution.width - 28)
                if show_fps is True
                else " " * (resolution.width - 16)
            )
            + ("Debug: %s " if debug is True else " " * 12)
            + "||"
            + "".join((r"\\", "=" * (resolution.width - 4), r"//"))
        )
        # the distro_function is used for test printing color gradients with the default ramp
        g = len(self.goto_ramp) * resolution.height
        self._distro_function = lambda x: g * x
        # supervised print log
        self._temp_log = [""] * 6
        self._DEBUG_BOX = (
            "/" * self.resolution.width
            + " " * self.resolution.width * 4
            + "/" * self.resolution.width
        )
        self._frame = self.emptyframe[:]
        self._fps = 0
        self._frames_displayed = 0
        self._started_at = time()
        self._stop_at = forcestop
        self._last_checked = time()

    @property
    def frame(self):
        # type: () -> str
        """
        The current frame of the screen do not fiddle with it, please.
        """
        return "".join(self._frame)

    @property
    def fps(self):
        """
        The amount of frames rendered per second.
        """
        # type: () -> int
        now = time()
        duration = now - self._last_checked
        if duration >= 1:
            self._fps = self._frames_displayed
            self._frames_displayed = 0
            self._last_checked = now
        return self._fps

    @property
    def tick(self):
        """
        Internal ticks, from 0 to 25 for tracking usage.
        """
        # type: () -> int
        return round(time() - self._started_at) % self.TPS

    def slice_fit(self, text, point):
        """
        Fits text onto the current frame.

        Time Complexity: O(n) where n is len(TEXT)
        """
        if point < 0:
            point = self.resolution.width + point
        return self._frame[:point] + list(text) + self._frame[point + len(text) :]

    def _infograph(self):
        """
        Slice-fits a debug menu at the top of the window and inserts appropriate
        details.

        This menu is pre-rendered before-hand and the values are formatted
        in to maintain a max slice-fit of one per render.
        """
        args = []
        if self.show_fps:
            args.append(str(self.fps).rjust(4))
        if self.debug:
            args.append("True")
        if args:
            self._frame = self.slice_fit(self._infotext % tuple(args), 0)
        if self._stop_at is not None:
            self._frame = self.slice_fit(
                "Stopwatch: " + str(self._stop_at - round(time() - self._started_at)),
                20,
            )
            if time() - self._started_at >= self._stop_at:
                raise RuntimeError("Times up! Program has been force stoppe.")

    def blit(self, object, *args, **kwargs):
        # type: (Model, Optional[Tuple[int, int]], bool) -> None
        """
        Simply calls the object's inner blit method onto itself and does necessary
        records.
        """
        self._frame = object.blit(self, *args, **kwargs)
        if self.all_models.get(object.rect) is None:
            self.all_models[object.rect] = object

    def refresh(self):
        self._infograph()
        self._frames_displayed += 1
        print("".join(self._frame), end="\r")

        self._frame = self.emptyframe[:]

    def _test_print(self):
        frame = r""""""

        def change_frm(_frame):
            global frame
            frame = _frame

        [
            [
                change_frm(
                    (
                        lambda: frame
                        + self.goto_ramp[round(self._distro_function(row)) - 1]
                    )()
                )
                for c in range(self.resolution.width)
            ]
            for row in range(self.resolution.height)
        ]
        self._frame = frame

    def _resize(self):
        pass

    def _new(self):
        pass


class WinWindow(Displayable):
    def _resize(self):
        """
        Resizes a powershell or a command prompt to the given resolution, this does not actually
        care about the size of the screen - also removes scroll wheel.
        """
        system(
            "mode con cols=%d lines=%d"
            % (self.resolution.width, self.resolution.height)
        )

    def _new(self):
        """
        Creates an accessible powershell or a command prompt to the given resolution.
        """
        pass


class WinLinux(Displayable):
    pass


class WinMacOS(Displayable):
    pass


class Screen:
    platform_to_window = {"Windows": WinWindow, "Linux": WinLinux, "Darwin": WinMacOS}

    def __init__(self, resolution, max_framerate=None):
        # type: (Union[Tuple[int, int], Resolutions], int) -> None
        """
        An abstract representation of a screen or window, this class is intentionally limited so that
        the only way to access the real window is by gouging the Displayable parameter in a loop.

        Attributes
        ===========
            max_framerate (Optional[int]): framerate cap
        """
        self.max_framerate = max_framerate

        self._client_loop = None  # type: Callable
        self._system_loop = None  # type: Callable

        self._resolution = resolution
        self._stop_time = None

    @property
    def resolution(self):
        return self._resolution

    def loop(self, forcestop=None):
        # type: (Optional[int]) -> Callable[[Displayable], None]
        """
        Basic wrapper to register a game loop to the screen.

        Args:
            forcestop (Optional[int]): Time duration in seconds to stop the loop function. Defaults to None and runs until the function is exhausted.
        """
        self._stop_time = forcestop

        def wrapper(function):
            # type: (Callable) -> Callable
            self._client_loop = function

            return function

        return wrapper

    def run(self, debug=False, show_fps=False):
        # type: (bool, bool) -> None
        global SCREENS
        window = self.platform_to_window[platform.system()]
        win_instance = window(
            self._resolution, self.max_framerate, self._stop_time, debug, show_fps
        )

        if len(SCREENS) > 1:
            win_instance._new()
        else:
            win_instance._resize()

        SCREENS.append(win_instance)
        self._client_loop(win_instance)
