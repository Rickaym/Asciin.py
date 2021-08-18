import os

from Asciinpy.screen import Color
from Asciinpy.utils import Profiler
from Asciinpy import Displayable, Window
from Asciinpy._2D import Square
from random import randint

size = os.get_terminal_size(1)
res = size.columns, size.lines
window = Window(res)

@window.loop()
def my_loop(screen):
    sq = Square((9, 10), 15, "\u2588")
    sq.rect.texture = "\u2588"
    
    sq.rect.color = Color.FORE(101, 101, 101)
    while True:
        sq.color = Color.FORE(randint(0, 255), randint(0, 255), randint(0, 255))
        screen.blit(sq)
        screen.refresh()

window.run(show_fps=True)
