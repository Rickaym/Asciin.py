from __future__ import print_function, division
from __future__ import division
from uuid import uuid4
from os import system
from time import sleep, time
from functools import cached_property, wraps
from math import e, tan
import sys
import re
import pydoc
import platform
from math import cos, sin
from os import getcwd
from pstats import Stats
from cProfile import Profile
from io import BytesIO, StringIO
from platform import python_version
"""
MIT License
Copyright (c) 2021 Ricky M
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__version__ = "0.1.7"

SINGLE_PRINT_FLAG = False
SCREENS = []
SCOPE_CACHE = {}
try:
    from typing import Any, List, Union, Callable
except ImportError:
    pass
TargetIO = StringIO if python_version()[0] == "3" else BytesIO
CWD = getcwd()
class Profiler:
    def __init__(self, path):
        self.path = path
    def __enter__(self):
        self.start()
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
    def start(self):
        self.cpf = Profile()
        self.cpf.enable()
    def stop(self):
        self.cpf.disable()
        redirect = TargetIO()
        Stats(self.cpf, stream=redirect).sort_stats("time").print_stats()
        with open(self.path, "w") as f:
            f.write(redirect.getvalue().replace(CWD, "", -1))
def beautify(frame, screen):
    # type: (Union[str, List[str]], Any) -> str
    """
    Maps an uncut frame into different pieces with newline characters to make it
    readable without perfect resolution.
    :param frame:
        The frame to be converted from newline characters to a straight line.
    :type frame: Union[:class:`str`, List[:class:`str`]:
    :param screen:
        The screen where this screen is ideally implemented ~ just to get the sense of the resolution really.
    :type screen: :class:`Displayable`
    """
    new_frame = list(frame)
    for h in range(screen.height):
        dist = h * screen.width
        new_frame[dist] = new_frame[dist] + "\n"
    return "".join(new_frame)
def morph(initial_string, end_string, consume="end", loop=True):
    # type: (str, str, str, bool) -> List[str]
    """
    Morphs one string onto another and return a string array
    of all the frames needed to be displayed.
    Args:
        initial_string (str): The starting frame of the resulting string.
        end_string (str): The ending frame of the resulting string.
        consume (Literal["end"], Literal["start"]): Direction of space consumption.
        loop (bool): Whether to make the morphing loop-friendly. Defaults to True.
    Returns:
        Tuple[List[str]]: All the frames needed to be displayed for the morphing process.
    """
    stages = []
    for i, z in enumerate(initial_string):
        if i > 0:
            out = initial_string[:-i] if consume == "end" else initial_string[i:]
        else:
            out = str(initial_string)
        if out in end_string:
            break
        stages.append(out)
    stages_2 = []
    for i, z in enumerate(end_string):
        if i > 0:
            out = end_string[:-i] if consume == "end" else end_string[i:]
        else:
            out = str(end_string)
        if len(out) >= len(stages[-1]):
            stages_2.append(out)
    stages.extend(stages_2[::-1])
    if loop:
        stages.extend(stages[::-1])
    return stages
def deprecated(callable):
    # type: (Callable) -> Callable
    """
    A decorator that simply raises a DeprecationWarning when the decorated function is called.
    This is just used around the package on demand.
    """
    def wrapper(*args, **kwargs):
        raise DeprecationWarning(
            "{} is deprecated, although fine for usage, consider other alternatives as this callable may be less optimized.".format(
                callable.__name__
            )
        )
    return wrapper
def write_collision_state(screen, self_frame, other_frame):
    """
    Helps tracking collision states by writing it onto a file IO.
    Uses a global flag to make sure it doesn't write a thousand times.
    :param screen:
        The screen where this is taking place.
    :type screen: :class:`Displayable`:
    :param self_frame:
        The frame of itself.
    :type self_frame: List[:class:`str`]
    :param other_frame:
        The frame of the other model.
    :type other_frame: List[:class:`str`]
    """
    # type: (Displayable, List[str], List[str]) -> None
    global SINGLE_PRINT_FLAG
    if SINGLE_PRINT_FLAG is False:
        SINGLE_PRINT_FLAG = True
        with open("self_frame.txt", "w") as f:
            f.write(beautify(self_frame, screen))
        with open("model_frame.txt", "w") as f:
            f.write(beautify(other_frame, screen))
def caches(func):
    def wrapper(*args, **kwargs):
        if SCOPE_CACHE.get(func) is None or SCOPE_CACHE[func][0] != (args, kwargs):
            global SCOPE_CACHE
            retval = func(*args, **kwargs)
            SCOPE_CACHE[func] = (args, kwargs), retval
        else:
            retval = SCOPE_CACHE[func][1]
        return retval
    return wrapper
GRADIENT = caches(
    lambda P1, P2: None if P2[0] - P1[0] == 0 else (P2[1] - P1[1]) / (P2[0] - P1[0])
)
PROJE_MATRIX = caches(lambda a, f, q, near: M(
    [a * f, 0, 0, 0],
    [0, f, 0, 0],
    [0, 0, q, 1],
    [0, 0, -near * q, 0]
))
class Matrix:
    """
    A matrix class that supports up to 10x10 matrixes.
    Supports scalar multiplication, pretty printing, equality checks,
    matrix multiplication and alias references such as x for element 0 and
    y for element 1.
    :param layers:
        The layers of the Matrix, a matrix can contain other matrixes.
    :type layers: Union[Tuple[:class:`int`], :class:`Matrix`]
    """
    NAME_SPACE = ("x", "y", "z", "k", "w")
    def __init__(self, *layers):
        self.layers = [
            layer if not isinstance(layer, (tuple, list)) else Matrix(*layer)
            for layer in layers
        ]
        self.__dict__.update(dict(zip(self.NAME_SPACE, self.layers)))
    def __eq__(self, o):
        return all(self.__dict__.get(attr) == o.__dict__.get(attr) for attr in self.NAME_SPACE)
    def __ne__(self, o):
        return not self.__eq__(o)
    def __repr__(self):
        return (
            "["
            + " ".join(
                (
                    str(val)
                    if not isinstance(val, Matrix)
                    else ("\n " if i != 0 else "") + val.__repr__()
                )
                for i, val in enumerate(self.layers)
            )
            + "]"
        )
    def __len__(self):
        return len(self.dimension)
    def __mul__(self, other):
        # type: (Union[Matrix, int]) -> Matrix
        """
        The number of columns of the 1st matrix must equal the number of rows of the 2nd matrix in multiplicatioon.
        And the result will have the same number of rows as the 1st matrix, and the same number of columns as the 2nd matrix.
        Matrix Multiplication,
            Scalar multiplication just multiplies every component of a matrix with the multiplier
            In a matrix to matrix multiplication, consider their sizes,
                in format :: row x column
            Matrix A: MA = 1x2 [[1 1]   Matrix B: MB = 2x1 [[0 0]
                                [1 1]]                      [1 1]]
            Col of MA == Row of MB or is incompatible
            that means MA(1x2) MB(2x1)
                          \ \_EA__/ /
                           \____EB_/
            expression A: EA = column(MA) == row(MB) represents the comparison expression needed to be true for compatibility
            expression B: EB =  row(MA), column(MB)  represents the dimension of the resultant matrix
        """
        if isinstance(other, Matrix):
            # self columns must equal other rows
            if len(self.dimension) != len(other.dimension["x"]):
                raise TypeError("uncompatible to multiple these matrixes")
            else:
                self_vals = list(self.layers)
                other_vals = list(other.layers)
                pass
        else:
            # scalar multiplication
            return M(*[val * other for val in list(self.dimension.values())])
    def __getitem__(self, item):
        try:
            return self.layers[item]
        except TypeError:
            return self.layers[self.NAME_SPACE.index(item)]
    def rounds(self):
        for i, l in enumerate(self.layers):
            if isinstance(l, Matrix):
                self.layers[i] = l.rounds()
            else:
                self.layers[i] = roundi(l)
        return self.layers
    @staticmethod
    def fast_4x4_mul(coord, other):
        coord = [coord[0], coord[1], coord[2], 1]
        res = [0, 0, 0, 0]
        for i in range(len(coord)):
            res[i] = (
                coord[0] * other[0][i]
                + coord[1] * other[1][i]
                + coord[2] * other[2][i]
                + coord[3] * other[3][i]
            )
        return M(res[0], res[1], res[2], res[3])
    @staticmethod
    def fast_3x3_mul(coord, other):
        coord = [coord[0], coord[1], coord[2]]
        res = [0, 0, 0]
        for i in range(len(coord)):
            res[i] = (
                coord[0] * other[0][i]
                + coord[1] * other[1][i]
                + coord[2] * other[2][i]\
            )
        return M(res[0], res[1], res[2])
class Line:
    """
    A conceptual line class with simple properties.
    :param p1:
        Starting point
    :type p1: List[:class:`int`, :class:`int`]
    :param p2:
        Endpoint
    :type p2: List[:class:`int`, :class:`int`]
    """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.gradient = GRADIENT(
            p1, p2
        )  #: Union[:class:`float`, :class:`int`]: The gradient of the line
        self.equation = (
            self._get_equation()
        )  #: Callable[[:class:`int`], Tuple[:class:`int`, :class:`int`]]: f(x) of the line that takes in x to return the (x,y) at that point
        self.inverse_equation = (
            self._get_inverse_equation()
        )  #: Callable[[:class:`int`], Tuple[:class:`int`, :class:`int`]]: inverse f(x) of the line that takes in y to return the (x,y) at that point
        self._points = None
    def __getitem__(self, x):
        return self.equation(x)
    @property
    def points(self):
        """
        The points that join p1 to p2.
        :type: List[Tuple[:class:`int`, :class:`int`]]
        """
        if self._points is None or self._points[1] != [self.p1, self.p2]:
            self._points = self._get_points(), [self.p1[:], self.p2[:]]
        return self._points[0]
    def _get_points(self):
        points_set = []
        if self.gradient is not None:
            points_set.extend(
                [
                    self.equation(x)
                    for x in range(
                        *(
                            (self.p1[0], self.p2[0] + 1)
                            if self.p1[0] - self.p2[0] < 0
                            else (self.p2[0], self.p1[0] + 1)
                        )
                    )
                ]
            )
        points_set.extend(
            [
                self.inverse_equation(y)
                for y in range(
                    *(
                        (self.p1[1], self.p2[1] + 1)
                        if self.p1[1] - self.p2[1] < 0
                        else (self.p2[1], self.p1[1] + 1)
                    )
                )
            ]
        )
        return set(points_set)
    def _get_equation(self):
        if self.p1[1] - self.p2[1] == 0:
            return lambda x: (x, self.p1[1])
        elif self.gradient is None or self.gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda x: (
                x,
                (self.gradient * x) - (self.gradient * self.p1[0]) + self.p1[1],
            )
    def _get_inverse_equation(self):
        if self.gradient is None or self.gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda y: (((y - self.p1[1]) / self.gradient) + self.p1[0], y)
class MatrixFactory:
    def __getitem__(self, layers):
        return Matrix(*layers)
    def __call__(self, *layers):
        return Matrix(*layers)
M = MatrixFactory()
X_ROTO_MATRIX = caches(lambda l: M(
    [1, 0       , 0],
    [0, cos(l) , -sin(l)],
    [0, sin(l), cos(l)]
))
Y_ROTO_MATRIX = caches(lambda l: M(
    [cos(l) , 0, sin(l)],
    [0      , 1, 0],
    [-sin(l), 0, cos(l)]
))
Z_ROTO_MATRIX = caches(lambda l: M(
    [cos(l), -sin(l), 0],
    [sin(l), cos(l) , 0],
    [0     , 0      , 1]
))
"""
Input: [ x ]
       | y |
       [ z ]
RoX: [1  0     0    ] RoY = [cos0  0  sin0] RoZ = [cos0  -sin0  0]
     |0  cos0  -sin0|       |0     1  0   |       |sin0  cos0   0|
     [0  sin0  cos0 ]       [-sin0 0  cos0]       [0     0      1]
"""
def project_3D(m, aspect_ratio, fov):
    # type: (Matrix, int, int) -> Matrix
    fnear = 0.1
    ffar = 10000
    q = ffar / (ffar - fnear)
    m = [m[0], m[1], m[2], 1]
    resultant = Matrix.fast_4x4_mul(m, PROJE_MATRIX(aspect_ratio, fov, q, fnear))
    if resultant.k != 0:
        resultant.x /= resultant.k
        resultant.y /= resultant.k
        resultant.z /= resultant.k
    return resultant
def rotate_3D(m, angle, axis):
    roto_mat = (
        X_ROTO_MATRIX
        if axis.lower() == "x"
        else Z_ROTO_MATRIX
        if axis.lower() == "z"
        else Y_ROTO_MATRIX
    )
    resultant = Matrix.fast_3x3_mul(m, roto_mat(angle))
    return resultant.layers
def roundi(num):
    return int(round(num))
class Characters:
    ramp = r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?<>i!lI;:-_+~,"^`'. """
    miniramp = r"""@%#*+=-:. """
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
    def __init__(self, dimension):
        if not isinstance(dimension, (type(self))):
            self.value = dimension
        else:
            self.value = dimension.value
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

try:
    from typing import Callable, Tuple, Union, Optional, Dict, List, Any
except ImportError:
    pass
__all__ = ["Window", "Displayable"]
SIGMOID = lambda x: 1 / (1 + e ** (-x))
class Displayable:
    """
    Defines the integral structure of a console displayable generalized for different OS terminals.
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
        self.resolution = resolution  #: :class:`Resolutions`: A conceptual enum of a the window resolution.
        self.width = resolution.width  #: :class:`int`: The width of the window.
        self.height = resolution.height  #: :class:`int`: The height of the window.
        self.debug_area = [
            0,
            self.resolution.height * 0.8,
        ]  #: Tuple[:class:`int`, :class:`int`]: Approximated area of a debug prompt on the terminal.
        self.fps_limiter = fps_limiter  #: Optional[:class:`int`]: The specified FPS limit of the window.
        self.palette = (
            Characters.miniramp
        )  #: List[:class:`str`]: The default list of a characters for test printing and native menu styling. Any changes to it must be in references to the valid :class:`Characters` texture list.
        self.fov = fov  #: :class:`float`: Fov of the current screen, must be in radians for 3D applicaions
        self.aspect_ratio = resolution.height / resolution.width
        self.emptyframe = [" "] * (
            self.resolution.pixels
        ) + ["\r"]  #: List[:class:`str`]: A base frame with nothing on it.
        self.show_fps = show_fps  #: :class:`bool`: Whether if the window has a menu indicating the fps.
        self.timer = timer  #: :class:`bool`: Whether the menu shows the timer before elimination when given.
        self.sysdout = sysdout  #: :class:`bool`: Whether the rendered frames are printed onto the window.
        self.debug = debug  #: :class:`bool`: Whether the window has debug mode enabled.
        self._fov = 1 / tan(fov * 0.5)
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
        if self._stop_at is not None and self.timer:
            self._frame = self._slice_fit(
                "Stopwatch: " + str(self._stop_at - roundi(time() - self._started_at)),
                20,
            )
    def to_distance(self, coordinate):
        return roundi(coordinate[0]) + (roundi(coordinate[1]) * self.width) -1
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
            sys.stdout.write(current_frame)
            sys.stdout.flush()
        if log_frames and self._last_frame != current_frame:
            self._frame_log.append(current_frame)
            self._last_frame = current_frame
        self._frames_displayed += 1
        self._frame = self.emptyframe[:]
    def _resize(self):
        """
        Abstract method in resizing a powershell or a command prompt to the given resolution, this does not actually
        care about the size of the screen - also removes scroll wheel.
        """
    def _new(self):
        """
        Creates an accessible powershell or a command prompt to the given resolution.
        """
class DispWindow(Displayable):
    def _resize(self):
        system(
            "mode con cols={} lines={}".format(
                self.resolution.width, self.resolution.height
            )
        )
    def _new(self):
        pass
class DispLinux(Displayable):
    def _resize(self):
        system(
            "printf '\e[8;{};{}t'".format(self.resolution.height, self.resolution.width)
        )
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
    def __init__(self, resolution, fps_limiter=None):
        # type: (Union[Tuple[int, int], Resolutions], int) -> None
        self.resolution = Resolutions(
            resolution
        )  #: :class:`Resolutions`: The respective resolution of the window.
        # format: off
        self.fps_limiter = fps_limiter  #: Optional[:class:`int`]: A simple FPS lock.
        self._window = None
        self._client_loop = None  # type: Callable
        self._system_loop = None  # type: Callable
        self._stop_time = None
    def _replay_loop(self, win_instance, frames, fps):
        # type: (Displayable, Tuple[List[str]], int) -> None
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
            self.resolution, self.fps_limiter, self._stop_time, False, False, False
        )
        if len(SCREENS) > 1:
            win_instance._new()
        else:
            win_instance._resize()
        SCREENS.append(win_instance)
        self._window = win_instance
        return self._replay_loop(win_instance, frames, fps)
    def run(
        self, fov=1.570796327, debug=False, show_fps=False, sysdout=True, timer=False
    ):
        # type: (int, bool, bool, bool, bool) -> None
        """
        Runs the client loop that has been defined.
        """
        global SCREENS
        window = self.platform_to_window[platform.system()]
        win_instance = window(
            self.resolution,
            self.fps_limiter,
            self._stop_time,
            fov,
            debug,
            show_fps,
            sysdout,
            timer,
        )
        if sysdout:
            if len(SCREENS) > 1:
                win_instance._new()
            else:
                win_instance._resize()
        SCREENS.append(win_instance)
        self._window = win_instance
        return self._client_loop(win_instance)

"""
Contains different definitions of blitting a model onto a frame with `model` and `screen` given.
Different models can pick best fitting render methods circumstantially.
"""
try:
    from typing import Any, Optional, Tuple, List, Set
except ImportError:
    pass
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def abstract_render_method(model, screen, **kwargs):
    # type: (Model, Displayable, Dict[str, Any]) -> Tuple[List[str], Tuple[int]]
    """
    Every rendering methods must implement this conceptual abstract method.
    """
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def rect_and_charpos(model, screen, empty=False):
    # type: (Any, Optional[Tuple[int, int]], bool) -> Tuple[List[str], Set[int]]
    """
    Figures out the position of the characters based on the temporal position and
    the position of the character in the model image.
    Time Complexity of this method is O(n) where n is
    the total amount of characters in a model image.
    """
    pixels = list(model.image)
    frame = list(screen._frame) if not empty else list(screen.emptyframe)
    # gets the starting index of the image in a straight line screen
    loc = roundi(model.rect.x) + (roundi(model.rect.y) * screen.resolution.width)
    max_loc = screen.resolution.width * screen.resolution.height
    x_depth = 0
    y_depth = 0
    occupancy = []
    for i, char in enumerate(pixels):
        if loc < 0 or loc > max_loc:
            continue
        if model.rect.texture:
            if char == "\n":
                frame[loc - 1] = model.rect.texture
            elif x_depth == 0 or y_depth == 0 or y_depth == (model.dimension[1] - 1):
                char = model.rect.texture
            elif i == (len(pixels) - 1):
                char = model.rect.texture
        if char == "\n":
            loc += screen.resolution.width - x_depth
            x_depth = 0
            y_depth += 1
            continue
        elif char == " ":
            continue
        occupancy.append(loc)
        try:
            frame[loc] = char
        except IndexError:
            continue
        else:
            x_depth += 1
            loc += 1
    if model.rect.texture:
        frame[-1] = model.rect.texture
    return frame, set(occupancy)
def rect_and_modelen(model, screen, empty=False):
    # type: (Any, Any, bool) -> Tuple[List[str], Set[int]]
    """
    Figures out the positions of characters by using the position of the character in the model
    image and it's desired dimensions to guess where it is on the screen.
    The only time you would want to use this is if you somehow cannot have newline characters in your image.
    Time Complexity of this method is O(n) where n is
    the total amount of characters in a model image.
    """
    frame = list(screen._frame) if not empty else list(screen.emptyframe)
    occupancy = []
    for row in range(model.rect.dimension[1]):
        for col in range(model.rect.dimension[0]):
            loc = (
                round(model.rect.x)
                + col
                + (screen.resolution.width * row)
                + round(model.rect.y) * screen.resolution.width
            )
            occupancy.append(loc)
            try:
                frame[loc] = model.texture
            except IndexError:
                pass
    return frame, set(occupancy)
def slice_fit(model, screen):
    # type: (Any, Any) -> Tuple[List[str], Set[int]]
    """
    Fits text onto the current frame.
    An adaptation of how the screen blits it's menubar etc natively.
    Extremely optimized.
    Time Complexity: O(n) where n is len(TEXT)
    """
    point = roundi(model.rect.x) + (screen.resolution.width * roundi(model.rect.y))
    if point < 0:
        point = screen.resolution.width + point
    frame = list(screen._frame[:point])
    frame.extend(list(model.image))
    frame.extend(screen._frame[point + len(model.image) :])
    return frame, set(range(point, point + len(model.image)))

"""
Contains different definitions on checking collisions of a model
Different models can pick best fitting collisions checking methods circumstantially.
"""
try:
    from typing import Any
except ImportError:
    pass
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def abstract_collision_checker(self, other):
    # type: (Model, Model) -> bool
    """
    Every collisions checking method must implement this conceptual abstract method.
    """
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@deprecated
def multi_collides_with(self, *models):
    # type: (Any, Any) -> bool
    self_frame = None
    other_frames = None
    screen_ = None
    states = [False] * len(models)
    # screen lookup is O(n) where n is the amount of screens
    # let the blit method have the time complexity of O(z)
    # Result: O(n+2z)
    for screen in SCREENS:
        if screen.all_models.get(self.rect) is not None:
            self_frame = self.blit(screen, empty=True)
            other_frames = [
                model.blit(screen, empty=True) for model in models if model != self
            ]
            screen_ = screen
            break
    # compared models are shallow and doesn't have a boundary
    if self_frame is None or len(other_frames) < 0:
        return False
    # collision lookup is O(m)
    # total time complexity in checking collisions is
    # O(n+2z+m) where m is the amount of characters in a screen
    for z, frame in enumerate(other_frames):
        for i, char in enumerate(self_frame):
            if char != " " and frame[i] != " ":
                write_collision_state(screen_, self_frame, frame)
                states[z] = True
                break
    return states if len(states) > 1 else states[0]
@deprecated
def collides_with(self, model):
    # type: (Any, Any) -> bool
    if model == self:
        return False
    self_frame = None
    other_frame = None
    screen_ = None
    # screen lookup is O(n) where n is the amount of screens
    # let the blit method have the time complexity of O(z)
    # Result: O(n+2z)
    for screen in SCREENS:
        if screen.all_models.get(self.rect) is not None:
            self_frame = self.blit(screen, empty=True)
            other_frame = model.blit(screen, empty=True)
            screen_ = screen
            break
    # compared models are shallow and doesn't have a boundary
    if self_frame is None or other_frame is None:
        return False
    # collision lookup is O(m)
    # total time complexity in checking collisions is
    # O(n+2z+m) where m is the amount of characters in a screen
    for i, char in enumerate(self_frame):
        if char != " " and other_frame[i] != " ":
            write_collision_state(screen_, self_frame, other_frame)
            return True
    return False
def coord_collides_with(self, model):
    """
    Retrives model occupancy and compares each sets to identify and
    colliding pixels.
    """
    if model is self:
        return False
    intersections = []
    intersections.extend(model.occupancy)
    intersections.extend(self.occupancy)
    if len(set(intersections)) < (
        len(model.occupancy) + len(self.occupancy)
    ):
        return True
    else:
        return False

try:
    from typing import Tuple, Any
except ImportError:
    pass
class Rectable(object):
    """
    A simple parent class for all models that can be translated into a rect.
    """
    def get_rect(self, coordinate=None, dimension=None):
        # type: (Tuple[int, int], Tuple[int, int]) -> Rect
        """
        Builds a rect object from scratch. If neither coordinate or dimension
        is given, the coordinate is assumed to be the origin and the dimension is fetched
        from the parent Object.
        This only creates a new rectangle object if none is present.
        If present returns what it already has.
        :param coordinate:
            The top-left coordinate for the rect.
        :type coordinate: Tuple[:class:`int`, :class:`int`]
        :param dimension:
            The dimension of the rect.
        :type coordinate: Tuple[:class:`int`, :class:`int`]
        :return: (:class:`Rect`) The rectangle made or acquired.
        """
        if self.__dict__.get("rect") is None:
            coordinate = coordinate or (0, 0)
            dimension = dimension or self.dimension
            self.rect = Rect(coordinate, dimension, self)
        return self.rect
    @staticmethod
    def make_rect(self, coordinate, dimension):
        # type: (Tuple[int, int], Tuple[int, int], str) -> Rect
        """
        Builds a rect object from the given arguments.
        :param coordinate:
            The top left coordinate of the rect.
        :type coordinate: Tuple[:class:`int`, :class:`int`]
        :param dimension:
            A tuple width it's width and height.
        :type dimension: Tuple[:class:`int`, :class:`int`]
        :return: (:class:`Rect`) The rectangle made or acquired.
        """
        if self.__dict__.get("rect") is None:
            coordinate = coordinate or (0, 0)
            dimension = dimension or self.dimension
            self.rect = Rect(coordinate, dimension, self)
        return self.rect
class Rect:
    """
    An abstract quadrilateral boundary for Rectable objects.
    Provides temporal positions of the given model's boundary.
    This can be an erroneous measurement of collisions when sections of the model
    exceeds the given boundary or an object is moving extremely fast.
    """
    def __init__(self, coordinate, dimension, parent):
        # type: (Tuple[int, int], Tuple[int, int], Any) -> None
        self.x = coordinate[0]  #: :class:`int`: Top left x position
        self.y = coordinate[1]  #: :class:`int`: Top left y position
        self.width = dimension[
            0
        ]  #: :class:`int`: The width of the rect. This is the horizontal difference.
        self.height = dimension[
            1
        ]  #: :class:`int`: The height of the rect (or length) this is the vertical difference.
        self.parent = (
            parent  #: :class:`Model`: A Parent object that the rect is assigned under.
        )
        self.texture = ""  #: :class:`str`: The outline texture of the rect.
        self._id = str(uuid4())[:5]
    @property
    def top(self):
        # type: () -> int
        """
        Uppermost y value.
        :type: :class:`int`
        """
        return self.y
    @property
    def bottom(self):
        # type: () -> int
        """
        Bottomost y value.
        :type: :class:`int`
        """
        return self.y + self.height
    @property
    def right(self):
        # type: () -> int
        """
        Right-most x value.
        :type: :class:`int`
        """
        return self.x + self.width
    @property
    def left(self):
        # type: () -> int
        """
        Left-most x value.
        :type: :class:`int`
        """
        return self.x


try:
    from typing import Tuple, List, str, Any, Dict
except ImportError:
    pass
DEFAULT_BRICK = "@"
DEFAULT_FILL = "&"
class Plane(Rectable):
    """
    Defines the integral structure for a model on a 2D plane.
    It is used to provide basic inheritance for prerequisites in subsystem interactions.
    For example the model's texture attribute is accessed in a certain
    rendering method and the image attribute is used to analyze it's dimension when none is provided etc..
    When subclassing, overidding the defined methods are operable - so long as it is in awareness of their consequences.
    Overidding those methods require you to follow a strict format as provided by the abstract methods - it is encouraged to
    avoid this unless perfectly necessary.
    """
    def __init__(self, path=None, image=None, rect=None, texture=None, fill=None, coordinate=None):
        # type: (str, str, Rect, str, str, Tuple[int, int]) -> None
        tmp_model = None
        if path is not None:
            with open(path, "r") as f:
                tmp_model = f.read()
        elif image is not None:
            tmp_model = image
        else:
            return
        split_model = tmp_model.split("\n")
        self.dimension = (
            len(max(split_model, key=lambda e: len(e))),
            len(split_model),
        )  #: Tuple[:class:`int`, :class:`int`]: The dimensions of the model. (Width, Height)
        self.image = str(tmp_model)  #: :class:`str`: The model's image/structure/shape.
        self.texture = texture or max(
            tmp_model,
            key=lambda element: tmp_model.count(element) and element != " ",
        )  #: :class:`str`: The generalized texture of the entire model. It is the most common character from the image.
        self.fill = fill
        self.rect = rect or self.get_rect(
            coordinate=coordinate, dimension=self.dimension
        )  #: :class:`Rect`: The rect boundary of the class.
        self.occupancy = (
            []
        )  #: List[:class:`int`]: A list of coordinates that the image would be at when blitted. This is used for collision detection.
    def collides_with(self, model):
        # type: (Model) -> bool
        """
        Checks whether if the current model is in collision with the provided
        model.
        :param model:
            The opposing model.
        :type model: :class:`Model`
        :returns: (:class:`bool`) Whether if the current model is in collision with the opposite model.
        """
        return coord_collides_with(self, model)
    def blit(self, screen, **kwargs):
        # type: (Displayable, Dict[str, Any]) -> None
        """
        The inner blitting method of the model. You should not use this yourself.
        :param screen:
            This is passed in the subsystem call inside the :obj:`Displayable.blit`.
        :type screen: :class:`Displayable`
        """
        return (
            rect_and_charpos(self, screen, **kwargs)
            if "\n" in self.image
            else rect_and_modelen(self, screen, **kwargs)
        )
class SimpleText(Plane):
    """
    A Simple text model that stores normal text objects in it's image attribute.
    Uses the slice-fit render method that native menus for the screen uses in a
    system level.
    :param coordinate:
        The top-left coordinate of the text.
    :type coordinate: Tuple[:class:`int`, :class:`int`]
    :param text:
        The text for the model.
    :type text: :class:`str`
    """
    def __init__(self, coordinate, text):
        super(SimpleText, self).__init__(image=str(text), coordinate=coordinate)
    def blit(self, screen):
        return slice_fit(self, screen)
class AsciiText(Plane):
    def __init__(self, coordinate, text):
        pass
    def blit(self, screen, **kwargs):
        pass
class Triangle(Plane):
    """
    A triangle model, this is often used as a 3D primitive.
    :param p1:
        Pivot or starting point
    :type p1: Tuple[:class:`int`, :class:`int`]
    :param p2:
        Certain bottom point
    :type p2: Tuple[:class:`int`, :class:`int`]
    :param p3:
        Certain bottom point
    :type p3: Tuple[:class:`int`, :class:`int`]
    """
    def __init__(self, p1, p2, p3, texture=None, fill=None):
        # type: (Tuple[int, int], Tuple[int, int], Tuple[int, int], str, str) -> None
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.texture = texture or DEFAULT_BRICK
        self.fill = fill or DEFAULT_FILL
        self.vertices = (
            Line(self.p1, self.p2),
            Line(self.p2, self.p3),
            Line(self.p1, self.p3),
        )
    def blit(self, screen):
        frame = list(screen._frame)
        for vert in self.vertices:
            for p in vert.points:
                loc = screen.to_distance(p)
                try:
                    frame[loc] = self.texture
                except IndexError:
                    pass
                except TypeError:
                    raise TypeError(
                        "list indices must be integers, not {} of value {}".format(
                            type(loc), loc
                        )
                    )
        return frame, [vert.points for vert in self.vertices]
class PixelPainter(Plane):
    """
    A model that takes in a coordinate and a dimension to create an empty canvas that is imprinted
    onto the frame at the exact coordinate when blitted onto screen.
    If not obvious, it doesn't directly create an imprint onto the frame - so when drawing onto the canvas
    the distance units and x, y values are relative to the dimensions of the canvas, not the screen.
    :param screen:
        The screen of which the PixelPainter is attached to.
    :type screen: :class:`Displayable`
    :param coordinate:
        The (x, y) coordinates that defines the top right of the canvas relative to the screen.
    :type coordinate: Tuple[:class:`int`, :class:`int`]
    :param dimension:
        The width and height of the canvas.
    :type dimension: Tuple[:class:`int`, :class:`int`]
    """
    def __init__(self, screen, coordinate=None, dimension=None):
        # type: (Displayable, Tuple(int, int), Tuple(int, int)) -> None
        self.coordinate = coordinate or 0, 0
        self.screen = screen
        self.dimension = dimension or (screen.width, screen.height)
        self.rect = self.get_rect(coordinate=coordinate, dimension=dimension)
        self.image = [" "] * (self.dimension[0] * self.dimension[1])
    def draw(self, pixels, coordinate):
        # type: (List(str), Tuple(int, int)) -> None
        """
        A gateway to directly editing the pixels in the canvas based on the distance from the origin or
        through coordinates.
        You must pass in either a `xy` or a `distance` kwarg to work.
        :param pixels:
            The pixels to be drawn.
        :type pixels: List[:class:`str`]
        :param coordinate:
            The x and y position of the pixels to be drawn - Defaults to None.
        :type coordinate: Tuple[:class:`int`, :class:`int`]
        :raises TypeError: Raised when neither xy or distance is passed in.
        :raises IndexError: Raised when the coordinate of the pixel is out of bounds.
        """
        distance = self.screen.to_distance(coordinate[0], coordinate[1])
        for i, pix in enumerate(pixels):
            try:
                self.image[distance + i] = pix
            except IndexError:
                raise IndexError("list index {} is out of range".format(distance))
            except TypeError:
                raise TypeError(
                    "list indices must be integers, not {} of value {}".format(
                        type(distance), distance
                    )
                )
    def blit(self, screen, **kwargs):
        return rect_and_charpos(self, screen, **kwargs)
class Square(Plane):
    """
    A Square Model.
    :param coordinate:
        The top-left coordiante of the square.
    :type coordinate: Tuple[:class:`int`, :class:`int`]
    :param length:
        The length of the square.
    :type length: :class:`int`
    :param texture:
        The monotone texture of the square.
    :type texture: :class:`str`
    """
    def __init__(self, coordinate, length, texture=None, fill=None):
        # type: (Tuple[int, int], int, str, str) -> None
        self.length = length
        super().__init__(
            image=(((texture * length) + "\n") * (length // 2)).strip(),
            rect=self.get_rect(coordinate, (length, length // 2)),
            texture=texture or DEFAULT_BRICK,
            fill=fill or DEFAULT_FILL,
        )

class Model:
    pass
class Cube:
    pass

