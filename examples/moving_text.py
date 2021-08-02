from PyAscii.screen import Displayable
from PyAscii import Model, Screen, Resolutions

screen = Screen(resolution=Resolutions._60c)


@screen.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    my_model = Model("PyAscii/art/words.txt")
    my_model.rect.x += 1
    mover = 0.003
    while True:
        my_model.rect.y += mover
        if my_model.rect.bottom > screen.resolution.height:
            mover = -1 * abs(mover)
        elif my_model.rect.top < 0:
            mover = abs(mover)
        screen.blit(my_model)
        screen.refresh()


screen.run(debug=True, show_fps=True)
