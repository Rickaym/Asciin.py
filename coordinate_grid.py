from Asciinpy._2D.objects import Tile, Text
from Asciinpy.screen import Screen, Window
from Asciinpy.values import Color, Resolutions

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions.Basic)

@window.loop()
def my_loop(screen: Screen):
    """
    This is a user game loop that must accept a `Screen` parameter.
    """
    x_axis = Tile((1, 1), (screen.width-2, 1))
    y_axis = Tile((1, 1), (1, screen.height-2))

    emph_origin = Tile((1, 1), (1, 1), color=Color.foreground(255, 0, 0))
    emph_lf = Tile((screen.width-2, 1), (1, 1), color=Color.foreground(255, 0, 0))
    emph_rf = Tile((1, screen.height-2), (1, 1), color=Color.foreground(255, 0, 0))

    origin = Text((1, 0), "0, 0")

    lf_txt = str((screen.width, 0))[1:-1]
    left_flank = Text((screen.width-1-len(lf_txt), 2), lf_txt)

    rf_txt = str((0, screen.height))[1:-1]
    right_flank = Text((3, screen.height-2), rf_txt)
    while True:
        screen.blit(x_axis, y_axis, origin, left_flank, right_flank,
                    emph_origin, emph_lf, emph_rf)
        screen.refresh(log_frames=True)

window.enable_debug()

if __name__ == "__main__":
    window.run()
