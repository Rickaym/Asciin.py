from __future__ import print_function

import platform
import pydoc
import re

from math import e
from functools import wraps
from time import sleep, time
from os import system
from io import StringIO
from contextlib import redirect_stdout

from .values import Characters, Resolutions
from .models import Model
from .rect import Rect
from .globals import SCREENS

try:
    from typing import Callable, Tuple, Union, Optional, Dict, List, Any
except ImportError:
    pass


__all__ = ["Window", "Displayable"]

"""
Use Type comments for backwards compatibility
"""
SIGMOID = lambda x: 1 / (1 + e ** (-x))


class Displayable:
    """
    Defines the integral structure of a console displayable generalized for different OS terminals.

    Subclasses defines specific system calls to open a terminal, resize it, close it, move it and so on..
    """

    TPS = 25

    def __init__(
        self,
        resolution,
        max_framerate,
        forcestop,
        debug,
        show_fps,
        sysdout,
        show_stopwatch,
    ):
        # type: (Resolutions, Optional[int], Optional[int], bool, bool, bool, bool) -> None
        self.resolution = resolution  #: Union[:class:`Resolutions`, Tuple[:class:`int`, :class:`int`]]: A conceptual enum of a the window resolution.
        self.width = resolution.width  #: :class:`int`: The width of the window.
        self.height = resolution.height  #: :class:`int`: The height of the window.
        self.debug_area = [
            0,
            self.resolution.height * 0.8,
        ]  #: Tuple[:class:`int`, :class:`int`]: Approximated area of a debug prompt on the terminal.
        self.max_framerate = max_framerate  #: Optional[:class:`int`]: The specified FPS limit of the window.
        self.goto_ramp = (
            Characters.miniramp
        )  #: List[:class:`str`]: The default list of a characters for test printing and native menu styling.

        self.all_models = (
            {}
        )  #: Dict[:class:`Rect`, :class:`Model`]: A rect to model mapping of every model that the window has a record of presence.

        self.emptyframe = [
            " "
        ] * self.resolution.pixels  #: :class:`str`: A base frame that is drawn over.
        self.show_fps = show_fps  #: :class:`bool`: Whether if the window has a menu indicating the fps.
        self.show_stopwatch = show_stopwatch  #: :class:`bool`: Whether the menu shows the timer before elimination when given.
        self.sysdout = sysdout  #: :class:`bool`: Whether the rendered frames are printed onto the window.

        self.debug = debug  #: :class:`bool`: Whether the window has debug mode enabled.

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
        self._last_frame = self.emptyframe[:]
        self._frame_log = []
        self._fps = 0
        self._session_fps = 0
        self._frames_displayed = 0
        self._started_at = time()
        self._stop_at = forcestop
        self._last_checked = time()

    @property
    def frame(self):
        # type: () -> str
        """
        The current frame of the screen.

        :type: :class:`int`
        """
        return "".join(self._frame)

    @property
    def fps(self):
        # type: () -> int
        """
        The amount of frames rendered per the second passed.

        :type: :class:`int`
        """
        now = time()
        duration = now - self._last_checked
        if duration >= 1:
            self._session_fps += self._frames_displayed
            self._fps = self._frames_displayed
            self._frames_displayed = 0
            self._last_checked = now
        return self._fps

    @property
    def average_fps(self):
        # type: () -> int
        """
        The amount of frames rendered on average from start to present.

        :type: :class:`int`
        """
        return self._session_fps / (time() - self._started_at)

    @property
    def tick(self):
        # type: () -> int
        """
        Internal ticks, from 0 to 25 for timing certain things.

        :type: :class:`int`
        """
        return round(time() - self._started_at) % self.TPS

    def _slice_fit(self, text, point):
        # type: (str, int) -> List[str]
        """
        Simplified implementation of the slice_fit render method to blit window menus and
        native elements.
        """
        if point < 0:
            point = self.resolution.width + point
        return self._frame[:point] + list(text) + self._frame[point + len(text) :]

    def _infograph(self):
        """
        Ensures correct conditions to blit a debug menu at the top of the window.

        This menu is pre-rendered before-hand and the values are formatted
        in to maintain a max slice-fit of one per render.
        """
        args = []
        if self.show_fps:
            args.append(str(self.fps).rjust(4))
        if self.debug:
            args.append("True")
        if args:
            self._frame = self._slice_fit(self._infotext % tuple(args), 0)
        if self._stop_at is not None and self.show_stopwatch:
            self._frame = self._slice_fit(
                "Stopwatch: " + str(self._stop_at - round(time() - self._started_at)),
                20,
            )

    def blit(self, object, *args, **kwargs):
        # type: (Model, Tuple[Any], Dict[str, Any]) -> None
        """
        Simply calls the object's internal blit method onto itself and does necessary
        records.

        :param object:
            The Model to be blitted onto screen.
        :type object: :class:`Model`
        """
        self._frame, object.occupancy = object.blit(self, *args, **kwargs)
        if self.all_models.get(object.rect) is None:
            self.all_models[object.rect] = object

    def refresh(self, log_frames=False):
        # type: (bool) -> None
        """
        Empties the current frame. If sysdout is enabled, it is printed onto the window.

        :param log_frames:
            Whether to keep track of the amount of frames displayed throughout the session.
        :type log_frames: :class:`bool`
        """
        if self._stop_at is not None and time() - self._started_at >= self._stop_at:
            raise RuntimeError("Times up! Program has been force stopped.")

        self._infograph()

        current_frame = "".join(self._frame)
        if self.sysdout:
            print(current_frame, end="\r")

        if log_frames and self._last_frame != current_frame:
            self._frame_log.append(current_frame)
            self._last_frame = current_frame

        self._frames_displayed += 1
        self._frame = self.emptyframe[:]

    def _resize(self):
        """
        Resizes a powershell or a command prompt to the given resolution, this does not actually
        care about the size of the screen - also removes scroll wheel.
        """

    def _new(self):
        """
        Creates an accessible powershell or a command prompt to the given resolution.
        """


class DispWindow(Displayable):
    def _resize(self):
        system(
            "mode con cols=%d lines=%d"
            % (self.resolution.width, self.resolution.height)
        )

    def _new(self):
        pass


class DispLinux(Displayable):
    pass


class DispMacOS(Displayable):
    pass


class Window:
    """
    An abstract representation of a window, the class handles the internal loops for different kinds of uses.
    This isn't the screen parameter passed into the client loop. See Displayable for that.
    """

    platform_to_window = {
        "Windows": DispWindow,
        "Linux": DispLinux,
        "Darwin": DispMacOS,
    }  # type: Dict[str, Displayable]

    def __init__(self, resolution, max_framerate=None):
        # type: (Union[Tuple[int, int], Resolutions], int) -> None
        self.resolution = Resolutions(
            resolution
        )  #: :class:`Resolutions`: The respective resolution of the window.
        # format: off
        self.max_framerate = (
            max_framerate  #: Optional[:class:`int`]: The limiting cap for FPS.
        )

        self._window = None
        self._client_loop = None  # type: Callable
        self._system_loop = None  # type: Callable

        self._stop_time = None

    def _replay_loop(self, win_instance, frames, fps):
        # type: (Displayable, Tuple[List[str]], int) -> None
        """
        A screen manipulation loop written to reply frames submitted with the desired fps.
        Run exactly like the client loop same conditions and fundamentals applies.
        """
        frames = [frame.replace("\n", "", -1) for frame in frames]
        index = 0
        while True:
            win_instance._frame = frames[index]
            index += 1
            if index >= len(frames):
                raise RuntimeError("Replay had run out of frames..")
            win_instance.refresh()
            sleep(60 / (fps * 60))

    def _check_func_sig(self, function):
        # type: (Callable) -> Dict[str, Any]
        """
        Simply checks if the provided function has a single arg to pass the screen parameter into.
        """
        spec = pydoc.render_doc(function)
        signature = re.compile(r"\((?: *)(.*)\)")

        if len(signature.findall(spec)) > 0:
            return True
        else:
            return False

    def loop(self, forcestop=None):
        # type: (Optional[int]) -> Callable[[Displayable], None]
        """
        Basic wrapper to register a game loop onto the screen.

        :returns: (Callable[[:class:`Displayable`], None]) The wrapped function.
        """
        self._stop_time = forcestop

        def wrapper(function):
            # type: (Callable) -> Callable[[Displayable], None]
            wraps(function)
            if self._check_func_sig(function) is False:
                raise TypeError(
                    "you need to accept at least one argument for type Displayable in your loop"
                )

            self._client_loop = function
            return function

        return wrapper

    def replay(self, frames, fps=1):
        # type: (Tuple[List[str]], int) -> None
        """
        Runs the replay loop with the given frames and fps limit.
        """
        global SCREENS

        window = self.platform_to_window[platform.system()]
        win_instance = window(
            self.resolution, self.max_framerate, self._stop_time, False, False, False
        )

        if len(SCREENS) > 1:
            win_instance._new()
        else:
            win_instance._resize()

        SCREENS.append(win_instance)
        self._window = win_instance

        return self._replay_loop(win_instance, frames, fps)

    def run(self, debug=False, show_fps=False, sysdout=True, show_stopwatch=False):
        # type: (bool, bool, bool, bool) -> None
        """
        Runs the client loop that has been defined.
        """
        global SCREENS

        window = self.platform_to_window[platform.system()]
        win_instance = window(
            self.resolution,
            self.max_framerate,
            self._stop_time,
            debug,
            show_fps,
            sysdout,
            show_stopwatch,
        )

        if sysdout:
            if len(SCREENS) > 1:
                win_instance._new()
            else:
                win_instance._resize()
        SCREENS.append(win_instance)
        self._window = win_instance
        return self._client_loop(win_instance)
