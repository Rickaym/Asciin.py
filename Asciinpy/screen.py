import os
import sys

from typing import Callable, Literal, Tuple, Union, Optional, List
from abc import ABCMeta, abstractmethod
from time import sleep, time

from .values import Characters, Resolutions, ANSI
from .devices import Keyboard
from .events import ON_START, Event, EventListener
from .utils import CartesianList
from .globals import PLATFORM


Displayer = Callable[["Screen"], None]
AnyInt = Union[int, float]


class Screen(metaclass=ABCMeta):
    r"""
    A meta class for a screen object.
    """

    palette = Characters.miniramp
    TPS = 25

    __slots__ = (
        "resolution",
        "width",
        "height",
        "max_fps",
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
        debug: bool,
        show_fps: bool,
        sysdout: bool,
        timer: bool,
    ):
        self.resolution = resolution
        self.width, self.height = resolution.value

        self.max_fps = max_fps
        self.aspect_ratio = resolution.height / resolution.width
        self.emptyframe = lambda: CartesianList([[" "] * (resolution.width) for _ in range(resolution.height)])
        self.show_fps = show_fps
        self.timer = timer
        self.sysdout = sysdout
        self.debug = debug

        self._frame = self.emptyframe()
        self._last_frame = self.emptyframe()
        self._records = []

        self._fps = 0
        self._average_fps = 0
        self._frames_displayed = 0

        self._started_at = time()
        self._stops_at = forcestop
        self._last_fps_measure = time()

        # pre-rendered
        self._infotext = (
            self.palette[2]
            + (r" " * (resolution.width - 2))
            + self.palette[2]
            + self.palette[2]
            + (self.palette[2] * (resolution.width - 2))
            + self.palette[2]
        )
        self.__stdout__ = sys.stdout
        self.sysdout_fileno = self.__stdout__.fileno()

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
    def frame(self) -> str:
        """
        The current frame rendered.

        :type: :class:`str`
        """
        return "".join(self._frame.flatten())

    @property
    def fps(self) -> int:
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
    def average_fps(self) -> int:
        """
        The amount of frames rendered on average from start to present.

        :type: :class:`int`
        """
        return self._average_fps / (time() - self._started_at)

    @property
    def tick(self) -> int:
        """
        Internal ticks, from 0 to 25 for timing certain things.

        :type: :class:`int`
        """
        return round(time() - self._started_at) % self.TPS

    def _infograph(self):
        r"""
        Ensures correct conditions to blit a debug menu at the top of the window.

        This menu is pre-rendered before-hand and the values are formatted
        in to maintain a max slice-fit of one per render.
        """
        if self.show_fps:
            text = self._infotext % str(self.fps).rjust(5)
            self._frame[0] = text[:self.width-1]
            self._frame[1] = text[self.width-1:]

    def blit(self, object: Callable, *args, **kwargs):
        r"""
        Simply calls the object's internal blit method onto itself and does necessary
        records.

        :param object:
            The Model to be blitted onto screen.
        :type object: Union[:class:`Plane`, :class:`Mask`]
        """
        object.occupancy = object.blit(self, *args, **kwargs)

    def refresh(self, log_frames=False):
        r"""
        Empties the current frame. If sysdout is enabled, it is printed onto the window.

        :param log_frames:
            Whether to keep track of the amount of frames displayed throughout the session.
        :type log_frames: :class:`bool`
        """
        if self._stops_at is not None and time() - self._started_at >= self._stops_at:
            raise RuntimeError("Times up! Program has been force stopped.")

        self._infograph()
        current_frame = self.frame

        if self.sysdout:
            self._update(current_frame)
        if log_frames and self._last_frame != current_frame:
            self._records.append(current_frame)
            self._last_frame = current_frame

        self._frames_displayed += 1
        self._frame = self.emptyframe()

    def events(self):
        r"""
        Gather all IO events.
        """
        Keyboard.getch()

    def draw(self, coord: Tuple[int, int], char: str):
        r"""
        Paints a specific point on the cavas with the character.
        """
        self._frame[round(coord[0]), round(coord[1])] = str(char)

    def _resize(self):
        """
        Abstract method in resizing a powershell or a command prompt to the given resolution, this does not actually
        care about the size of the screen - also removes scroll wheel.
        """

    def _new(self):
        """
        Creates an accessible powershell or a command prompt to the given resolution.
        """

    @abstractmethod
    def _update(self, frame: str):
        pass


class ConsoleInterface(EventListener, Screen):
    def __init__(self, resolution: Resolutions, max_fps: Optional[int], forcestop: Optional[int], debug: bool, show_fps: bool, sysdout: bool, timer: bool):
        super().__init__(resolution, max_fps, forcestop, debug, show_fps, sysdout, timer)
        self.stdout = sys.stdout
        self.cout = self.stdout.fileno()

    def _resize(self):
        if PLATFORM == "Windows":
            os.system(
                f"mode con cols={self.width} lines={self.height}"
            )
        elif PLATFORM == "Linux" or PLATFORM == "Darwin":
            os.system(f"printf '\e[8;{self.resolution.height};{self.resolution.width}t'")
        else:
            raise NotImplementedError("Resize method is not implemented in this OS")

    def _new(self, mode: Literal["k", "c"], origin_depth: int):
        r"""
        Starts a different command prompt dedicated for display and
        leaves the current one.
        """
        frame = list(sys._current_frames().values())[0]

        # Searches the origin of a call
        for i in range(origin_depth):
            if getattr(frame, "f_back") is None:
                caller = frame.f_globals["__file__"]
            else:
                frame = frame.f_back
        if PLATFORM == "Windows":
            command = f"""start cmd /{mode} {sys.executable} "{caller}" ;pause"""
        else:
            command = f"""gnome-terminal --working-directory=$pwd  -- "{sys.executable}" '{caller}'"""

        os.system(command)

    def _puts(self, *sequence: List[str]):
        r"""
        Writes onto sys stdout directly with the encoding.
        """
        os.write(self.cout, "".join(sequence).encode())

    def _slice_fit(self, coordinate: Tuple[int, int], *body: str):
        r"""
        Simplified implementation of the slice_fit render method to blit window menus and
        native elements.
        """
        coordinate = list(coordinate)
        for i, chr in enumerate(str(body)):
            self.draw((coordinate[0]+i, coordinate[1]), chr)
            if coordinate[0]+i == self.width:
                coordinate[1] +=1
                coordinate[0] = -i

    def _clear(self):
        """
        Clears the current visible terminal
        """
        self._puts(ANSI.CSI, "2J")

    def _cursor(self, goto: Tuple[AnyInt, AnyInt]=None, visibility: bool=None):
        if goto is not None:
            self._puts(ANSI.CSI, "%d;%dH" % goto)
        if visibility is not None:
            if visibility is True:
                self._puts(ANSI.CSI, "?25h")
            else:
                self._puts(ANSI.CSI, "?25l")

    def _update(self, frame: str):
        self._cursor((0, 0))
        self._puts(frame)

    @Event.listen("on_terminate")
    def _terminate(self):
        self._puts(ANSI.BEL)
        if self.sysdout is True:
            self._cursor((0, 0), visibility=True)
            self._clear()

    def _startup(self):
        if self.sysdout is True:
            self._resize()
            self._clear()
            self._cursor(visibility=False)


class Window:
    r"""
    An abstract representation of a window, the class handles the internal loops.

    Subclasses of Window must implement :obj:`Window.loop` as it's client loop.
    Whereas traditionally, it as a decorator.
    """

    PNAME = "ASCIINPY_PROCESS"

    __slots__ = (
        "resolution",
        "max_fps",
        "_stop_time",
        "__loop__",
        "_debug"
    )

    def __init__(
        self,
        resolution: Union[Resolutions, Tuple[int, int]],
        max_fps: Optional[int] = None,
    ):
        self.resolution = Resolutions(resolution)
        self.max_fps = max_fps
        self.__loop__ = None
        self._debug = False, None, None

    def enable_debug(self, mode: Literal["k", "c"] = "k", origin_depth: int = 5):
        r"""
        Enables debug mode for developers. Defaults to debug mode `k`.

        Modes:
            k - Executes the application until interrupted but remains open

            c - Executes the application until interrupted then closes

        Offloads program onto a subprocess on an external Terminal with the given mode.
        """
        self._debug = True, mode, origin_depth

    def loop(self, forcestop: Optional[int] = None, screen: Screen=None) -> Displayer:
        r"""
        Registers the client loop under `loop` of window class.
        This consenquentially limits the decorator to be re-used.

        :returns: (Callable[[:class:`Screen`], None]) The wrapped function.
        """
        if self.__loop__ is not None:
            return self.__loop__(screen)

        self._stop_time = forcestop

        def wrapper(func: Displayer):
            self.__loop__ = func
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
        frames = [frame.replace("\n", "", -1) for frame in frames]
        index = 0
        ON_START.emit()
        while True:
            self.screen._frame = frames[index]
            index += 1
            if index >= len(frames):
                raise RuntimeError("Replay had run out of frames..")
            self.screen.refresh()
            sleep(60 / (fps * 60))

    def set_title(self, title: str):
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

    def _run_consolas(self, show_fps: bool, sysdout: bool, timer: bool,):
        r"""
        Creates and screen object by basis of a console.

        :param fov:
            FOV of the screen, only relevant to 3D.
        """
        screen = ConsoleInterface(
            self.resolution,
            self.max_fps,
            self._stop_time,
            self._debug,
            show_fps,
            sysdout,
            timer,
        )
        if self._debug[0] is True:
            if os.getenv(self.PNAME) != "child":
                os.environ[self.PNAME] = "child"
                screen._new(self._debug[1], self._debug[2])
                return
            else:
                del os.environ[self.PNAME]

        ON_START.emit()

        # running this on another thread can delete potential
        # tracebacks
        screen._startup()
        if self.__loop__ is None:
            return self.loop(screen=screen)
        else:
            return self.__loop__(screen=screen)

    def run(
        self,
        show_fps: bool = False,
        sysdout: bool = True,
        timer: bool = False,
    ):
        return self._run_consolas(show_fps, sysdout, timer)
