import os
import sys

from typing import Callable, Literal, Tuple, Union, Optional, Dict, List, Any
from abc import ABC, abstractmethod

from math import tan
from time import sleep, time

from .values import Characters, Resolutions, ANSI
from .devices import Keyboard
from .events import ON_START, Event, EventListener


__all__ = ["Window", "Screen"]

Displayer = Callable[["Screen"], None]


class Screen(ABC):
    """
    A context Abstract class for the console screen.
    Unix and NT machines subclasses this class into two children classes that implements
    `_new` and `_resize` differently.
    """

    palette = Characters.miniramp
    TPS = 25

    __slots__ = (
        "resolution",
        "width",
        "height",
        "max_fps",
        "fov",
        "aspect_ratio",
        "emptyframe",
        "show_fps",
        "timer",
        "sysdout",
        "debug",
        "_infotext",
        "_fov",
        "_frame",
        "_last_frame",
        "_records",
        "_fps",
        "_average_fps",
        "_frames_displayed",
        "_stops_at",
        "_started_at",
        "_last_fps_measure",
    )

    def __init__(
        self,
        resolution: Resolutions,
        max_fps: Optional[int],
        forcestop: Optional[int],
        fov: Optional[int],
        debug: bool,
        show_fps: bool,
        sysdout: bool,
        timer: bool,
    ):
        self.resolution = resolution
        self.width, self.height = resolution.value

        self.fov = fov
        self.max_fps = max_fps
        self.aspect_ratio = resolution.height / resolution.width
        self.emptyframe = [" "] * (self.resolution.pixels)
        self.show_fps = show_fps
        self.timer = timer
        self.sysdout = sysdout
        self.debug = debug

        # pre-rendered
        self._infotext = (
            self.palette[2]
            + (r" " * (resolution.width - 2))
            + self.palette[2]
            + self.palette[2]
            + (self.palette[2] * (resolution.width - 2))
            + self.palette[2]
        )
        self._last_frame = self.emptyframe[:]
        self._frame = self.emptyframe[:]
        self._records = []

        self._fps = 0
        self._average_fps = 0
        self._frames_displayed = 0
        if fov is not None:
            self._fov = 1 / tan(fov * 0.5)

        self._started_at = time()
        self._stops_at = forcestop
        self._last_fps_measure = time()

        if show_fps is True:
            inf = r"FPS: [%s]"
            fps_size = len(inf) + 3
            self._infotext = self._infotext[:3] + inf + self._infotext[3 + fps_size :]
        if timer is True:
            watch = r"StopWatch: %s  "
            offs = 5
            self._infotext = (
                self._infotext[: 3 + fps_size + offs]
                + watch
                + self._infotext[3 + fps_size + offs + len(watch) :]
            )

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
        duration = now - self._last_fps_measure
        if duration >= 1:
            self._average_fps += self._frames_displayed
            self._fps = self._frames_displayed
            self._frames_displayed = 0
            self._last_fps_measure = now
        return self._fps

    @property
    def average_fps(self):
        # type: () -> int
        """
        The amount of frames rendered on average from start to present.

        :type: :class:`int`
        """
        return self._average_fps / (time() - self._started_at)

    @property
    def tick(self):
        # type: () -> int
        """
        Internal ticks, from 0 to 25 for timing certain things.

        :type: :class:`int`
        """
        return round(time() - self._started_at) % self.TPS

    @staticmethod
    def _puts(*sequence: List[str]):
        r"""
        Writes out sys stdout directly in bytes
        """
        os.write(1, "".join(sequence).encode())

    def _slice_fit(self, text: str, point: int):
        # type: (str, int) -> List[str]
        r"""
        Simplified implementation of the slice_fit render method to blit window menus and
        native elements.
        """
        if point < 0:
            point = self.resolution.width + point
        return self._frame[:point] + list(text) + self._frame[point + len(text) :]

    def _infograph(self):
        r"""
        Ensures correct conditions to blit a debug menu at the top of the window.

        This menu is pre-rendered before-hand and the values are formatted
        in to maintain a max slice-fit of one per render.
        """
        if self.show_fps:
            self._frame = self._slice_fit(self._infotext % str(self.fps).rjust(5), 0)

    @abstractmethod
    def _resize(self):
        """
        Abstract method in resizing a powershell or a command prompt to the given resolution, this does not actually
        care about the size of the screen - also removes scroll wheel.
        """

    @abstractmethod
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

    def _to_distance(self, x, y):
        return round(x) + (round(y) * self.width)

    def _to_coordinate(self, distance):
        return divmod(distance, self.width)[::-1]

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
        if self._stops_at is not None and time() - self._started_at >= self._stops_at:
            raise RuntimeError("Times up! Program has been force stopped.")

        Keyboard.getch()
        self._infograph()

        current_frame = self.frame
        if self.sysdout:
            Screen._cursor((0, 0))
            Screen._puts(current_frame)
        if log_frames and self._last_frame != current_frame:
            self._records.append(current_frame)
            self._last_frame = current_frame

        self._frames_displayed += 1
        self._frame = self.emptyframe[:]


class WindowsControl(Screen):
    def _resize(self):
        os.system(
            f"mode con cols={self.resolution.width} lines={self.resolution.height}"
        )

    def _new(self, mode: Literal["k", "c"], origin_depth: int):
        frame = list(sys._current_frames().values())[0]

        # Searches the origin of a call
        for i in range(origin_depth):
            if getattr(frame, "f_back") is None:
                caller = frame.f_globals["__file__"]
            else:
                frame = frame.f_back

        os.system("""start cmd /{} py {}""".format(mode, caller))


class UnixControl(Screen):
    def _resize(self):
        os.system(f"printf '\e[8;{self.resolution.height};{self.resolution.width}t'")

    def _new(self):
        pass


class Window(EventListener):
    """
    An abstract representation of a window, the class handles the internal loops.

    Subclasses of Window must implement :obj:`Window.loop` as it's client loop.
    Whereas traditionally, it as a decorator.
    Below is an example on the different approaches you can take.

    In functional programming:
    .. code:: py

       app = Window(resolution, max_fps)

       @app.loop()
       def game(screen):
           # this is the game loop
           ...

       # event subscriber
       @ON_SOME_EVENT.on_emit
       def callback():
           # event callback
           ...

    OOP:
    .. code:: py

       class App(Window):
           def loop(screen): # important that this is named "loop"
               # this is the game loop
               ...

           @Events.listen("ON_SOME_EVENT") # don't use @ON_SOME_EVENT.on_emit
           def callback():
               # event callback
               ...
    """

    PNAME = "ASCIINPY_PROCESS"

    __slots__ = (
        "resolution",
        "max_fps",
        "fov",
        "_debug",
        "_screen",
        "_client_loop",
        "_stop_time",
        "_new_win_mode",
        "_origin_depth",
    )

    def __init__(
        self,
        resolution: Union[Resolutions, Tuple[int, int]],
        max_fps: Optional[int] = None,
    ):
        self.screen: Screen = None
        self._stop_time: int = None

        self._new_win_mode: Literal["k", "c"]
        self._origin_depth: int

        self.fov = 1.53
        self.resolution = Resolutions(resolution)
        self.max_fps = max_fps

        self._debug = False

    @Event.listen("on_terminate")
    def _terminate(self):
        Screen._puts(ANSI.BEL)
        Screen._puts(ANSI.RESET)
        Screen._cursor((0, 0), visibility=True)
        Screen._clear()
        sys.exit(0)

    def enable_debug(self, mode: Literal["k", "c"] = "k", origin_depth: int = 5):
        r"""
        Enables debug mode for developers. Defaults to debug mode `k`.

        Modes
        ------
            k - Executes the application until interrupted but remains open

            c - Executes the application until interrupted then closes

        - Offloads program onto a subprocess on an external Terminal with the given mode
        - (TODO) Create another subprocess on a different Terminal for error catching and logging.
        """
        self._debug = True
        self._new_win_mode = mode
        self._origin_depth = origin_depth

    def loop(self, forcestop: Optional[int] = None) -> Displayer:
        r"""
        Registers the client loop under `loop` of window class.
        This consenquentially limits the decorator to be re-used.

        :returns: (Callable[[:class:`Screen`], None]) The wrapped function.
        """
        self._stop_time = forcestop

        def wrapper(func: Displayer):
            self.loop = func
            return func
        return wrapper

    def replay(self, frames: List[str], fps: int = 1):
        r"""
        Replays a given list of frames with the specified fps limit.

        :param frames:
            A list of frames to play.
        :type frames: List[:class:`str`]
        :param fps:
            The FPS at which the replay is rendered. It is defaulted to `1`.
        :type frames: :class:`int`
        """
        self.screen = self.get_screen(
            self.resolution, self.max_fps, self._stop_time, False, False, False
        )
        self.screen._resize()

        ON_START.emit()

        frames = [frame.replace("\n", "", -1) for frame in frames]
        index = 0
        while True:
            self.screen._frame = frames[index]
            index += 1
            if index >= len(frames):
                raise RuntimeError("Replay had run out of frames..")
            self.screen.refresh()
            sleep(60 / (fps * 60))

    def get_screen(self, *args, **kwargs):
        r"""
        Makes a screen based on the OS if none is present.
        """
        if self.screen is None:
            if os.name == "nt":
                constructor = WindowsControl
            else:
                constructor = UnixControl
            return constructor(*args, **kwargs)
        return self.screen

    def set_title(self, title: str):
        # type: (str) -> None
        r"""
        Sets the title of the current console window.
        """
        if os.name != "nt":
            Screen._puts(ANSI.ESC, "]2;{}".format(title))

    def set_fov(self, fov: float):
        r"""
        Sets the screen fov, this is only relevant if 3D objects are involved.

        :param fov:
            The FOV of the screen in radians. Defaults to 90 degrees or pi/2.
        :type fov: :class:`float`
        """
        self.fov = fov

    def run(
        self,
        show_fps: bool = False,
        sysdout: bool = True,
        timer: bool = False,
    ):
        r"""
        Creates a screen object internally, does necessary calls on the console and proceeds with debug mode if it is enabled.

        :param fov:
            FOV of the screen, only relevant to 3D.

        """

        self.screen = self.get_screen(
            self.resolution,
            self.max_fps,
            self._stop_time,
            self.fov,
            self._debug,
            show_fps,
            sysdout,
            timer,
        )

        if self._debug is True:
            if os.getenv(self.PNAME) != "child":
                os.environ[self.PNAME] = "child"
                self.screen._new(self._new_win_mode, self._origin_depth)
                return
            else:
                del os.environ[self.PNAME]

        if sysdout is True:
            self.screen._resize()
        Screen._clear()
        Screen._cursor(visibility=False)

        ON_START.emit()
        return self.loop(self.screen)
