import inspect

from functools import wraps
from io import StringIO
from cProfile import Profile
from pstats import Stats
from typing import Any, Iterator, Literal, Tuple, List, Union, Callable

from .globals import FINISHED_ONCE_TASKS, CWD


class Profiler:
    """
    Instance profiler wrapper for CProfiler.

    Encapsulate the call with a context manager of the profiler and a file path to save the statistics returned.

    .. code:: py

       with Profiler("file.txt"):
           window.run(show_fps=True)


    You can also use it functionally for any reason.

    .. code:: py

       pf = Profiler("file.txt")
       pf.start()
       window.run(show_fps=True)
       pf.stop()
    """
    def __init__(self, path: str):
        self.path = path

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        """
        Starts gathering statistics.
        """
        self.cpf = Profile()
        self.cpf.enable()

    def stop(self):
        """
        Stop gathering statistics.
        """
        self.cpf.disable()
        redirect = StringIO()
        Stats(self.cpf, stream=redirect).sort_stats("time").print_stats()
        with open(self.path, "w") as f:
            f.write(redirect.getvalue().replace(CWD, "", -1))


def beautify(dimension: Tuple[int, int], frame: Union[List[str], str]) -> str:
    """
    Maps an uncut frame into different pieces with newline characters to make it
    readable in a given context of dimension.

    :param dimension:
        The bordering dimension of this line frame.
    :type dimension: Tuple[:class:`int`, :class:`int`]
    :param frame:
        The frame to be converted from newline characters to a straight line.
    :type frame: Union[:class:`str`, List[:class:`str`]:
    """
    nw_frame = list(frame)
    if isinstance(nw_frame[0], str):
        for h in range(dimension[1]):
            nw_frame[h * dimension[0]] += "\n"
    elif isinstance(nw_frame[0], (list, tuple)):
        for i in range(len(nw_frame)):
            nw_frame[i] += '\n'
    return "".join(nw_frame)


def morph(initial_string: str, end_string: str, consume: Literal["start", "end"]="end", loop: bool=True) -> List[str]:
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


def deprecated(callable: Callable) -> Callable:
    """
    Simply raises a DeprecationWarning when the decorated function is called.
    """

    def wrapper(*args, **kwargs):
        raise DeprecationWarning(
            "{} is deprecated, although fine for usage, consider other alternatives as this callable may be less optimized.".format(
                callable.__name__
            )
        )
    return wrapper


def praised(release) -> Callable:
    """
    A to-be implemented features.
    """
    def wrapper(callable: Callable) -> Callable:
        def wrapped():
            raise TypeError(
            f"{callable.__name__} is praised in the current release and is expected to be implemented in version {release}."
        )
        return wrapped
    return wrapper


def only_once(func: Callable) -> Callable:
    """
    Executes the given function only once.

    .. code:: py

       @only_once
       def some_func(...):
           ...

       while ...:
           some_func()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        global FINISHED_ONCE_TASKS
        if func not in FINISHED_ONCE_TASKS:
            FINISHED_ONCE_TASKS.append(func)
            return func(*args, **kwargs)
        else:
            return None
    return wrapper


def isinstancemethod(func: Callable) -> bool:
    """
    Returns whether if a given function is a staticmethod or an instancemethod/classmethod.
    """
    return "self" in inspect.getfullargspec(func)[0]
