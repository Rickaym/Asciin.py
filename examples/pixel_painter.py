"""
Basic Example for using the PixelPainter class to draw onto any given pixel of the screen.

PixelPainter doesn't directly create an imprint onto the frame. It keeps a reference frame inside
itself that the user draw onto. Only when it is blitted that the pixel painter localizes it's
canvas onto the screen frame. Even then, it is rendered like every other Model.
"""
import sys

from Asciinpy.utils import Color
from Asciinpy.screen import Screen, Window
from Asciinpy.values import Resolutions
from Asciinpy._2D import Mask

from random import random, choice, randint
from string import ascii_letters

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen: Screen):
    # Create a PixelPainter class to keep a reference frame
    canvas = Mask(screen)
    while True:
        # Randomly draw ascii letters onto the canvas
        canvas.draw(
           choice(ascii_letters),
           (int(random() * screen.width), int(random() * screen.height)),
           color=Color.FORE(randint(0, 255), randint(0, 255), randint(0, 255))
        )
        # Blit the canvas onto the screen
        screen.blit(canvas)
        # Refresh the screen to render new blits
        screen.refresh()

if __name__ == "__main__":
    # Runs the window
    window.run(show_fps=True)
    sys.exit(0)