import signal

from threading import Thread
from typing import Any, Callable, Protocol, Union, List

from .globals import PLATFORM
from .utils import isinstancemethod

__all__ = ["Event", "EventListener"]

#
# Types
#

Consumer = Callable[[Any], None]
BoundConsumer = Callable[[object], None]

class ListeningFunc(Protocol):
    __threaded__: bool
    __subscribes_to__: "Event"

# ---

class Event:
    __slots__ = ("callbacks")

    def __init__(self):
        self.callbacks: List[ListeningFunc] = []

    def emit(self, *args, **kwargs):
        r"""
        Event emitter that passes on all args and kwargs it is called against and calls listeners on subprocesses.
        Bound callbacks should be partialized if they need extra data.
        """
        if len(self.callbacks) != 0:
            for cb in self.callbacks:
                if cb.__threaded__ is True:
                    Thread(target=cb, args=args, kwargs=kwargs).start()
                else:
                    cb(*args, *kwargs)

    @staticmethod
    def listen(event: Union[str, "Event"]=None, threaded: bool=True):
        r"""
        A decorator that registers a callable as a callback under an event.
        Decorated function can be of any type with the only exception that bound methods must subclass under :class:`EventListener`.
        """
        if isinstance(event, str):
            target_event = globals().get(event.upper(), None)
            if target_event is None or not isinstance(target_event, Event):
                raise AttributeError(f"cannot find event with name {event}")
        else:
            target_event = event
        def wrapper(func: Consumer) -> ListeningFunc:
            if isinstancemethod(func):
                func.__subscribes_to__ = target_event
                func.__threaded__ = threaded
            else:
                target_event.callbacks.append(func)
            return func
        return wrapper

# Window events
class ON_TERMINATE_EVENT(Event):
    def emit(self, *args, **kwargs):
        super().emit()
        exit(0)

ON_TERMINATE = ON_TERMINATE_EVENT()
ON_START = Event()
ON_RESIZE = Event()
# IO
ON_KEY_PRESS = Event()
ON_MOUSE_CLICK = Event()

del ON_TERMINATE_EVENT

# Sigint and sigterm signals will start a system termination call
signal.signal(signal.SIGINT, ON_TERMINATE.emit)
signal.signal(signal.SIGTERM, ON_TERMINATE.emit)

# more available unix signals for termination and terminal resize
if PLATFORM != "Windows":
    signal.signal(signal.SIGKILL, ON_TERMINATE.emit)
    signal.signal(signal.SIGWINCH, ON_TERMINATE.emit)

class EventListener:
    def __new__(cls, *args, **kwargs):
        r"""
        Filters callables that are marked a subscriber of an event to be registered as the callback.
        """
        obj = super().__new__(cls)
        for item_name in dir(obj):
            item = getattr(obj, item_name, None)
            if callable(item):
                is_subscriber = getattr(item, '__subscribes_to__', False)
                if is_subscriber is not False:
                    # the event itself is attached to __subscribes_to__ so we just need to append onto its callbacks
                    item.__subscribes_to__.callbacks.append(item)
        return obj
