"""
THIS IS ON THE WORKS AND NOT STABLE
"""
from Asciinpy import Screen, Resolutions, Window
from Asciinpy._2D import Mask
from Asciinpy.geometry import Matrix
from random import randint, choice

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen):
    # type: (Screen) -> None

    # Create a pixel painter object, this creates a blank canvas in the given size to draw onto
    # this is a great way when editing each pixels one by one (which we're about to)
    rain_model = Mask(screen)

    # Make a list to keep track of each drizzle
    matrixes = []

    # simple tick value to randomly make matrixes
    tick = 0
    while True:
        # Make a new matrix drop every 200 ticks
        if tick % 200 == 0:
            matrixes.append(Matrix(randint(0, 59), 0, randint(3, 6)))
            tick = 1

        # Since we'll be removing certain drizzles when overbound, it's necessary to loop through
        # a different reference to the matrixes list. (bad idea to remove elements from the list
        # currently being looped)
        for ent in list(matrixes):
            # lower down the drizzles
            ent.y += 0.1

            # the drizzle had entirely gone off screen
            if ent.z > screen.resolution.height:
                matrixes.remove(ent)
            else:
                # if the uppermost pixel trail passes the size, it gets cleaned up
                if ent.z > 0:
                    rain_model.draw(
                        " ", (ent.x,  ent.z)
                    )
                # if the bottomost y value is still in bounds, we will draw the subsequent character
                if ent.y < screen.resolution.height:
                    try:
                        rain_model.draw(
                            choice(["0", "1"]),
                            (ent.x, ent.y),
                        )
                    except IndexError:
                        pass

        tick += 1
        screen.blit(rain_model)
        # Refresh the screen to render new blits
        screen.refresh()


# Runs the window
window.run(show_fps=False)
