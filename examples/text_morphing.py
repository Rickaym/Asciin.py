from AsciiPy.utils import morph
from AsciiPy import Window, Resolutions, Displayable, SimpleText

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.
@window.loop(forcestop=2)
def my_loop(screen):
    # type: (Displayable) -> None
    text = SimpleText((10, 20), " ")
    morphs = morph("You are my friend..", "You are not my enemy...")
    morphs = morph("What the hell are you..?", "You you.. are a devil~")
    index = 0
    while True:
        screen.blit(text)
        text.image = morphs[round(index)]
        index += 0.006
        if round(index) >= len(morphs):
            index = 0
        try:
            screen.refresh()
        except RuntimeError:
            return


window.run(debug=True, show_fps=True)
