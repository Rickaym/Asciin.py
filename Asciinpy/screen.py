import os
import sys

from itertools import chain
from time import sleep, time
from traceback import print_exception
from abc import ABCMeta, abstractmethod
from typing import Callable, Literal, Tuple, Union, Optional, List

from .objects import Blitable
from .values import WINDOW_COLOR_HEXES, Color, Characters, Resolutions, ANSI
from .devices import Keyboard
from .events import ON_START, ON_TERMINATE, Event, EventListener
from .globals import Platform
from .types import AnyInt, IntCoordinate


__all__ = ["Window", "Screen"]

Displayer = Callable[["Screen"], None]
DisplayerWrapper = Callable[[Displayer], Displayer]


class Screen(metaclass=ABCMeta):
    """
    A meta class for a screen object.

    Attributes:
        resolutions: :class:`~Asciinpy.values.Resolutions`
            The resolution of the screen.
        max_fps: :class:`int`
            The fps cap for the screen.
        aspect_ratio: :class:`int`
            The aspect ratio of the screen.
        show_fps: :class:`bool`
            A boolean flag whether an FPS text box is shown on screen.
        timer: :class:`int`
            A number in seconds that the screen is allowed to run in entirity, when reached exits gracefully.
        sysdout: :class:`bool`
            A boolean flag on whether visualization of the rendering is enabled.
        debug: :class:`bool`
            A boolean flag whether debug mode is turned on.
    """

    palette = Characters.some
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
        "_stdout",
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
        self.resolution: Resolutions = resolution
        self.width, self.height = resolution.value

        self.max_fps = max_fps
        self.aspect_ratio = resolution.height / resolution.width
        self.show_fps = show_fps
        self.timer = timer
        self.sysdout = sysdout
        self.debug = debug

        self._frame = self.get_emptyframe()
        self._last_frame = self.get_emptyframe()
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
        self._stdout = sys.stdout

        fps_size = 0
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

    def get_emptyframe(self) -> List[List[str]]:
        return [[" "] * (self.resolution.width) for _ in range(self.resolution.height)]

    @property
    def frame(self) -> str:
        """
        The current frame rendered.
        """
        return "".join(chain.from_iterable(self._frame))

    @property
    def fps(self) -> int:
        """
        The amount of frames rendered per the second passed.
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
    def average_fps(self) -> float:
        """
        The amount of frames rendered on average from start to present.
        """
        return self._average_fps / (time() - self._started_at)

    @property
    def tick(self) -> int:
        """
        Internal ticks, from 0 to 25 for timing certain things.
        """
        return round(time() - self._started_at) % self.TPS

    def _infograph(self):
        """
        Ensures correct conditions to blit a debug menu at the top of the window.

        This menu is pre-rendered before-hand and the values are formatted
        in to maintain a max slice-fit of one per render.
        """
        if self.show_fps:
            text = self._infotext % str(self.fps).rjust(5)
            self._frame[0] = text[: self.width - 1]
            self._frame[1] = text[self.width - 1 :]

    def blit(self, *objects: Blitable, **kwargs):
        """
        Simply calls the object's internal blit method onto itself and does necessary
        records.

        :param objects:
            Any number of models to be blitted onto screen.
        :type object: :class:`~Asciinpy.objects.Blitable`
        """
        for obj in objects:
           obj.blit(self, **kwargs)

    def refresh(self, log_frames=False):
        """
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
        self._frame = self.get_emptyframe()

    def events(self):
        """
        Generally, the client does not capture user events
        this method must be called in order to gather them.
        """
        Keyboard.getch()

    def draw(self, point: IntCoordinate, char: str):
        """
        Paints a specific point on the cavas with the character.
        """
        try:
            self._frame[point[1]][point[0]] = char
        except IndexError:
            pass

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
        super().__init__(
            resolution, max_fps, forcestop, debug, show_fps, sysdout, timer
        )
        self.stdout = sys.stdout
        self.cout = self.stdout.fileno()

    def _resize(self):
        if Platform.is_window:
            os.system(f"mode con cols={self.width} lines={self.height}")
        elif Platform.is_linux or Platform.is_darwin:
            os.system(
                rf"printf '\e[8;{self.resolution.height};{self.resolution.width}t'"
            )
        else:
            raise NotImplementedError(
                f"resize method is not implemented in this platform {Platform.name}"
            )

    def _new(self, mode: Union[str, Literal["k", "c"]], origin_depth: int):
        """
        Starts a different command prompt dedicated for display and
        leaves the current one.
        """
        frame = list(sys._current_frames().values())[0]
        # Searches the origin of a call
        caller = None
        for _ in range(origin_depth):
            if getattr(frame, "f_back") is None:
                caller = frame.f_globals["__file__"]
            else:
                if frame.f_back is None:
                    break
                else:
                    frame = frame.f_back
        if caller is None:
            raise ValueError(
                f"origin depth {origin_depth} is not enough to find the caller"
            )

        if Platform.is_window:
            command = f"""start cmd /{mode} {sys.executable} "{caller}" ;pause"""
        elif Platform.is_linux or Platform.is_darwin:
            command = f"""gnome-terminal --working-directory=$pwd  -- "{sys.executable}" '{caller}'"""
        else:
            raise NotImplementedError(
                f"this platform {Platform.name} is not supported on asciinpy"
            )

        os.system(command)

    def _puts(self, *sequence: str):
        """
        Writes onto sys stdout directly with the encoding.
        """
        os.write(self.cout, "".join(sequence).encode())

    def _slice_fit(self, coordinate: Tuple[int, int], *body: str):
        """
        Simplified implementation of the slice_fit render method to blit window menus and
        native elements.
        """
        m_coordinate = list(coordinate)
        for i, chr in enumerate(str(body)):
            self.draw((m_coordinate[0] + i, m_coordinate[1]), chr)
            if m_coordinate[0] + i == self.width:
                m_coordinate[1] += 1
                m_coordinate[0] = -i

    def _clear(self):
        """
        Clears the current visible terminal
        """
        self._puts(ANSI.CSI, "2J")

    def _cursor(self, goto: Optional[Tuple[AnyInt, AnyInt]] = None, visibility: Optional[bool] = None):
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

    def _enable_VT100(self):
        """
        Enable the VT100 sequence.
        """
        if Platform.is_window:
            os.system("")

    @Event.listen(ON_START)
    def _start(self):
        self._enable_VT100()
        if self.sysdout is True:
            self._resize()
            self._clear()
            self._cursor(visibility=False)

    @Event.listen(ON_TERMINATE)
    def _terminate(self, exit_code: int):
        if self.sysdout is True:
            self._cursor(visibility=True)
            if exit_code != -1:
                self._clear()


class Window(EventListener):
    """
    An abstract representation of a window, the class handles the internal loops.

    Subclasses of Window must implement :obj:`Window.loop` as it's client loop.
    Whereas traditionally, it as a decorator.

    Attributes:
        resolutions: :class:`~Asciinpy.values.Resolutions`
            The resolution of the screen.
        max_fps: :class:`int`
            The fps cap for the screen.
        fov: :class:`int`
            The fov of the screen relevant for 3D rendering.
        screen: Optional[:class:`~Asciinpy.screen.Screen`]
            A screen object instantiated when run.
    """

    PNAME = "ASCIINPY_PROCESS"

    __slots__ = (
        "resolution",
        "max_fps",
        "fov",
        "screen",
        "_game_loop",
        "_title",
        "_foreground_color",
        "_background_color",
        "_stop_time",
        "_debug",
        "_debug_mode",
        "_debug_origin_depth",
    )

    def __init__(
        self,
        resolution: Union[Resolutions, Tuple[int, int]],
        max_fps: Optional[int] = None,
    ):
        if isinstance(resolution, Resolutions):
            self.resolution = resolution
        else:
            self.resolution = Resolutions.custom(resolution)

        self.max_fps = max_fps
        self._title = None
        self._debug = False
        self._debug_mode = "k"
        self._debug_origin_depth = 5
        self._foreground_color = None
        self._background_color = None
        self._game_loop: Optional[Displayer] = None

    def enable_debug(self, mode: Optional[Literal["k", "c"]] = None, origin_depth: Optional[int] = None):
        """
        Enables debug mode for developers. Defaults to debug mode `k`.

        Modes:
            k - Executes the application until interrupted but remains open
            c - Executes the application until interrupted then closes

        Offloads program onto a subprocess on an external Terminal with the given mode.
        """
        self._debug = True
        if mode:
            self._debug_mode = mode
        if origin_depth:
            self._debug_origin_depth = origin_depth

    def loop(
        self, screen: Optional[Screen] = None, forcestop: Optional[int] = None
    ) -> DisplayerWrapper:
        """
        Registers the client loop under `loop` of window class.
        This consenquentially limits the decorator to be re-used.

        :returns: (Callable[[:class:`Screen`], None]) The wrapped function.
        """

        def wrapper(func: Displayer) -> Displayer:
            self._game_loop = func
            return func

        if self._game_loop and screen:
            self._game_loop(screen)
            return wrapper

        self._stop_time = forcestop
        return wrapper

    def replay(self, frames: List[str], fps: int = 1):
        """
        Replays a given list of frames with the specified fps limit.

        :param frames:
            A list of frames to play.
        :type frames: List[:class:`str`]
        :param fps:
            The FPS at which the replay is rendered. It is defaulted to `1`.
        :type frames: :class:`int`
        """
        self.screen = ConsoleInterface(
            self.resolution, self.max_fps, self._stop_time, False, False, False, False
        )
        _frames = [frame.replace("\n", "", -1) for frame in frames]
        index = 0
        ON_START.emit()
        while True:
            self.screen._frame = _frames[index]
            index += 1
            if index >= len(_frames):
                raise RuntimeError("Replay had run out of frames..")
            self.screen.refresh()
            sleep(60 / (fps * 60))

    def set_fov(self, fov: float):
        """
        Sets the screen fov, this is only relevant if 3D objects are involved.

        :param fov:
            The FOV of the screen in radians. Defaults to 90 degrees or pi/2.
        :type fov: :class:`float`
        """
        self.fov = fov

    def set_title(self, title: str):
        self._title = title

    def set_color(
        self, foreground: Optional[Color] = None, background: Optional[Color] = None
    ):
        if foreground:
            self._foreground_color = foreground
        if background:
            self._background_color = background

    @Event.listen(ON_START)
    def _decorate_console(self):
        if Platform.is_window:
            if self._title:
                os.system(f"TITLE {self._title}")
            if self._foreground_color or self._background_color:
                fg_hex = (
                    WINDOW_COLOR_HEXES[self._foreground_color]
                    if self._foreground_color
                    else "0"
                )
                bg_hex = (
                    WINDOW_COLOR_HEXES[self._background_color]
                    if self._background_color
                    else "0"
                )
                if os.system(f"COLOR {bg_hex}{fg_hex}") == 1:
                    raise ValueError(
                        f"a combination of foreground {self._foreground_color}"
                        f" and background {self._background_color} is invalid"
                    )
        elif Platform.is_darwin or Platform.is_linux:
            if self._title:
                self.screen._puts(ANSI.ESC, "]2;{}".format(self._title))
            if self._foreground_color or self._background_color:
                raise NotImplementedError
        else:
            raise NotImplementedError(
                f"console decorations not supported for {Platform.name}"
            )

    @Event.listen(ON_TERMINATE)
    def _restore_console(self, exit_code: int):
        if Platform.is_window:
            if self._title:
                os.system("TITLE Command Prompt")
            if self._foreground_color or self._background_color:
                os.system("COLOR")
        elif Platform.is_darwin or Platform.is_linux:
            if self._title:
                raise NotImplementedError
            if self._foreground_color or self._background_color:
                raise NotImplementedError
        else:
            raise NotImplementedError(
                f"console decorations not supported for {Platform.name}"
            )

    def _run_consolas(
        self,
        show_fps: bool,
        sysdout: bool,
        timer: bool,
    ):
        """
        Creates and screen object by basis of a console.

        :param fov:
            FOV of the screen, only relevant to 3D.
        """
        self.screen = ConsoleInterface(
            self.resolution,
            self.max_fps,
            self._stop_time,
            self._debug,
            show_fps,
            sysdout,
            timer,
        )

        if self._debug is True:
            if os.getenv(self.PNAME) != "child":
                os.environ[self.PNAME] = "child"
                self.screen._new(self._debug_mode, self._debug_origin_depth)
                return
            else:
                del os.environ[self.PNAME]

        ON_START.emit()
        try:
            self.loop(screen=self.screen)
        except Exception as e:
            print_exception(e.__class__, e, e.__traceback__)
            exit_code = -1
        else:
            exit_code = 0
        ON_TERMINATE.emit(exit_code)

    def run(
        self,
        show_fps: bool = False,
        sysdout: bool = True,
        timer: bool = False,
    ):
        return self._run_consolas(show_fps, sysdout, timer)
