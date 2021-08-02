try:
    from typing import Callable, Any, List, Union
except ImportError:
    pass


class HashablePoint:
    pass


def beautify(frame, screen):
    # type: (Union[str, List[str]], Any) -> str
    """
    Maps an uncut frame into different pieces with newline characters to make it
    readable without perfect resolution.
    """
    new_frame = list(frame)
    for i, char in enumerate(frame):
        if (i + 1) % screen.resolution.width == 0:
            new_frame[i] = char + "\n"
    return "".join(new_frame)


def morph(initial_string, end_string, consume="end", loop=True):
    # type: (str, str, str, bool) -> List[str]
    """
    Simply morphs a string onto another and return a string array
    of all the frames needed to be displayed.
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
