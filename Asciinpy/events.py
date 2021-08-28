import signal
import os

from typing import Any, Callable, Union, List

# A consumer is marked as a method that does or doesn't take a self reference and returns nothing.
Consumer = Union[Callable[[Any], None], Callable[[object], None]]


class Event:
    __slots__ = ("callbacks")

    def __init__(self):
        self.callbacks: List[Consumer] = []

    def on_emit(self, func: Consumer):
        r"""
        This is the same with :obj:`Event.listen` but it doesn't require finding events in
        the global scope as it registers the callable onto itself.

        Decorated function must be a staticmethod.
        """
        # this attribute is later checked on class initiation
        func.__subscribes_to__ = self
        return func

    def emit(self, *args, **kwargs):
        r"""
        Event emitter that consumes all args and kwargs it is called against.
        Bound callbacks should be partialized if they need extra data.
        """
        if len(self.callbacks) != 0:
            for cb in self.callbacks:
                cb(*args, **kwargs)

    @staticmethod
    def register(event: "Event"):
        r"""
        Connects a user event into the global registery (injection to the globals for events module).
        Do not give your events conflicting names.
        """
        globals().update({event.__name__: event})

    @staticmethod
    def listen(name: str):
        r"""
        A decorator that registers the callable as a callback under the event with a maching name.
        The given name is searched inside the module level events which exists in the global scope of
        the `events` module.

        If you're making your own events use the instance method :obj:`Event.on_emit` directly or connect
        into the internal runtime event registeries with :obj:`Event.register`:
        Decorated function can be of any type.
        """
        def wrapper(func: Consumer):
            target_event = globals().get(name.upper(), None)
            if target_event is None:
                raise AttributeError(f"cannot find event with name {name}")
            else:
                func.__subscribes_to__ = target_event
            return func
        return wrapper

# Window events
ON_TERMINATE = Event()
ON_START = Event()
ON_RESIZE = Event()
ON_KEY_PRESS = Event()
ON_MOUSE_CLICK = Event()


# Sigint and sigterm signals will start a system termination call
signal.signal(signal.SIGINT, ON_TERMINATE.emit)
signal.signal(signal.SIGTERM, ON_TERMINATE.emit)

# more available unix signals for termination and terminal resize
if os.name == "posix":
    signal.signal(signal.SIGKILL, self.ON_TERMINATE.emit)
    signal.signal(signal.SIGWINCH, self.ON_RESIZE.emit)


class EventListener:
    def __new__(cls, *args, **kwargs):
        r"""
        Filters callables that are marked a subscriber of events to be registered as the event callback.
        """
        obj = super().__new__(cls)
        for item_name in dir(obj):
            item = getattr(obj, item_name, None)
            if callable(item):
                is_subscriber = getattr(item, '__subscribes_to__', False)
                if is_subscriber is not False:
                    # the event itself is attached to __subscribes_to__ so we just need to append onto its callbacks
                    # this is necessary so that methods don't come unbounded
                    item.__subscribes_to__.callbacks.append(item)
        return obj
