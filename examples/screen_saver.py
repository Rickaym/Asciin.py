"""
Recreation of the classic DVD screensaver

PixelPainter doesn't directly create an imprint onto the frame. It keeps a reference frame inside
itself that the user draw onto. Only when it is blitted that the pixel painter localizes it's
canvas onto the screen frame. Even then, it is rendered like every other Model.
"""
import sys

from Asciinpy._2D import Plane
from Asciinpy.values import Color
from Asciinpy.screen import Screen, Window, Resolutions

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions.Medium)

# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen):
    # type: (Screen) -> None
    # Make the DVD_logo model out of scratch with the path
    DVD_logo = Plane(
        image="""  shhhhhhhhhy`  `+hhhhhhhyo.
 `yysosmMMmMM/ .hMmoyyooyNMM:
 sMM:  /MMysMd:NMs.NMm` `dMM-
`NMMsshMNs``NMMm- oMMdsyNMd:
.oosso+:`   /Mo`  +oosoo/.
 `-/+syyhdddhdyyhdddhyys+/-`
-mMMMMMMMMM+`   `+MMMMMMMMMm.
  .-/+ossyyhhyyyhhyysso+/-.""",
        coordinate=(20, 15),
    )
    # Map the velocity for the mmovement
    velocity = [0.0302, 0.0302]
    while True:
        DVD_logo.y += velocity[1]
        DVD_logo.x += velocity[0]

        # Check for border collisions and flip signs
        if int(DVD_logo.x) < 0:
            velocity[0] = abs(velocity[0])
            DVD_logo.color = Color.foreground_random()
        elif round(DVD_logo.x + DVD_logo.dimension[0]) > screen.resolution.width:
            velocity[0] = -velocity[0]
            DVD_logo.color = Color.foreground_random()

        if round(DVD_logo.y) < 0:
            velocity[1] = abs(velocity[1])
            DVD_logo.color = Color.foreground_random()
        elif round(DVD_logo.y + DVD_logo.dimension[1]) > screen.resolution.height:
            velocity[1] = -velocity[1]
            DVD_logo.color = Color.foreground_random()

        # Blit the dvd logo onto screen
        screen.blit(DVD_logo)
        # Refresh the screen to render new blits
        screen.refresh()


if __name__ == "__main__":
    # Runs the window
    window.run()
    sys.exit(0)
