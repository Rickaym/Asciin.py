import inspect

from functools import wraps
from io import StringIO
from cProfile import Profile
from pstats import Stats
from itertools import chain
from random import randint
from types import LambdaType
from typing import Any, Iterator, Literal, Tuple, List, Union, Callable

from .values import ANSI
from .globals import FINISHED_ONCE_TASKS, CWD

Supplier = Callable[[], Any]

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
        redirect = StringIO()
        Stats(self.cpf, stream=redirect).sort_stats("time").print_stats()
        with open(self.path, "w") as f:
            f.write(redirect.getvalue().replace(CWD, "", -1))


class CartesianList(list):
    r"""
    A subclass of list to translates coordinate notation (1, 2) to [y][x] notation and starting from 1.

    Supports:
        CartList[1, 2]      equals   list[1][0]
        CartList[1, 2] = 2  equals   list[1][0] = 2
        CartList.flatten()  equals   chain.from_iterable(2DList)
        CartList.copy()     equals   deepcopy(CartList)
    """
    __ignore_oob__ = True

    def __getitem__(self, key) -> Any:
        if isinstance(key, (tuple, list)):
            return super().__getitem__(key[1]-1).__getitem__(key[0]-1)
        else:
            return super().__getitem__(key)

    def __setitem__(self, key, value) -> Any:
        if isinstance(key, (tuple, list)):
            if not (key[1]-1 >= super().__len__() or key[0]-1 >= super().__getitem__(0).__len__() or key[1] <= 0 or key[0] <= 0):
                return super().__getitem__(key[1]-1).__setitem__(key[0]-1, value)
        else:
            return super().__setitem__(key, value)

    def flatten(self) -> Iterator:
        return chain.from_iterable(super().__iter__())


def beautify(dimension: Tuple[int, int], frame: Union[List[str], str]) -> str:
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
    if isinstance(nw_frame[0], str):
        for h in range(dimension[1]):
            nw_frame[h * dimension[0]] += "\n"
    elif isinstance(nw_frame[0], (list, tuple)):
        for i in range(len(nw_frame)):
            nw_frame[i] += ['\n']
    return nw_frame


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


def deprecated(callable: Callable) -> Callable:
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


def asset(getlibt: LambdaType) -> Callable:
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

           @asset(lambda: "self.bomb")
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
        if isinstance(func, property):
            func.fget.__getliables__ = getlibt
            func.fget.__libt__ = getlibt()
        else:
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
        new_cls = None

        # properties must be tampered before class creation
        for item_name, item in vars(cls).items():
            if isinstance(item, property):
                # __getliables__ is a marker that this function is decorated
                is_liable = getattr(item.fget, '__getliables__', False)
                if is_liable is not False:
                    # properties rely on the class method so we need a new type for each
                    # different self-sustaining property
                    if new_cls is None:
                        new_cls = type(cls.__name__, (cls,), {})
                        obj = super().__new__(new_cls)
                    __libt__ = item.fget.__libt__
                    setattr(new_cls, item_name, property(AssetCached.__predicate__(item.fget, AssetCached.__libt_getter__(__libt__, obj))))

        for item_name in dir(obj):
            item = getattr(obj, item_name, None)

            if callable(item):
                is_liable = getattr(item, '__getliables__', False)
                if is_liable is not False:
                    __libt__ = item.__libt__
                    setattr(obj, item_name, AssetCached.__predicate__(item, AssetCached.__libt_getter__(__libt__, obj)))
        return obj

    @staticmethod
    def __libt_getter__(__libt__, obj):
        r"""
        Just a helper function to derive a liability supplier.
        """
        prepared_libt = [libt.split('.')[1:] if isinstance(libt, str) else libt for libt in __libt__]

        return lambda: [getattr(obj, src) if isinstance(src, str) else src for src in prepared_libt]

    @staticmethod
    def __predicate__(func, __getliables__: Supplier=None):
        r"""
        Predicates the given function into a self-sustainingly cached method.
        """
        @wraps(func)
        def wrapped(*args, **kwargs):
            if wrapped.__libt__ != wrapped.__getliables__():
                wrapped.__cached_return__ = func(*args, **kwargs)
                wrapped.__libt__ = [_[:] for _ in wrapped.__getliables__()]
            return wrapped.__cached_return__

        wrapped.__getliables__ = __getliables__ or func.__getliables__
        wrapped.__cached_return__ = None
        wrapped.__libt__ = [_[:] for _ in func.__libt__]
        return wrapped
