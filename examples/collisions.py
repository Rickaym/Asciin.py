"""
Simple collisions system with squares.
"""

from Asciinpy.screen import Screen, Window
from Asciinpy.values import Resolutions
from Asciinpy._2D import Square

from typing import Iterable, List

window = Window(resolution=Resolutions.Basic)

def manage_collisions(velocities: List[List[float]], i: int, square: Square, other_squares: Iterable[Square]) -> List[List[float]]:
    for other in other_squares:
        # Any subclass of `Collidable` has the collides_with method and `Square`
        # happens to be one of them.
        # When you check a collisions for a square and itself, it returns False.
        tolerance = 7
        if square.collides_with(other):
            if abs(square.right - other.left) <= tolerance:
                velocities[i][0] = -abs(velocities[i][0])
            elif abs(square.left - other.right) <= tolerance:
                velocities[i][0] = abs(velocities[i][0])

            if abs(square.top - other.bottom) <= tolerance:
                velocities[i][1] = abs(velocities[i][1])
            elif abs(square.bottom - other.top) <= tolerance:
                velocities[i][1] = -abs(velocities[i][1])

    # returns the altered velocities
    return velocities

@window.loop()
def my_loop(screen: Screen):
    """
    This is a user game loop that must accept a `Screen` parameter.
    """
    squares = (
        Square((2, 4), 5, texture="#"),
        Square((9, 4), 6, texture="."),
        Square((5, 5), 7, texture="+"),
        Square((2, 18), 8, texture=","),
        )

    SPEED = 0.06902
    velocities = [[SPEED, SPEED] for _ in squares]

    while True:
        for i, square in enumerate(squares):
            square.x += velocities[i][0]
            square.y += velocities[i][1]

            # Check for boundary collisions
            if round(square.y) < 0:
                velocities[i][1] = -1 * velocities[i][1]
                square.y = 0
            elif round(square.y) + (square.length // 2) > screen.resolution.height:
                velocities[i][1] = -1 * velocities[i][1]
                square.y = screen.resolution.height - (square.length // 2)

            if round(square.x) < 0:
                velocities[i][0] = -1 * velocities[i][0]
                square.x = 0
            elif round(square.x) + square.length > screen.resolution.width:
                velocities[i][0] = -1 * velocities[i][0]
                square.x = screen.resolution.width - square.length

            # Check for collisions between each other and update the velocity matrix
            velocities = manage_collisions(velocities, i, square, squares)

            screen.blit(square)

        screen.refresh()

window.enable_debug()

if __name__ == "__main__":
    window.run()
