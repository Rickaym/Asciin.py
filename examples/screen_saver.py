"""
Recreation of the classic DVD screensaver

PixelPainter doesn't directly create an imprint onto the frame. It keeps a reference frame inside
itself that the user draw onto. Only when it is blitted that the pixel painter localizes it's
canvas onto the screen frame. Even then, it is rendered like every other Model.
"""
from Asciinpy.geometry import roundi
from Asciinpy.screen import Color
import sys

from Asciinpy import Screen, Window, Resolutions
from Asciinpy._2D import Plane

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen):
    # type: (Screen) -> None
    # Make the DVD_logo model out of scratch with the path
    with open("./examples/DVD_logo.txt", "r") as f:
        img = f.read()
        lines = img.split('\n')
        DVD_logo = Plane(image=img, dimension=(len(lines[0]), len(lines)))
        DVD_logo.get_rect()
    # Map the velocity for the mmovement
    velocity = [0.0302, 0.0302]
    while True:
        DVD_logo.rect.y += velocity[1]
        DVD_logo.rect.x += velocity[0]

        # Check for border collisions and flip signs
        if roundi(DVD_logo.rect.y) < 0:
            velocity[1] = abs(velocity[1])
            DVD_logo.color = Color.FORE.random()
        elif (roundi(DVD_logo.rect.y) + DVD_logo.dimension[1]) > screen.resolution.height:
            velocity[1] = -velocity[1]
            DVD_logo.color = Color.FORE.random()

        if roundi(DVD_logo.rect.x) < -1:
            velocity[0] = abs(velocity[0])
            DVD_logo.color = Color.FORE.random()
        elif (roundi(DVD_logo.rect.x) + DVD_logo.dimension[0]) >= screen.resolution.width-1:
            velocity[0] = -velocity[0]
            DVD_logo.color = Color.FORE.random()

        # Blit the dvd logo onto screen
        screen.blit(DVD_logo)
        # Refresh the screen to render new blits
        screen.refresh()

if __name__ == "__main__":
    # Runs the window
    window.run()
    sys.exit(0)