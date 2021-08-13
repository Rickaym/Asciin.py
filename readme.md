# Asciin.py

![logo](https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/inverted_logo.png)

A 2D and 3D Ascii game engine written for performance (still under development).

Current docs: **https://asciipy.readthedocs.io/en/latest/**

pypi project: **https://pypi.org/project/Asciin.py/**

Github repository: **https://github.com/Rickaym/Asciin.py**

Development server: **https://discord.gg/UmnzdPgn6g**

### Status Demo

1. **Matrixes Patterns**
   <br> An example in working with PixelPainters.

![demo](https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/LuckyDevStuff_render.gif)

Credits to LuckyDevStuff for the examples ~

More examples [here](https://github.com/Rickaym/Asciin.py/tree/main/examples/).

### Installing

**Python 2.7 or higher is required**

```js
// Windows
py -m pip install -U asciin.py

// Linux/macOS
python -m pip install -U asciin.py
```

### Quick Start

#. Instantiate a `Asciinpy.Window` class with the desired values.

#. Define your game loop and decorate it with the `Asciinpy.Window.loop` decorator that should accept one parameter of type `Displayable`.

#. Write some fancy code with or without built-in models to render.

#. Call the `Asciinpy.Window.run` method!

```py
from Asciinpy import Square, Displayable, Window, Resolutions

# Define a window

window = Window(resolution=Resolutions._60c)

@window.loop()
def game_loop(screen): # type: (Displayable) -> None
coordinate = (0, 0)
length = 8
texture = "%"
Square = Square(coordinate, length, texture)
while True:
screen.blit(Square)
screen.refresh()

window.run()
```

Contact me at Neo#1844 for inquiries.
