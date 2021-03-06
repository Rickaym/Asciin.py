[![pipenv](https://img.shields.io/pypi/pyversions/Asciin.py.svg)](https://www.python.org/)
[![support](https://img.shields.io/discord/793047973751554088?logo=discord)](https://discord.gg/UmnzdPgn6g)
[![release](https://img.shields.io/pypi/v/Asciin.py.svg)](https://pypi.org/project/Asciin.py/)
![platform](https://img.shields.io/static/v1?label=platforms&message=Windows+|+Linux+|+OSX&color=informational)
[![documentation status](https://readthedocs.org/projects/asciinpy/badge/?version=latest)](https://asciinpy.readthedocs.io/en/latest/?badge=latest)


![logo](https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/inverted_logo.png)

A 2D and 3D Ascii Game Engine written purely in Python from ground up with zero external dependencies.
Supports Python versions starting from 3.5.3.


### Status Demo

1. **Matrix Patterns**
   <br> Uses `PixelPainters` and `Matrix`.
<sup>**[code](https://github.com/Rickaym/Asciin.py/tree/main/examples/matrix_patterns.py)**</sup>
<img src="https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/LuckyDevStuff_render.gif" data-canonical-src="https://raw.githubusercontent.com/Rickaym/Asciin.py/main/assets/LuckyDevStuff_render.gif" width="300" height="400" />

2. **Colors and Collisions** *NEW in 0.2.0 unreleased*
   <br> Uses `Color`, `Square` and `collides_with` for basic 2D planes.
<sup>**[code](https://github.com/Rickaym/Asciin.py/tree/main/examples/colors_and_collisions.py)**</sup>
<img src="https://i.gyazo.com/e3a410a475b2b2a81ad40c3426d75e26.gif" data-canonical-src="https://i.gyazo.com/e3a410a475b2b2a81ad40c3426d75e26.gif" width="300" height="400" />

3. **Screen Saver** *NEW in 0.2.0 unreleased*
   <br> Makes a DVD Logo model from scratch and uses `Color`.
<sup>**[code](https://github.com/Rickaym/Asciin.py/tree/main/examples/screen_saver.py)**</sup>
<img src="https://i.gyazo.com/2c457fe5057bfa71559b8cbe96747b28.gif" data-canonical-src="https://i.gyazo.com/2c457fe5057bfa71559b8cbe96747b28.gif" width="300" height="400" />


### Installing

I highly discourage using version `0.1.7`, please wait for `0.2.0`!

**Python 3.5.3 or higher is required**

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
from Asciinpy.screen import Screen, Window
from Asciinpy.values import Resolutions
from Asciinpy._2D import Square

# Define a window
window = Window(resolution=Resolutions.Basic)

@window.loop()
def game_loop(screen: Screen) -> None:
    square = Square(coordinate=(0, 0), length=8, texture="%")
    while True:
        screen.blit(square)
        screen.refresh()

if __name__ == "__main__":
   window.run()
```
