[![pipenv](https://img.shields.io/pypi/pyversions/Asciin.py.svg)](https://www.python.org/)
[![release](https://img.shields.io/pypi/v/Asciin.py.svg)](https://pypi.org/project/Asciin.py/)
![platform](https://img.shields.io/static/v1?label=platforms&message=Windows+|+Linux+|+OSX&color=informational)
[![documentation status](https://readthedocs.org/projects/asciinpy/badge/?version=latest)](https://asciinpy.readthedocs.io/en/latest/?badge=latest)

# Asciin.py

![logo](https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/inverted_logo.png)

A 2D and 3D Ascii Game Engine written purely in Python from ground up with zero external dependencies.
Supports Python versions starting from 2.7 to 3.9.

---

**[ReadTheDocs](https://asciinpy.readthedocs.io/en/latest/)** | **[PyPi Project](https://pypi.org/project/Asciin.py/)** |
**[Github Repo](https://github.com/Rickaym/Asciin.py)** |
**[Dev server](https://discord.gg/UmnzdPgn6g)**

---

### Status Demo

1. **Matrixes Patterns**
   <br> An example in working with `PixelPainters`.

![demo](https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/LuckyDevStuff_render.gif)

2. **Colors and Collisions** *NEW in 0.2.0 unreleased*
   <br> An Example in working with `Color` and `collides_with` for basic 2D planes.

![demo](https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/colors_and_collisions.gif)

### Installing

**Python 2.7 or higher is required**

```js
// Windows
py -m pip install -U asciin.py

// Linux/macOS
python -m pip install -U asciin.py
```

### Quick Start

1. Instantiate a `Asciinpy.Window` class with the desired values.

2. Define your game loop and decorate it with the `Asciinpy.Window.loop` decorator that should accept one parameter of type `Screen`.

3. Write some fancy code with or without built-in models to render.

4. Call the `Asciinpy.Window.run` method!

```py
from Asciinpy import Screen, Window, Resolutions
from Asciinpy._2D import Square
# Define a window

window = Window(resolution=Resolutions._60c)

@window.loop()
def game_loop(screen): # type: (Screen) -> None
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
