"""
Contains different definitions of blitting a model onto a frame with `model` and `screen` given.
Different models can pick best fitting render methods circumstantially.
"""

try:
    from typing import Any, Optional, Tuple, List
except ImportError:
    pass


def rect_and_charpos(model, screen, empty=False):
    # type: (Any, Any, Optional[Tuple[int, int]], bool) -> List[str]
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
    placed = 0
    for char in pixels:
        if loc < 0:
            continue
        if char == "\n":
            loc += screen.resolution.width - placed
            placed = 0
            continue
        try:
            frame[loc] = char
        except IndexError:
            continue
        else:
            placed += 1
            loc += 1
    return frame


def rect_and_modelen(model, screen, empty=False):
    # type: (Any, Any, Optional[Tuple[int, int]], bool) -> List[str]

    """
    Figures out the positions of characters by using the position of the character in the model
    image and it's desired dimensions to guess where it is on the screen.

    The only time you would want to use this is if you somehow cannot have newline characters in your image.

    Time Complexity of this method is O(n) where n is
    the total amount of characters in a model image."""
    frame = list(screen._frame) if not empty else list(screen.emptyframe)

    for row in range(model.rect.dimension[1]):
        for col in range(model.rect.dimension[0]):
            loc = (
                round(model.rect.x)
                + col
                + (screen.resolution.width * row)
                + round(model.rect.y) * screen.resolution.width
            )
            try:
                frame[loc] = model.texture
            except IndexError:
                pass
    return frame


def slice_fit(model, screen):
    """
    Fits text onto the current frame.
    An adaptation of how the screen blits it's menubar etc natively.

    Extremely optimized.

    Time Complexity: O(n) where n is len(TEXT)
    """
    point = model.rect.x + (screen.resolution.width * model.rect.y)
    if point < 0:
        point = screen.resolution.width + point
    return (
        screen._frame[:point]
        + list(model.image)
        + screen._frame[point + len(model.image) :]
    )
