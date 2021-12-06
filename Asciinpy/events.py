import signal

from threading import Thread
from types import FunctionType
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
    __call__: Callable
    __name__: str

# ---


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
                    # the event itself is attached to __subscribes_to__ so we actually only
                    # subscribes to the event on class __new__
                    item.__subscribes_to__.subscribers.append(item)
        return obj


class Event:
    __slots__ = ("subscribers")

    def __init__(self):
        r"""
        An Event Aggregator that allows observers to listen to certain events and observers in
        this specific case are callables.
        """
        self.subscribers: List[ListeningFunc] = []

    def emit(self, *args, **kwargs):
        if len(self.subscribers) != 0:
            for cb in self.subscribers:
                if cb.__threaded__ is True:
                    Thread(target=cb, args=args, kwargs=kwargs).start()
                else:
                    cb(*args, *kwargs)

    @staticmethod
    def listen(event: Union[str, "Event"]=None, threaded: bool=True):
        r"""
        Decorated function can be of any type with the only exception that bound methods must
        subclass under :class:`EventListener`.
        """
        def wrapped(func: ListeningFunc) -> ListeningFunc:
            if isinstance(event, str) or event is None:
                name = event or func.__name__
                target_event = globals().get(name.upper(), None)
                if target_event is None or not isinstance(target_event, Event):
                    raise AttributeError(f"cannot find event with name {event}")
            else:
                target_event = event

            if isinstancemethod(func):
                func.__subscribes_to__ = target_event
                func.__threaded__ = threaded
            else:
                func.__threaded__ = threaded
                target_event.subscribers.append(func)

            return func
        return wrapped

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


# Sigint and sigterm signals will start a system termination call
signal.signal(signal.SIGINT, ON_TERMINATE.emit)
signal.signal(signal.SIGTERM, ON_TERMINATE.emit)

#if PLATFORM != "Window":
#    signal.signal(signal.SIGWINCH, ON_TERMINATE.emit)

del ON_TERMINATE_EVENT, PLATFORM
