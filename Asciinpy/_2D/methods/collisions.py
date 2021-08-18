"""
Contains different definitions on checking collisions of a model
Different models can pick best fitting collisions checking methods circumstantially.
"""
from ...globals import SCREENS
from ...utils import deprecated, write_collision_state

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
