from PyAscii.screen import Displayable
from PyAscii import Model, Square, Screen, Resolutions

screen = Screen(resolution=Resolutions._60c)


@screen.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    my_square = Square((0, 0), 10, texture="@")
    velocity = [0.02002, 0.02002]
    while True:
        my_square.rect.y += velocity[1]
        my_square.rect.x += velocity[0]

        if round(my_square.rect.y) < 0:
            velocity[1] = abs(velocity[1])
        elif (
            round(my_square.rect.y) + (my_square.length // 2) > screen.resolution.height
        ):
            velocity[1] = -velocity[1]

        if round(my_square.rect.x) < 0:
            velocity[0] = abs(velocity[0])
        elif round(my_square.rect.x) + my_square.length > screen.resolution.width:
            velocity[0] = -velocity[0]

        screen.blit(my_square)
        screen.refresh()


screen.run(debug=False)
