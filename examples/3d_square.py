from Asciinpy.screen import Color
from __future__ import division
"""
THIS IS ON THE WORKS AND NOT STABLE
"""
from Asciinpy.values import Resolutions
from time import time
from Asciinpy.geometry import project_3D, roundi, rotate_3D
from Asciinpy import Screen, Window
from Asciinpy.utils import Profiler
from Asciinpy._2D import Triangle

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen):
    # type: (Screen) -> None
    coordinates = [
        [[0, 0, 0], [0, 1, 0], [1, 1, 0]],
        [[0, 0, 0], [1, 1, 0], [1, 0, 0]],
        [[1, 0, 0], [1, 1, 0], [1, 1, 1]],
        [[1, 0, 0], [1, 1, 1], [1, 0, 1]],
        [[1, 0, 1], [1, 1, 1], [0, 1, 1]],
        [[1, 0, 1], [0, 1, 1], [0, 0, 1]],
        [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 1], [0, 1, 0], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [1, 1, 1]],
        [[0, 1, 0], [1, 1, 1], [1, 1, 0]],
        [[1, 0, 1], [0, 0, 1], [0, 0, 0]],
        [[1, 0, 1], [0, 0, 0], [1, 0, 0]],
    ]
    zoffset = 6
    scale_factor = 0.3

    w, h = 60, 30
    aspr = h/w
    fov = 14

    length = len(coordinates)
    while True:
        for i in range(length):
            p1rack = list(coordinates[i][0])
            p2rack = list(coordinates[i][1])
            p3rack = list(coordinates[i][2])

            p1rack = rotate_3D(p1rack, (time()-screen._started_at)*0.7, "z")
            p2rack = rotate_3D(p2rack, (time()-screen._started_at)*0.7, "z")
            p3rack = rotate_3D(p3rack, (time()-screen._started_at)*0.7, "z")

            p1rack = rotate_3D(p1rack, (time()+3-screen._started_at)*0.7, "x")
            p2rack = rotate_3D(p2rack, (time()+3-screen._started_at)*0.7, "x")
            p3rack = rotate_3D(p3rack, (time()+3-screen._started_at)*0.7, "x")

            p1rack[2] += zoffset
            p2rack[2] += zoffset
            p3rack[2] += zoffset

            p1 = project_3D(p1rack, aspr, fov)
            p2 = project_3D(p2rack, aspr, fov)
            p3 = project_3D(p3rack, aspr, fov)

            p1.x *= scale_factor * w
            p1.y *= scale_factor * h

            p2.x *= scale_factor * w
            p2.y *= scale_factor * h

            p3.x *= scale_factor * w
            p3.y *= scale_factor * h

            screen.blit(Triangle(
                (roundi(p1.x) - 70, roundi(p1.y)-25),
                (roundi(p2.x) - 70, roundi(p2.y)-25),
                (roundi(p3.x) - 70, roundi(p3.y)-25),
                texture="#"
            ))
        try:
            screen.refresh()
        except RuntimeError:
            return

window.run(show_fps=True, sysdout=True, debug=True)
