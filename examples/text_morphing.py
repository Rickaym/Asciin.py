from Asciinpy.utils import morph
from Asciinpy import Window, Resolutions, Displayable
from Asciinpy._2D import SimpleText

# Start by defining a screen object with the desired resolution
window = Window(resolution=Resolutions._60c)

# Define a user loop for the screen and accept a screen parameter, this is of type Displayable.
@window.loop()
def my_loop(screen):
    # type: (Displayable) -> None
    text = SimpleText((10, 20), " ")
    morphs = morph(
        "An example of the morph utils", "pretty simple and straight forward..."
    )
    index = 0
    while True:
        screen.blit(text)
        text.image = morphs[int(round(index))]
        index += 0.006
        if round(index) >= len(morphs):
            index = 0
        try:
            screen.refresh()
        except RuntimeError:
            return


window.run(debug=True)
