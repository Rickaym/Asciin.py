"""
Basic Example for using the PixelPainter class to draw onto any given pixel of the screen.

PixelPainter doesn't directly create an imprint onto the frame. It keeps a reference frame inside
itself that the user draw onto. Only when it is blitted that the pixel painter localizes it's
canvas onto the screen frame. Even then, it is rendered like every other Model.
"""
import sys

from Asciinpy.screen import Screen, Window, Resolutions

from random import random, choice
from string import ascii_letters

from Asciinpy.utils import Profiler

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the scree and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen: Screen):
    # Create a PixelPainter class to keep a reference frame
    while True:
        # Randomly draw ascii letters onto the canvas
        screen.draw(
           (int(random() * screen.width), int(random() * screen.height)),
           choice(ascii_letters),
           #color=Color.FORE(randint(0, 255), randint(0, 255), randint(0, 255))
        )
        # Refresh the screen to render new blits
        screen.refresh()

if __name__ == "__main__":
    # Runs the window
    with Profiler("file.txt"):
        window.run(show_fps=True)
    sys.exit(0)