"""
THIS IS ON THE WORKS AND NOT STABLE
"""
from Asciinpy import Displayable, Resolutions, Window
from Asciinpy.twod import PixelPainter
from random import randint, choice

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c, max_framerate=60)


# We will approach this example in an object oriented way
class MatrixDrop:
    def __init__(self, x, y, s) -> None:
        """
        A simple matrix class with x, y and a size value s.

        Every drizzle is controlled by these three attributes - their names should be
        apparent on what they mean.
        """
        self.x = x  # x position
        self._y = y  # y position
        self.s = s  # trail size of drop

    @property
    def z(self):
        # retrieves get the top of the trail, used commonly so it's set as a property
        return self.y - self.s

    @property
    def y(self):
        # rounding if there were any float additions
        return round(self._y)

    @y.setter
    def y(self, value):
        self._y = value


# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.
@window.loop()
def my_loop(screen):
    # type: (Displayable) -> None

    # Create a pixel painter object, this creates a blank canvas in the given size to draw onto
    # this is a great way when editing each pixels one by one (which we're about to)
    rain_model = PixelPainter(screen, (0, 0))

    # Make a list to keep track of each drizzle
    matrixes = []

    # simple tick value to randomly make matrixes
    tick = 0
    while True:
        # Make a new matrix drop every 200 ticks
        if tick % 200 == 0:
            matrixes.append(MatrixDrop(randint(0, 59), 0, randint(3, 6)))
            tick = 1

        # Since we'll be removing certain drizzles when overbound, it's necessary to loop through
        # a different reference to the matrixes list. (bad idea to remove elements from the list
        # currently being looped)
        for ent in list(matrixes):
            # lower down the drizzle
            ent.y += 0.11

            # the drizzle had entirely gone off screen
            if ent.z > screen.resolution.height:
                matrixes.remove(ent)
            else:
                # if the uppermost pixel trail passes the size, it gets cleaned up
                if ent.z > 0 and ent.z < screen.resolution.height:
                    rain_model.draw(
                        " ", distance=(ent.x + ent.z * rain_model.dimension[0])
                    )
                # if the bottomost y value is still in bounds, we will draw the subsequent character
                if ent.y < screen.resolution.height:
                    rain_model.draw(
                        choice(["0", "1"]),
                        distance=(ent.x + ent.y * rain_model.dimension[0]),
                    )

        tick += 1
        screen.blit(rain_model)
        # Refresh the screen to render new blits
        screen.refresh()


# Runs the window
window.run(show_fps=False)
