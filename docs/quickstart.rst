Quickstart
===========

#. Instantiate a :class:`Asciinpy.Window` class with the desired values.

#. Define your game loop and decorate it with the :obj:`Asciinpy.Window.loop` decorator that should accept one parameter of type :class:`Displayable`.

#. Write some fancy code with or without built-in models to render.

#. Call the :obj:`Asciinpy.Window.run` method!


.. code:: py

   from Asciinpy import Square, Displayable, Window, Resolutions

   # Define a window
   window = Window(resolution=Resolutions._60c)

   @window.loop()
   def game_loop(screen):
       # type: (Displayable) -> None
       coordinate = (0, 0)
       length = 8
       texture = "%"
       Square = Square(coordinate, length, texture)
       while True:
           screen.blit(Square)
           screen.refresh()

   window.run()

.. note::

   Don't forget to blit the objects after creating them or else they won't appear. Not calling the refresh method will also result in freezed frames.
