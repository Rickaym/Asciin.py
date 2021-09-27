"""
Simple collisions system with squares.
"""
from Asciinpy.events import Event
import sys

from Asciinpy.utils import Profiler
from Asciinpy.screen import Screen, Window
from Asciinpy.values import Resolutions
from Asciinpy._2D import Square

from random import randint
from typing import List, Tuple

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

@Event.listen("on_start")
def abc(): pass

def manage_collisions(velocities: Tuple[int, int], i: int, square: Square, other_squares: List[Square]) -> Tuple[int, int]:
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

            if abs(square.right - other.left) <= tolerance:
                velocities[i][0] = -abs(velocities[i][0])
            elif abs(square.left - other.right) <= tolerance:
                velocities[i][0] = abs(velocities[i][0])

            if abs(square.top - other.bottom) <= tolerance:
                velocities[i][1] = abs(velocities[i][1])
            elif abs(square.bottom - other.top) <= tolerance:
                velocities[i][1] = -abs(velocities[i][1])

    # returns the altered velocities
    return velocities

# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen: Screen):
    # Make a bunch of squares to simulate collisions
    squares = (
        Square((2, 4), 10, texture="#"),
        )

    STATIC = 0.03902
    velocities = []
    sq = Square((0, 20), 10, texture="@")
    for i in squares:
        velocities.append([STATIC, STATIC])

    while True:
        for i, square in enumerate(squares):
            square.x += velocities[i][0]
            square.y += velocities[i][1]
            #square.color=Color.FORE(randint(0, 255), randint(0, 255), randint(0, 255))

            if round(square.y) < 0:
                velocities[i][1] = -1 * velocities[i][1]
                square.y = 0
            elif round(square.y) + (square.length // 2) > screen.resolution.height:
                velocities[i][1] = -1 * velocities[i][1]
                square.y = screen.resolution.height - (square.length // 2)

            if round(square.x) < 0:
                velocities[i][0] = -1 * velocities[i][0]
                square.x = 0
            elif round(square.x) + square.length > screen.resolution.width:
                velocities[i][0] = -1 * velocities[i][0]
                square.x = screen.resolution.width - square.length

            velocities = manage_collisions(velocities, i, square, squares)

            # Blit the current square in iteration
            screen.blit(square)

        # Refresh the screen to render new blits
        screen.refresh()

if __name__ == "__main__":
    # Runs the window
    with Profiler("stats.txt"):
        window.run(show_fps=True)
    sys.exit(0)
