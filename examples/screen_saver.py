"""
Recreation of the classic DVD screensaver

PixelPainter doesn't directly create an imprint onto the frame. It keeps a reference frame inside
itself that the user draw onto. Only when it is blitted that the pixel painter localizes it's
canvas onto the screen frame. Even then, it is rendered like every other Model.
"""
from Asciinpy import Displayable, Window, Resolutions
from Asciinpy._2D import Plane

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.
@window.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    # Make the DVD_logo model out of scratch with the path
    DVD_logo = Plane(path="./examples/DVD_logo.txt")
    # Map the velocity for the mmovement
    velocity = [0.02002, 0.02002]
    while True:
        DVD_logo.rect.y += velocity[1]
        DVD_logo.rect.x += velocity[0]

        # Check for border collisions and flip signs
        if round(DVD_logo.rect.y) < 0:
            velocity[1] = abs(velocity[1])
        elif round(DVD_logo.rect.y) + DVD_logo.dimension[1] >= screen.resolution.height:
            velocity[1] = -velocity[1]

        if round(DVD_logo.rect.x) < 0:
            velocity[0] = abs(velocity[0])
        elif round(DVD_logo.rect.x) + DVD_logo.dimension[0] >= screen.resolution.width:
            velocity[0] = -velocity[0]

        # Blit the dvd logo onto screen
        screen.blit(DVD_logo)
        # Refresh the screen to render new blits
        screen.refresh()


# Runs the window
window.run(show_fps=True)
