Fundamentals
===============
To start off, an instantiation of the :class:`Asciinpy.Window` class is required.
It handles the OS dependencies and provides a way to inject a game loop through a decorator.

`E.g. 1`

.. code:: py

   from Asciinpy import Window

   window = Window(resolution: Union[Tuple[int, int], Asciinpy.values.Resolutions], max_framerate: Optional[int] = None)

There are a few methods you can call from this instance; :obj:`Asciinpy.Window.replay` and :obj:`Asciinpy.Window.run`.

Run
----
The run method executes the game loop that has been passed in previously with an internal clock.
It is possible to set a timer for termination, refer to :obj:`Asciinpy.Window.loop` for further information.
Passing in the game loop is as simple as defining a function with a given signature of one parameter and decorated.
The game loop must accept a single parameter of type :class:`Asciinpy.Displayable`, it will raise an error if the signature is incorrect.

.. note::

   The client loop is only executed once and returned during the call on run. This means any looping must be done within the function.

`E.g. 1.2`

.. code:: py

   @window.loop()
   def game_loop(screen):
       pass

   window.run()

There are a few customizations you can make when running a game loop. This includes with and without sysdout. For instance rendering frame headless to get an animation and have it fetched from a hidden attribute :obj:`Asciinpy.Window._frame_log`.

Replay
-------
The replay method simply covers plain iteration of a recorded ascii string array of similar resolutions.

`E.g. 1.3`

.. code:: py

   window.replay(["frame 1", "frame 2", "frame 3"], fps=1)

Models
=======
Models, they are shapes, angles, text, diagrams, spheres and circles.
Every model inherits from the :class:`Asciinpy.Model` that provides an interface for a variety of things necessary for subsystem interactions to the model.

There are two ways to create your own models.

1. Subclassing.

When subclassing :class:`Asciinpy.Model` you are provided a full set of methods that a model should traditionally have such as :obj:`Asciinpy.Model.blit` and :obj:`Asciinpy.Model.collides_with`.
These methods can be overidden but avoid it if possible.

`E.g. 2`

.. code:: py

   from Asciinpy import Model

   class MyModel(Model):
      def __init__(self, ...):
         super().__init__() # necessary

      def blit(self, ...): pass
         # overrides the inner blitting method of the model
         # do this only when you are aware of the consequences

      def collides_with(self, ...): pass
         # overrides the inner collision checking method
         # do this only when you are aware of the consequences



2. Using the **__init__** method.

Taking a closer look to :obj:`Asciinpy.Model.__init__` you will understand that all the built-in models calls this method somewhere during instantiation.

You can do the same and acquire a function model. The **__init__** method takes a few parameters such as *path* and *image*.
providing either is enough to make a model from scratch.

`E.g. 2.2`

.. code:: py

   from Asciinpy import Model

   my_model = Model(image="ABBBBBBBB\nABBBBBBB")

Pixel Painter
--------------
A :class:`Asciinpy.PixelPainter` model is a simple interface to draw over each pixel on the screen.

You can instantiate a pixel painter model by passing in the current :class:`Asciinpy.Displayable`.
After instantiation, the pixel painter takes a copy of the screen with the given coordinates and dimension (if none is given it takes the entire screen - by default the coordinate and the dimension of the model is based on the screen).

You will be drawing onto this frame by making use of :obj:`Asciinpy.PixelPainter.draw` method.
Like every other model, it must be blitted onto screen. Only when it is blitted, the changes in the canvas are rendered onto the screen elegantly.

`E.g. 2.3`

.. code:: py

   from Asciinpy import PixelPainter, Resolutions

   window = Window(Resolutions._60c)

   @window.loop()
   def game_loop(screen):
      canvas = PixelPainter(screen)

      while True:
         canvas.draw("HAHA", xy=(0, 3))

         screen.blit(canvas)
         screen.refresh()

Shapes
--------

Refer to the Api Reference for more information.

============================== ==============================================================================================
Class                             Description
============================== ==============================================================================================
:class:`Asciinpy.Rectangle`      Makes a generic rectangle from **coordinate** and **width**, **height**.
:class:`Asciinpy.Square`         Makes a generic square from **coordinate** and **length**.
:class:`Asciinpy.SimpleText`     Makes a simple model with a text body from **coordinate** and **text**.
:class:`Asciinpy.AsciiText`      Makes an ascii model in the form of a typical text body
============================== ==============================================================================================
