"""
Contains different definitions of blitting a model onto a frame with `model` and `screen` given.
Different models can pick best fitting render methods circumstantially.
"""

from Asciinpy.screen import Color
from ...math import roundi


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
        color = model.color
        if loc < 0 or loc > max_loc:
            continue
        if model.rect.texture:
            if char == "\n":
                color = model.rect.color
                frame[loc - 1] = color + model.rect.texture + Color.FORE(255, 255, 255)
            elif x_depth == 0 or y_depth == 0 or y_depth == (model.dimension[1] - 1) or i == (len(pixels) - 1):
                color = model.rect.color
                char = model.rect.texture
                
        if char == "\n":
            loc += screen.resolution.width - x_depth
            x_depth = 0
            y_depth += 1
            continue
        elif char == " ":
            continue

        try:
            frame[loc] = color + char + Color.FORE(255, 255, 255)
        except IndexError:
            continue
        else:
            occupancy.append(loc)
            
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
