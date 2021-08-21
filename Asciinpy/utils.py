from platform import python_version
from io import BytesIO, StringIO
from cProfile import Profile
from pstats import Stats
from copy import deepcopy
from os import getcwd

from .globals import FINISHED_ONCE_TASKS, SINGLE_PRINT_FLAG, SCOPE_CACHE

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


def beautify(dimension, frame):
    # type: (Union[str, List[str]], Any) -> str
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
    for h in range(dimension[1]):
        nw_frame[h * dimension[0]] += "\n"
        raise KeyboardInterrupt(nw_frame)

    return "".join(nw_frame)


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


def save_frame(frame, path):
    with open(path, "w") as f:
        f.write(frame)


def only_once(func):
    def wrapper(*args, **kwargs):
        global FINISHED_ONCE_TASKS
        if func not in FINISHED_ONCE_TASKS:
            FINISHED_ONCE_TASKS.append(func)
            return func(*args, **kwargs)
        else:
            return None
    return wrapper


def caches(func):
    def wrapper(*args, **kwargs):
        global SCOPE_CACHE
        if SCOPE_CACHE.get(func) is None or SCOPE_CACHE[func][0] != (args, kwargs):
            retval = func(*args, **kwargs)
            SCOPE_CACHE[func] = (deepcopy(args), deepcopy(kwargs)), deepcopy(retval)
        else:
            retval = SCOPE_CACHE[func][1]
        return retval
    return wrapper