import sys

from Asciinpy.screen import Screen, Window
from Asciinpy.values import Resolutions
from Asciinpy._2D import Square

# Define a window
window = Window(resolution=Resolutions._60c)

@window.loop()
def game_loop(screen: Screen) -> None:
    coordinate = (0, 0)
    length = 8
    texture = "%"
    square = Square(coordinate, length, texture)
    while True:
        screen.blit(square)
        screen.refresh()

if __name__ == "__main__":
   window.run()
   sys.exit(0)
