from __future__ import print_function, division

import os
import signal

from math import tan
import sys
from time import sleep, time
from functools import partial

from .values import Characters, Resolutions, ANSI
from .geometry import roundi

try:
    from typing import Callable, Tuple, Union, Optional, Dict, List, Any
except ImportError:
    pass


__all__ = ["Window", "Screen"]


class Color:
    def FOREGROUND(id): return ANSI.CSI + "38;5;{}m".format(id)
    def BACKGROUND(id): return ANSI.CSI + "48;5;{}m".format(id)

    @staticmethod
    def RGB_FOREGROUND(r, g, b): return ANSI.CSI + \
        "38;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def RGB_BACKGROUND(r, g, b): return ANSI.CSI + \
        "48;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def FORE(r, g, b):
        return Color.RGB_FOREGROUND(r, g, b)

    @staticmethod
    def BACK(r, g, b):
        return Color.RGB_BACKGROUND(r, g, b)


class Screen:
    """
    Defines the integral structure of a console screen generalized for different OS terminals.

    Subclasses defines specific system calls to open a terminal, resize it, close it, move it and so on..
    You shalln't make instances of this class or it's subclasses.
    """

    TPS = 25

    def __init__(
        self,
        resolution,
        fps_limiter,
        forcestop,
        fov,
        debug,
        show_fps,
        sysdout,
        timer,
    ):
        # type: (Resolutions, int, int, float, bool, bool, bool, bool) -> None
        self.resolution = resolution #: :class:`Resolutions`: A conceptual enum of a the window resolution.
        self.width = resolution.width #: :class:`int`: The width of the window.
        self.height = resolution.height #: :class:`int`: The height of the window.

        self.debug_area = [
            0,
            self.resolution.height * 0.8,
        ]  #: Tuple[:class:`int`, :class:`int`]: Approximated area of a debug prompt on the terminal.
        self.fps_limiter = fps_limiter #: Optional[:class:`int`]: The specified FPS limit of the window.
        self.palette = (
            Characters.miniramp
        )  #: List[:class:`str`]: The default list of a characters for test printing and native menu styling. Any changes to it must be in references to the valid :class:`Characters` texture list.

        self.fov = fov  #: :class:`float`: Fov of the current screen, must be in radians for 3D applicaions
        self.aspect_ratio = resolution.height / resolution.width
        self.emptyframe = [" "] * (
            self.resolution.pixels
        )  # : List[:class:`str`]: A base frame with nothing on it.

        self.show_fps = show_fps #: :class:`bool`: Whether if the window has a menu indicating the fps.
        self.timer = timer #: :class:`bool`: Whether the menu shows the timer before elimination when given.
        self.sysdout = sysdout #: :class:`bool`: Whether the rendered frames are printed onto the window.
        self.debug = debug #: :class:`bool`: Whether the window has debug mode enabled.

        # pre-rendered
        self._infotext = (
            self.palette[2] + (r" " * (resolution.width-2)) + self.palette[2] +
            self.palette[2] + (self.palette[2] * (resolution.width-2)) + self.palette[2]
        )
        if self.show_fps is True:
            inf = r"FPS: [%s]"
            fps_size = len(inf) + 3
            self._infotext = self._infotext[:3] + inf + self._infotext[3+fps_size:]
        if timer is True:
            watch = r"StopWatch: %s  "
            offs = 5
            self._infotext = self._infotext[:3+fps_size+offs] + watch + self._infotext[3+fps_size+offs+len(watch):]

        self._fov = 1 / tan(fov * 0.5)
        self._frame = self.emptyframe[:]
        self._last_frame = self.emptyframe[:]
        self._frame_log = []
        self._fps = 0
        self._session_fps = 0
        self._frames_displayed = 0
        self._stop_at = forcestop
        self._started_at = time()
        self._last_checked = time()

    @property
    def frame(self):
        # type: () -> str
        """
        The current frame rendered.

        :type: :class:`str`
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
        return roundi(time() - self._started_at) % self.TPS

    @staticmethod
    def _puts(*sequence):
        # type: (List[str]) -> None
        """
        Writes out sys stdout directly in bytes
        """
        os.write(1, "".join(sequence).encode())

    def _slice_fit(self, text, point):
        # type: (str, int) -> List[str]
        """
        Simplified implementation of the slice_fit render method to blit window menus and
        native elements.
        """
        if point < 0:
            point = self.resolution.width + point
        return self._frame[:point] + list(text) + self._frame[point + len(text):]

    def _infograph(self):
        """
        Ensures correct conditions to blit a debug menu at the top of the window.

        This menu is pre-rendered before-hand and the values are formatted
        in to maintain a max slice-fit of one per render.
        """
        if self.show_fps:
            self._frame = self._slice_fit(
                self._infotext % str(self.fps).rjust(5), 0)

    def _resize(self):
        """
        Abstract method in resizing a powershell or a command prompt to the given resolution, this does not actually
        care about the size of the screen - also removes scroll wheel.
        """

    def _new(self):
        """
        Creates an accessible powershell or a command prompt to the given resolution.
        """

    @staticmethod
    def _clear():
        """
        Clears the current visible terminal
        """
        Screen._puts(ANSI.CSI, "2J")

    @staticmethod
    def _cursor(goto=None, visibility=None):
        if goto is not None:
            Screen._puts(ANSI.CSI, "%d;%dH" % goto)
        if visibility is not None:
            if visibility is True:
                Screen._puts(ANSI.CSI, "?25h")
            else:
                Screen._puts(ANSI.CSI, "?25l")

    def to_distance(self, coordinate):
        return roundi(coordinate[0]) + (roundi(coordinate[1]) * self.width) - 1

    def blit(self, object, *args, **kwargs):
        # type: (object, Tuple[Any], Dict[str, Any]) -> None
        """
        Simply calls the object's internal blit method onto itself and does necessary
        records.

        :param object:
            The Model to be blitted onto screen.
        :type object: :class:`Model`
        """
        self._frame, object.occupancy = object.blit(self, *args, **kwargs)

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

        current_frame = self.frame
        if self.sysdout:
            Screen._cursor((0, 0))
            Screen._puts(current_frame)

        if log_frames and self._last_frame != current_frame:
            self._frame_log.append(current_frame)
            self._last_frame = current_frame

        self._frames_displayed += 1
        self._frame = self.emptyframe[:]


class WindowsControl(Screen):
    def _resize(self):
        os.system(
            "mode con cols={} lines={}".format(
                self.resolution.width, self.resolution.height
            )
        )

    def _new(self, mode):
        frame = list(sys._current_frames().values())[0]

        # searches the origin of a call up to depth of 5
        # this is more than necessary
        for i in range(5):
            if getattr(frame, "f_back") is None:
                caller = frame.f_globals["__file__"]
            else:
                frame = frame.f_back

        os.system("""start cmd /{} py {}""".format(mode, caller))

class UnixControl(Screen):
    def _resize(self):
        os.system(
            "printf '\e[8;{};{}t'".format(
                self.resolution.height, self.resolution.width)
        )

    def _new(self):
        pass

class Window:
    """
    An abstract representation of a window, the class handles the internal loops for different kinds of uses.
    """

    ON_TERMINATE = "on_terminate"
    ON_START = "on_start"
    ON_RESIZE = "on_resize"

    PNAME = "ASCIINPY_PROCESS"

    platform_to_window = {
        "nt" : WindowsControl,
        "posix": UnixControl,
    }  # type: Dict[str, Screen]

    def __init__(self, resolution, fps_limiter=None):
        # type: (Union[Tuple[int, int], Resolutions], int) -> None
        self.resolution = Resolutions(
            resolution
        )  #: :class:`Resolutions`: The respective resolution of the window.
        self.fps_limiter = fps_limiter #: Optional[:class:`int`]: A simple FPS lock.

        self._screen = None
        self._client_loop = None
        self._stop_time = None
        self._debug = False
        self._new_win_mode = None

        self._event_handlers = {self.ON_TERMINATE: [], self.ON_START: [], self.ON_RESIZE: []}

        signal.signal(signal.SIGINT, self._terminate)
        signal.signal(signal.SIGTERM, self._terminate)

        # more available unix signals for termination and terminal resize
        if os.name == "posix":
            signal.signal(signal.SIGKILL, self._terminate)
            signal.signal(signal.SIGWINCH, partial(self._emit, self, self.ON_RESIZE))

    def _emit(self, event):
        for handlers in self._event_handlers[event]:
            handlers()

    def _replay_loop(self, win_instance, frames, fps):
        # type: (Screen, Tuple[List[str]], int) -> None
        """
        A screen manipulation loop written to reply frames submitted with the desired fps.

        Runs exactly like the client loop, same conditions and fundamentals applies.
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

    def _terminate(self, *traces):
        self._emit(self.ON_TERMINATE)

        # send cursor home and
        Screen._puts(ANSI.BEL)
        Screen._cursor((0, 0), visibility=True)
        Screen._puts(ANSI.RESET)
        Screen._clear()

        raise RuntimeError(traces)

    def enable_debug(self, mode="k"):
        # type: (str) -> None
        """
        Enables debug mode for developers.

        Modes:
            k - Executes the application until interrupted but remains open
            c - Executes the application until interrupted then closes

        - Offloads program onto a subprocess on an external Terminal with the given mode
        - (TODO) Creates another subprocess on a different Terminal for error catching, logging etc..
        """
        self._debug = True
        self._new_win_mode = mode

    def listen(self, event):
        # type: (str) -> None
        """
        Registers possible types of signals emitted by the window and the subprocesses.
        """
        def wrapper(func):
            self._event_handlers[event].append(func)
            return func
        return wrapper

    def loop(self, forcestop=None):
        # type: (Optional[int]) -> Callable[[Screen], None]
        """
        Basic wrapper to register a game loop onto the screen.

        :returns: (Callable[[:class:`Screen`], None]) The wrapped function.
        """
        self._stop_time = forcestop

        def wrapper(function):
            # type: (Callable) -> Callable[[Screen], None]
            self._client_loop = function
            return function

        return wrapper

    def replay(self, frames, fps=1):
        # type: (Tuple[List[str]], int) -> None
        """
        Runs the replay loop with the given frames and fps limit.
        """
        window = self.platform_to_window[os.name]
        win_instance = window(
            self.resolution, self.fps_limiter, self._stop_time, False, False, False
        )
        win_instance._resize()
        self._screen = win_instance

        return self._replay_loop(win_instance, frames, fps)

    def set_title(self, title):
        # type: (str) -> None
        """
        Broken in non-unix machines.
        """
        if os.name != "nt":
            Screen._puts(ANSI.ESC, "]2;{}".format(title))

    def run(
        self, fov=1.570796327, show_fps=False, sysdout=True, timer=False
    ):
        # type: (int, bool, bool, bool) -> None
        """
        Runs the client loop that has been defined.
        """
        window = self.platform_to_window[os.name]
        self._screen = window(
            self.resolution,
            self.fps_limiter,
            self._stop_time,
            fov,
            self._debug,
            show_fps,
            sysdout,
            timer,
        )
        if self._debug is True:
            if os.getenv(self.PNAME) != "child":
                os.environ[self.PNAME] = "child"
                self._screen._new(self._new_win_mode)
                return
            else:
                del os.environ[self.PNAME]

        if sysdout is True:
            self._screen._resize()

        Screen._clear()
        Screen._cursor(visibility=False)

        self._emit(self.ON_START)
        return self._client_loop(self._screen)
