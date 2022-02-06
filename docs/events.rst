Events
=======

Two primary classes that conclude events are :class:`Event` and :class:`EventListener`.
An event can be made by creating an instance of :class:`Event`. If you want a
broader control over the various methods of the events, you can always subclass
and override.

Internal Events
----------------

Internal events are instances of :class:`Event` and is as listed..

================= =============================== ===============================
Event Name         Signature                       Description
================= =============================== ===============================
on_start           None                            As soon as the screen is made
on_terminate       exit_code :obj:`int`            Fatal signal is caught
on_resize          None                            Terminal resize
on_key_press       key: :obj:`Keyboard.Keys`       Keyboard key is pressed
on_key_release     key: :obj:`Keyboard.Keys`       Keyboard key is released
on_mouse_click     button: :obj:`Mouse.Buttons`    Mouse button is pressed
on_mouse_release   button: :obj:`Mouse.Buttons`    Mouse button is released
================= =============================== ===============================


Signature is the proposed function signature for the event handler.
There are several ways we can listen to an internal event depending on the situation.
We can use the :obj:`Event.listen` method and pass in the name of the internal
event to be listened.

.. code:: py

   from Asciinpy.events import Event, ON_KEY_PRESS
   from Asciinpy.devices import Keyboard

   @Event.listen(ON_KEY_PRESS)
   def handler(key: Keyboard.Keys):
       print("This function is called when a key is pressed.")

The name provided is looked-up inside the globals of `events` module. This means
that non-internal events as presumably won't be found! (don't be injecting them
into events now..) we will address how to deal with user events in a moment.

The example provided works fine as long as the function is a staticmethod.
When dealing with classmethods, although we can use the same decorator the way
we did, the class that the classmethod belongs to must be subclassed under
:class:`EventListener`. In most cases where you subclass :class:`Window` your
class will automatically be an event listener.

.. code:: py

   from Asciinpy.events import Event, EventListener, ON_KEY_PRESS
   from Asciinpy.devices import Keyboard

   class Widget(EventListener):
       @Event.listen(ON_KEY_PRESS)
       def handler(self, key: Keyboard.Keys):
           print("This bound-method is called when a key is pressed")

User Events
------------

Creating an event is as easy as making an instance of :class:`Event` or any of
your subclasses of it. We cannot necessarily use the name look-up method so we
can directly pass in the event instance into :obj:`Event.listen` method. You can
then call all event listeners of your event simply by calling :obj:`Event.emit`
with the targetted signature.

.. code:: py

   from Asciinpy.events import Event

   my_event = Event()

   @Event.listen(my_event)
   def handler():
       print("This function is called when my_event is emitted.")

   my_event.emit() # adding args to the call will be passed onto listeners

In cases where your handler needs `self`, make sure that your classes are event
listeners.


Functional Device Events
-------------------------

.. code:: py

   # Define a user loop for the screen and accept a screen parameter, this is of
   # type Screen.
   @window.loop()
   def my_loop(screen: Screen):
       # screen.events() captures all listenable device events and it should be
       # called before analysis
       e = screen.events()
       if Keyboard.pressed is Keyboard.Keys.RightArrow:
           ...
