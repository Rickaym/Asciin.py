import inspect
import os

from platform import python_version
from functools import wraps
from io import BytesIO, StringIO
from cProfile import Profile
from pstats import Stats
from random import randint
from typing import Any, Literal, Tuple, List, Union, Callable

from .values import ANSI
from .globals import FINISHED_ONCE_TASKS, ASSET_CACHE

TargetIO = StringIO if python_version()[0] == "3" else BytesIO
CWD = os.getcwd()
Supplier = Callable[[None], Any]

class Color:
    def FOREGROUND(id):
        return ANSI.CSI + "38;5;{}m".format(id)

    def BACKGROUND(id):
        return ANSI.CSI + "48;5;{}m".format(id)

    @staticmethod
    def RGB_FOREGROUND(r, g, b):
        return ANSI.CSI + "38;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def RGB_BACKGROUND(r, g, b):
        return ANSI.CSI + "48;2;{};{};{}m".format(r, g, b)

    @staticmethod
    def FORE(r, g, b):
        return Color.RGB_FOREGROUND(r, g, b)

    @staticmethod
    def BACK(r, g, b):
        return Color.RGB_BACKGROUND(r, g, b)


Color.FORE.random = lambda: Color.FORE(
    randint(0, 255), randint(0, 255), randint(0, 255)
)
Color.BACK.random = lambda: Color.BACK(
    randint(0, 255), randint(0, 255), randint(0, 255)
)


class Profiler:
    def __init__(self, path: str):
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


def beautify(dimension: Tuple[int, int], frame: Union[str, List[str]]) -> str:
    r"""
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


def morph(initial_string: str, end_string: str, consume: Literal["start", "end"]="end", loop: bool=True) -> List[str]:
    r"""
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


def deprecated(callable: Callable):
    r"""
    Simply raises a DeprecationWarning when the decorated function is called.
    """

    def wrapper(*args, **kwargs):
        raise DeprecationWarning(
            "{} is deprecated, although fine for usage, consider other alternatives as this callable may be less optimized.".format(
                callable.__name__
            )
        )

    return wrapper


def save_frame(frame: str, path: str):
    r"""
    Helper function to save a string frame onto a text file.
    """
    with open(path, "w") as f:
        f.write(frame)


def only_once(func: Callable) -> Callable:
    r"""
    Executes the given function only once.
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
    r"""
    Returns whether if a given function is a staticmethod or an instancemethod/classmethod.
    """
    return "self" in inspect.getfullargspec(func)[0]


def asset(getlibt):
    r"""
    A decorator that marks a methods to be only re-evaulated on first call and necessary liability changes ignorant
    towards arguments.

    Where as LRU caching etc.. is oriented by arguments, liabilites are oriented by a supplier.
    A supplier is a function that takes no arguments but returns some.
    Consider this simple supplier -> lambda: 2

    The supplier is called and save and whenever the output of the supplier changes, the function return value will be re-evaluated,
    if not the function is only called once and the results are returned from cache.

    .. code:: py

       a = 21

       @asset(lambda: a)
       def a_mutate():
           return a // 23 ** 24 - 245

       # all of this will only call `a_mutate` once
       a_mutate() and a_mutate() and a_mutate()
       # unless a is changed, the function is re-evaluated
       a = 55
       a_mutate() and a_mutate()

    Instance attributes can also be used within the supplier but it isn't straight forward.
    Classes that want to use asset caching must be subclassed under AssetCached and reference it's
    instance variables in strings.

    .. code::py

       class Klazz(AssetCached):
           def __init__(self, bomb):
               self.bomb = bomb

           @asset(lambda: "bomb")
           def get_bomb(self):
               return self.bomb.upper().strip().replace(' ', "KAPOW")

    The string liability names provided will be looked up on initialization time and will be resolved
    automically.
    """
    ret = getlibt()
    # tuplize single string
    if isinstance(ret, str):
        def wrapped_getlibt():
            return (ret,)
        getlibt = wrapped_getlibt

    def wrapper(func: Callable) -> Callable:
        func.__getliables__ = getlibt
        func.__libt__ = getlibt()
        # staticmethods are predicated immediately
        if not isinstancemethod(func):
            func = AssetCached.__predicate__(func)
        return func
    return wrapper


class AssetCached:
    def __new__(cls, *args, **kwargs):
        r"""
        Check attributes on object creation to predicate asset caching function.

        This must be done in order to resolve string names and cache dict occupation based
        on instances and not type based.

        If we don't do this, the calls from different instances of the same type will
        be convoluted into a singular name space.
        """
        obj = super().__new__(cls)
        for item_name in dir(obj):
            item = getattr(obj, item_name, None)
            if callable(item):
                # __getliables__ is a marker that this function is decorated
                is_liable = getattr(item, '__getliables__', False)
                if is_liable is not False:
                    primer = item.__getliables__()
                    setattr(obj, item_name, AssetCached.__predicate__(item, __getliables__ = lambda: [getattr(obj, name) if isinstance(name, str) else name for name in primer]))
        return obj

    @staticmethod
    def __predicate__(func, __getliables__: Supplier=None):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if ASSET_CACHE.get(func) is None or wrapped.__libt__ != wrapped.__getliables__():
                ASSET_CACHE[func] = func(*args, **kwargs)
                wrapped.__libt__ = wrapped.__getliables__()
            return ASSET_CACHE[func]
        wrapped.__getliables__ = __getliables__ or func.__getliables__
        wrapped.__libt__ = func.__libt__
        return wrapped

