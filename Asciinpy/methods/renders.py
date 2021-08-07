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
    loc = round(model.rect.x) + (round(model.rect.y) * screen.resolution.width)
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
    the total amount of characters in a model image."""
    frame = list(screen._frame) if not empty else list(screen.emptyframe)
    pixels = list(model.image)
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
    point = round(model.rect.x) + (screen.resolution.width * round(model.rect.y))
    if point < 0:
        point = screen.resolution.width + point

    frame = screen._frame[:point]
    frame.extend(list(model.image))
    frame.extend(screen._frame[point + len(model.image) :])

    return frame, set(range(point, point + len(model.image)))
