"""
THIS IS ON THE WORKS AND NOT STABLE
"""
from Asciinpy._2D.objects import Polygon
from Asciinpy import Screen, Resolutions, Window

from random import randint

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.


@window.loop()
def my_loop(screen: Screen):
    tri = Polygon(((2, 15), (15, 15), (15, 25), (2, 25)), texture="#")

    while True:
        screen.blit(tri)
        tri.x += 0.01
        # Refresh the screen to render new blits
        screen.refresh()


window.enable_debug()

# Runs the window
window.run(show_fps=True)
