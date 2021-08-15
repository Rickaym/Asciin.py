"""
Basic Example for using the PixelPainter class to draw onto any given pixel of the screen.

PixelPainter doesn't directly create an imprint onto the frame. It keeps a reference frame inside
itself that the user draw onto. Only when it is blitted that the pixel painter localizes it's
canvas onto the screen frame. Even then, it is rendered like every other Model.
"""
from Asciinpy import Displayable, Resolutions, Window
from Asciinpy._2D import PixelPainter
from random import random, choice
from string import ascii_letters

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.
@window.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    # Create a PixelPainter class to keep a reference frame
    canvas = PixelPainter(screen)
    while True:
        # Randomly draw ascii letters onto the canvas
        # canvas.draw(
        #    choice(ascii_letters),
        #    xy=(int(random() * screen.width), int(random() * screen.height)),
        # )

        canvas.draw("a", xy=(1, 9))
        # Blit the canvas onto the screen
        screen.blit(canvas)
        # Refresh the screen to render new blits
        screen.refresh()


# Runs the window
window.run(show_fps=True)
