Quickstart
===========

#. Instantiate a :class:`Asciinpy.Window` class with the required details.

#. Define your game loop and decorate it with the :obj:`Asciinpy.Window.loop` decorator that should accept one parameter of type :class:`Screen`.

#. Write some fancy code with or without built-in models to render.

#. Call the :obj:`Asciinpy.Window.run` method!


.. code:: py

   from Asciinpy.screen import Screen, Window
   from Asciinpy.values import Resolutions
   from Asciinpy._2D import Square

   # Define a window
   window = Window(resolution=Resolutions._60c)

   @window.loop()
   def game_loop(screen: Screen) -> None:
      coordinate = (0, 0)
      length = 8
      texture = "%"
      square = Square(coordinate, length, texture)
      while True:
         screen.blit(square)
         screen.refresh()

   if __name__ == "__main__":
      window.run()

.. note::

   Don't forget to blit the objects after creating them or else they won't appear. Not calling the refresh method will also result in freezed frames.
