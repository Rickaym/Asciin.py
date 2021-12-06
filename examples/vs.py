from Asciinpy._2D.definitors import Plane
from Asciinpy.screen import Screen, Window, Resolutions

window = Window(resolution=Resolutions._60c)


@window.loop()
def my_loop(screen: Screen):
    pol = Plane("##########\n########\n###", [4, 4])
    while True:
        screen.blit(pol)
        pol.x += 0.001
        # fig.x, fig.y = 10, 10
        #print(pol.topleft, end="\r")
        screen.refresh()


window.enable_debug()

window.run(show_fps=True)
