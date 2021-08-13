from .globals import SINGLE_PRINT_FLAG

try:
    from typing import Any, List, Union, Callable
except ImportError:
    pass


def beautify(frame, screen):
    # type: (Union[str, List[str]], Any) -> str
    """
    Maps an uncut frame into different pieces with newline characters to make it
    readable without perfect resolution.

    Args:
        frame (Union[str, List[str], Displayable]): The frame to be converted from newline characters to a straight line.
        screen (Displayable): The screen where this frame is taken from.
    """
    new_frame = list(frame)
    for h in range(screen.height):
        dist = h * screen.width
        new_frame[dist] = new_frame[dist] + "\n"

    return "".join(new_frame)


def reverse_beautify(frame, screen):
    # type: (Union[str, List[str]], Any) -> str
    """
    Maps an newline oriented frame into a continuous frame with white spaces.

    Args:
        frame (Union[str, List[str], Displayable]): The frame to be converted from newline characters to a straight line.
        screen (Displayable): The screen where this frame is taken from.

    TODO: Newline detection isn't resolution friendly so it's broken
    """

    i = 0
    new_frame = list(frame)
    for char in frame:
        if char == "\n":
            padding = abs(screen.resolution.width - (i % screen.resolution.width))
            new_frame[i] = " " * padding
            i += padding
        else:
            i += 1
    return new_frame


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
    A decorator that raises a DeprecationWarning when the decorated function
    is called.
    """

    def wrapper(*args, **kwargs):
        raise DeprecationWarning(
            f"{callable.__name__} is deprecated, although fine for usage, consider other alternatives as this callable may be less optimized."
        )

    return wrapper


def write_collision_state(screen, self_frame, other_frame):
    """
    Helps tracking collision states by writing it onto a file IO.
    Uses a global flag to make sure it doesn't write a thousand times.

    Args:
        screen (Displayable): The screen where this is taking place.
        self_frame (List[str]): The frame of itself.
        other_frame (List[str]): The frame of the other model.
    """
    # type: (Displayable, List[str], List[str]) -> None
    global SINGLE_PRINT_FLAG
    if SINGLE_PRINT_FLAG is False:

        SINGLE_PRINT_FLAG = True
        with open("self_frame.txt", "w") as f:
            f.write(beautify(self_frame, screen))

        with open("model_frame.txt", "w") as f:
            f.write(beautify(other_frame, screen))
