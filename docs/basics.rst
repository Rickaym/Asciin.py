Fundamentals
===============
The :class:`~Asciinpy.screen.Window` class handles the OS dependencies and
provides a way to instantiate the game loop through a decorator in functional
programming, and when subclassing the window class, the game loop function
should be named `loop`.

There are two main methods to run a window, either as a replay or as a runnable
(:obj:`~Asciinpy.screen.Window.replay` or :obj:`~Asciinpy.screen.Window.run`).1

Run
----
Running a window initiates a real-time frame rendering that has a game loop defined.
As described previously, there are two ways you can instantiate the game loop.
1. You can define a function with a given signature of one parameter and decorated
with :obj:`~Asciinpy.screen.Window.loop`.

The game loop must accept a single parameter of type :class:`Asciinpy.screen.Screen`,
it will raise an error if the signature is incorrect.
The game loop is executed once and returned during the call on run and it is
expected for the developer to create a gameloop within the function.

`E.g. 1.1`

.. code:: py

   from Asciinpy import Window

   window = Window(...)

   @window.loop()
   def game_loop(screen):
       # Looping
       while True:
         ...

   if __name__ == "__main__":
      window.run()


1. Subclassing the window instance

`E.g. 1.2`

.. code:: py

   class Game(Window):
      # the game loop must be named loop
      def loop(screen):
         pass

   if __name__ == "__main__":
      game = Game()
      game.run()

There are a few customizations you can make when running a game loop.
This includes with and without stdout. Asciin.py also by default provides a way
to display FPS through the `show_fps` boolean flag in :obj:`~Asciinpy.screen.Window.run`.

Replay
-------
The replay method simply covers plain iteration of a recorded ascii string array of similar resolutions.

`E.g. 1.3`

.. code:: py

   window.replay(["frame 1", "frame 2", "frame 3"], fps=1)

Planes
=======
These are the most simple 2D objects available for basic static shapes like
:class:`~Asciinpy._2D.objects.Squares`, :class:`~Asciinpy._2D.objects.Tiles` and
:class:`~Asciinpy._2D.objects.Text`. Planes support basic transformation such as
movement and enlargement through supplementary methods. It cannot be trusted for
Plane subclasses to recalculate self attributes when complex transformation is imposed
instead, developers are recommended to override and change these attributes themselves --
this is particularly because Planes are meant to speedy and simplified. Consider using
:class:`~Asciinpy._2D.definitors.Mask` that we'll touch on next up.

There are two ways to create your own Planes.

1. Instantiating a new Plane object with an image kwarg

Taking a closer look to :obj:`Asciinpy.Plane.__init__`, the `image` attribute
is not expected to change unless enlargement is invoked. The dimensions of Plane
is also deduced by the given image.

`E.g. 2`

.. code:: py

   from Asciinpy import Plane

   my_model = Plane(image="##########"
                        "\n##########")


The example above will create our own Plane object with the rectangle image.

2. Instantiating by subclassing

Regardless of how the internals are changed through subclassing, developers should
call `super().__init__()` with the given kwargs. A similar example to the above
would look something like this:

`E.g. 2.2`

.. code:: py

   from Asciinpy import Plane

   class MyModel(Plane):
      def __init__(self, coordinate):
         super().__init__(coordinate, "##########"
                                    "\n##########")
      def blit(self, ...): pass
         # overrides the inner blitting method of the model

      def collides_with(self, ...): pass
         # overrides the inner collision checking method inherited from `Collidable`

   my_model = MyModel()
