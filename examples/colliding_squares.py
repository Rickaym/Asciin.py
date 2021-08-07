"""
Simple collisions system with squares.
"""
from Asciinpy import Square, Displayable, Window, Resolutions

try:
    from typing import Tuple
except ImportError:
    "Python 2.7.2 + compatibility"

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)


def manage_collisions(velocities, i, square, other_squares):
    # type: (Tuple[int, int], int, Square, Square) -> Tuple[int, int]
    for other in other_squares:
        # Squares or any Subclass of `Model` has a `collides_with` method, this can be
        # overidden when making your own model or making a model out of scratch.
        # Here we simply use a the method on other squares
        #
        # When you check a collisions for a square and itself, it returns False

        tolerance = 7
        if square.collides_with(other):
            # When a collision is certain, we need to find where it happened
            # this can be done simply by finding the distances of their points

            if abs(square.rect.right - other.rect.left) <= tolerance:
                velocities[i][0] = -abs(velocities[i][0])
            elif abs(square.rect.left - other.rect.right) <= tolerance:
                velocities[i][0] = abs(velocities[i][0])

            if abs(square.rect.top - other.rect.bottom) <= tolerance:
                velocities[i][1] = abs(velocities[i][1])
            elif abs(square.rect.bottom - other.rect.top) <= tolerance:
                velocities[i][1] = -abs(velocities[i][1])

    # returns the altered velocities
    return velocities


# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.
@window.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    # Make a bunch of squares to simulate collisions
    squares = (
        Square((0, 0), 9, texture="@"),
        Square((0, 24), 10, texture="&"),
        Square((24, 0), 7, texture="^"),
        Square((30, 0), 4, texture="L"),
    )

    # Make a list to appoint each of the squares a movement velocity
    STATIC = 0.03002
    velocities = [[STATIC, STATIC]] * len(squares)

    while True:
        for i, square in enumerate(squares):
            square.rect.x += velocities[i][0]
            square.rect.y += velocities[i][1]

            if round(square.rect.y) < 0:
                velocities[i][1] = -1 * velocities[i][1]
            elif round(square.rect.y) + (square.length // 2) > screen.resolution.height:
                velocities[i][1] = -1 * velocities[i][1]

            if round(square.rect.x) < 0:
                velocities[i][0] = -1 * velocities[i][0]
            elif round(square.rect.x) + square.length > screen.resolution.width:
                velocities[i][0] = -1 * velocities[i][0]

            velocities = manage_collisions(velocities, i, square, squares)

            # Blit the current square in iteration
            screen.blit(square)
        # Refresh the screen to render new blits
        screen.refresh()


# Runs the window
window.run(show_fps=True)
