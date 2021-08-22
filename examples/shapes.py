"""
Simple collisions system with squares.
"""
from Asciinpy.geometry import roundi
import sys

from Asciinpy.screen import Color
from Asciinpy import Screen, Window, Resolutions
from Asciinpy._2D import Square

try:
    from typing import Tuple
except ImportError:
    pass

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)


# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen):
    # type: (Screen) -> None
    # Make a bunch of squares to simulate collisions
    r = 255
    square = Square((2, 4), 10, color=Color.FORE(roundi(r), 255, 255), texture="#")
    coeff = -0.1
    while True:
        # Blit the square
        screen.blit(square)
        square.color = Color.FORE(roundi(r), 255, 255)
        r += coeff
        if roundi(r) < 0 or roundi(r) > 255:
            coeff = -1 * coeff
        # Refresh the screen to render new blits
        screen.refresh()

if __name__ == "__main__":
    # Runs the window
    window.run()
    sys.exit(0)
