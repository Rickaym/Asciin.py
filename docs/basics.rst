Fundamentals
===============
The :class:`Asciinpy.Window` class handles the OS dependencies and provides a way to instantiate the game loop through a decorator in functional programming, and when subclassing the window class, the game loop function should be named `loop`.


`E.g. 1 Functional`
.. code:: py

   from Asciinpy import Window

   window = Window(...)


There are two main modes to run a window, by calling either of :obj:`Asciinpy.Window.replay` or :obj:`Asciinpy.Window.run`.

Run
----
The run method begins a real-time rendering mode that has a game loop defined.
As described previously, there are two ways you can instantiate the game loop.
1. You can define a function with a given signature of one parameter and decorated with :obj:`Asciinpy.Window.loop`.

The game loop must accept a single parameter of type :class:`Asciinpy.Screen`, it will raise an error if the signature is incorrect.

.. note::

   The client loop is only executed once and returned during the call on run. This means any looping must be done within the function.

`E.g. 1.2`

.. code:: py

   @window.loop()
   def game_loop(screen):
       pass

   window.run()

2. Subclassing the window instance

.. code::py

   class Game(Window):
      # the game loop must be named loop
      def loop(screen):
         pass

There are a few customizations you can make when running a game loop. This includes with and without sysdout.
For instance rendering frame headless to get an animation and have it fetched from the attribute :obj:`Asciinpy.Window._frame_log`.

Replay
-------
The replay method simply covers plain iteration of a recorded ascii string array of similar resolutions.

`E.g. 1.3`

.. code:: py

   window.replay(["frame 1", "frame 2", "frame 3"], fps=1)

Planes
=======
A Plane is a
Models, they are shapes, angles, text, diagrams, spheres and circles.
Every model inherits from the :class:`Asciinpy.Plane` that provides an interface for a variety of things necessary for subsystem interactions to the model.

There are two ways to create your own models.

1. Subclassing.

When subclassing :class:`Asciinpy.Plane` you are provided a full set of methods that a model should traditionally have such as :obj:`Asciinpy.Plane.blit` and :obj:`Asciinpy.Plane.collides_with`.
These methods can be overidden but avoid it if possible.

`E.g. 2`

.. code:: py

   from Asciinpy import Plane

   class MyModel(Plane):
      def blit(self, ...): pass
         # overrides the inner blitting method of the model

      def collides_with(self, ...): pass
         # overrides the inner collision checking method


2. Instantiating a new Plane object

Taking a closer look to :obj:`Asciinpy.Plane.__init__` you will understand that all the built-in models calls this method somewhere during instantiation.

You can do the same and acquire a function model. The **__init__** method takes a few parameters such as *path* and *image*.
providing either is enough to make a model from scratch.

`E.g. 2.2`

.. code:: py

   from Asciinpy import Plane

   my_model = Plane(image="ABBBBBBBB\nABBBBBBB")
