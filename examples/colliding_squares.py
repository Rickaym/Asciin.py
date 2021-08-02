from PyAscii.screen import Displayable
from PyAscii import Square, Screen, Resolutions

screen = Screen(resolution=Resolutions._60c)


def manage_collisions(velocities, i, square, other_squares):
    for other in other_squares:
        if square.collides_with(other):
            if abs(square.rect.right - other.rect.left) <= 5:
                velocities[i][0] = -abs(velocities[i][0])
            elif abs(square.rect.left - other.rect.right) <= 5:
                velocities[i][0] = abs(velocities[i][0])
            if abs(square.rect.top - other.rect.bottom) <= 5:
                velocities[i][1] = abs(velocities[i][1])
            elif abs(square.rect.bottom - other.rect.top) <= 5:
                velocities[i][1] = -abs(velocities[i][1])
        else:
            continue
    return velocities


@screen.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    squares = [
        Square((0, 0), 6, texture="@"),
        Square((0, 24), 10, texture="&"),
        Square((24, 0), 6, texture="^"),
        Square((40, 0), 8, texture="L"),
    ]
    STATIC = 0.04
    velocities = [
        [STATIC, STATIC],
        [STATIC, STATIC],
        [STATIC, STATIC],
        [STATIC, STATIC],
    ]
    while True:
        for i, square in enumerate(squares):
            screen.blit(square)
            square.rect.x += velocities[i][0]
            square.rect.y += velocities[i][1]

            if round(square.rect.y) < 0:
                velocities[i][1] = -1 * velocities[i][1]
            elif round(square.rect.y) + (square.length // 2) > screen.resolution.height:
                velocities[i][1] = -1 * velocities[i][1]

            if round(square.rect.x) < 0:
                velocities[i][0] = -1 * velocities[i][0]
            elif round(square.rect.x) + square.length > screen.resolution.width:
                velocities[i][0] = -1 * velocities[i][0]
            manage_collisions(velocities, i, square, squares)
        screen.refresh()


screen.run(debug=False, show_fps=True)
