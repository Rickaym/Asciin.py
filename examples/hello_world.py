from Asciinpy.screen import Screen, Window, Resolutions
from Asciinpy._2D.objects import Text
from Asciinpy.values import Color

window = Window(resolution=Resolutions.Basic)

window.set_title("Example Window Title")
window.set_color(foreground=Color.White, background=Color.Black)


@window.loop()
def my_loop(screen: Screen):
    text = Text(((Resolutions.Basic.width//2)-12, Resolutions.Basic.height//2), "Hello World!")
    while True:
        screen.blit(text)
        screen.refresh()

window.enable_debug()

if __name__ == "__main__":
    window.run()
