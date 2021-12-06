import sys
import time

from Asciinpy.events import Event
from Asciinpy.devices import Keyboard
from Asciinpy.utils import Color
from Asciinpy._2D import Square, Plane
from Asciinpy import Screen, Window, Resolutions

from random import randint

pipe_bottom = (
r"""|     |
\     /
|     |
\-----/"""
)

pipe_middle = (
r"""
|     |
-_ ___-
- ___ -
|     |
"""
)

pipe_top = (
r"""/_ ___\
|     |
/     \
-__ _ -"""
)

class BotPipe(Plane):
    def __init__(self, coordinate):
        super().__init__()

        self.image = pipe_top+pipe_middle+pipe_middle+pipe_middle
        self.color = Color.FORE(255, 0, 0)
        self.get_rect(coordinate=coordinate)

class TopPipe(Plane):
    def __init__(self, coordinate):
        super().__init__()

        self.image = pipe_middle+pipe_middle+pipe_middle+pipe_bottom
        self.color = Color.FORE(255, 0, 0)
        self.get_rect(coordinate=coordinate)

class Game(Window):
    def __init__(self):
        super().__init__(Resolutions._60c)

        self.top_border = Square((1, 1), (60, 3), "~")
        self.bot_border = Square((1, 28), (60, 3), "~")
        self.visible_pipes = []

    def draw_background(self, screen: Screen):
        screen.blit(self.top_border)
        screen.blit(self.bot_border)

    def draw_pipe(self, screen, tick):
        if tick == 299:
            x = randint(60, 70)
            new_botpipe = BotPipe((x, randint(20, 30)))
            new_toppipe = TopPipe((x, 0))
            self.visible_pipes.extend((new_botpipe, new_toppipe))

        for pipe in list(self.visible_pipes):
            #pipe.rect.x -= 0.01
            #if pipe.rect.x <= -10:
            #    self.visible_pipes.remove(pipe)
            screen.blit(pipe)

    def loop(self, screen: Screen):
        # Main game loop.
        # Make a bunch of squares to simulate collisions
        red_vector = [255, -0.1] # distance, direction
        square = Square((-1, 4), 5, color=Color.FORE(round(red_vector[0]), 255, 255), texture="@")
        tick = 0

        while True:
            if tick == 300:
                tick = 0
            # Blit the square
            self.draw_background(screen)
            #self.draw_pipe(screen, tick)
            screen.blit(square)
            square.color = Color.FORE(round(red_vector[0]), 255, 255)

            if Keyboard.pressed == Keyboard.Keys.RIGHT_ARROW:
                square.rect.x += 1
            elif Keyboard.pressed == Keyboard.Keys.LEFT_ARROW:
                square.rect.x -= 1
            elif Keyboard.pressed == Keyboard.Keys.DOWN_ARROW:
                square.rect.y += 1
            elif Keyboard.pressed == Keyboard.Keys.UP_ARROW:
                square.rect.y -= 1

            red_vector[0] = sum(red_vector)
            if round(red_vector[0]) < 0 or round(red_vector[0]) > 255:
                red_vector[1] = -1 * red_vector[1]
            # Refresh the screen to render new blits
            screen.refresh()
            tick += 1

    @Event.listen("on_key_press")
    def interactive_menu(self, key):
        if key == Keyboard.Keys.F3:
            self.screen.show_fps = not self.screen.show_fps

    @Event.listen("on_start")
    def sleeper(self):
        time.sleep(3)

App = Game()
App.enable_debug()
if __name__ == "__main__":
    # Runs the window
    App.run()
    sys.exit(0)
