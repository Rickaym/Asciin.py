from PyAscii.utils import morph
from PyAscii.models import SimpleText
from PyAscii.screen import Displayable
from PyAscii import Screen, Resolutions

screen = Screen(resolution=Resolutions._60c)


@screen.loop()
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
        screen.refresh()


screen.run(debug=True, show_fps=True)
