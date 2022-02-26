from pickle import NONE
import random
import sys

from math import pi
from Asciinpy.values import Color
from Asciinpy.screen import Screen, Window
from Asciinpy.devices import Keyboard, Mouse
from Asciinpy._2D import Mask, Tile, Plane, Text
from Asciinpy.values import Resolutions
from string import ascii_letters

ascii_letters = ascii_letters.replace(' ', '')

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions.Basic)

TETRIS_BLOCKS = (
    "####",
    "#\n#\n#\n#",
    "#\n####",
    "#\n#\n#\n##"
)

LOGO = """
### ### ### #`\ ### +=-
 $  $-   $  #-#  $  #=#
 #  ###  #  ; \ ### -=+
"""

# Define a user loop for the screen and accept a screen parameter, this is of type Screen.
@window.loop()
def my_loop(screen: Screen):
    Mouse.Keys.Left
    GRAY = Color.background(128, 128, 128)
    LEFT_BORDER = 45
    RIGHT_BORDER = 3
    LOGO_PLANE = Plane(LOGO, (13, 0))
    BORDERS = (Tile((1, 1), (RIGHT_BORDER, 30), "#", GRAY),
               Tile((LEFT_BORDER, 1), (3, 30), "#", GRAY),
               Tile((1, 1), (60, 3), "#", GRAY),
               Tile((LEFT_BORDER, 30), (60, 3), "#", GRAY),
               Tile((58, 1), (3, 30), "#", GRAY))
    score = Text((52, 28), "00")

    is_next_turn = True
    controlling_block = None
    dormant_blocks = []

    while True:
        if is_next_turn is True or controlling_block is None:
            img = random.choice(TETRIS_BLOCKS)
            controlling_block = Mask(image=img.replace("#", random.choice(ascii_letters)),
                                     coordinate=(random.randint(RIGHT_BORDER+3, LEFT_BORDER-3), 1))
            is_next_turn = False

        if controlling_block:
            screen.blit(controlling_block)
            controlling_block.y += 0.01

        stoppage = False
        for block in list(dormant_blocks):
            if controlling_block.collides_with(block) and not stoppage:
                dormant_blocks.append(controlling_block)
                controlling_block.y += -1
                is_next_turn = True
                stoppage = True
            screen.blit(block)

        if controlling_block.y+(controlling_block.dimension[1]-1) >= screen.height:
            dormant_blocks.append(controlling_block)
            is_next_turn = True

        screen.events()
        if Keyboard.pressed is Keyboard.Keys.RightArrow and controlling_block.x+controlling_block.dimension[0] < LEFT_BORDER:
            controlling_block.x += 1
        elif Keyboard.pressed is Keyboard.Keys.LeftArrow and controlling_block.x > RIGHT_BORDER+1:
            controlling_block.x += -1
        elif Keyboard.pressed is Keyboard.Keys.Return:
            controlling_block.y += 3
        elif Keyboard.pressed is Keyboard.Keys.UpArrow:
            controlling_block.rotate(pi/2)
        elif Keyboard.pressed is Keyboard.Keys.DownArrow:
            controlling_block.rotate(-pi/2)

        for b in BORDERS:
            screen.blit(b)

        screen.blit(score)
        screen.blit(LOGO_PLANE)
        # Refresh the screen to render new blits
        screen.refresh()

if __name__ == "__main__":
    # Runs the window
    window.run()
    sys.exit(0)