from Asciinpy import Displayable, Resolutions, Window
from Asciinpy.amath import M
from Asciinpy.twod import Triangle

from random import randint

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.
@window.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    my_tri = Triangle([22, 3], [22, 23], [5, 23])
    tick = 0
    p_s = [randint(1, 3), randint(1, 3), randint(1, 3)]
    p_b = [randint(1, 3), randint(1, 3), randint(1, 3)]
    while True:
        screen.blit(my_tri)
        if tick == 100:
            tick = 0
            for i, p in enumerate((my_tri.p3, my_tri.p2, my_tri.p1)):
                p[0] += p_s[i]
                p[1] += p_b[i]

                if p[0] >= (screen.width - 1) or p[0] <= 0:
                    p_s[i] *= -1
                if p[1] >= (screen.height - 1) or p[1] <= 0:
                    p_b[i] *= -1
        # Refresh the screen to render new blits
        tick += 1
        screen.refresh()


# Runs the window
window.run(show_fps=True)