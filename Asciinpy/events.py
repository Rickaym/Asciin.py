import signal

from threading import Thread
from typing import Any, Callable, Protocol, List

from .utils import isinstancemethod

__all__ = ["Event", "EventListener"]

Consumer = Callable[[Any], None]
BoundConsumer = Callable[[object], None]


class ListeningFunc(Protocol):
    __threaded__: bool
    __subscribes_to__: "Event"
    __call__: Callable[[Any], Any]
    __name__: str


class EventListener:
    def __new__(cls, *args, **kwargs):
        """
        Filters callables that are marked a subscriber of an event to be registered as the callback.
        """
        obj = super().__new__(cls)

        for item_name in dir(obj):
            item = getattr(obj, item_name, None)
            if callable(item):
                is_subscriber = getattr(item, "__subscribes_to__", False)
                if is_subscriber is not False:
                    # the event itself is attached to __subscribes_to__ so we actually only
                    # subscribes to the event on class __new__
                    item.__subscribes_to__.subscribers.append(item)
        return obj


class Event:
    __slots__ = "subscribers"

    def __init__(self):
        """
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
    def listen(event: "Event", threaded: bool = True):
        """
        Decorated function can be of any type with the only exception that bound methods must
        subclass under :class:`EventListener`.
        """

        def wrapped(func: Any) -> ListeningFunc:
            if isinstancemethod(func):
                func.__subscribes_to__ = event
                func.__threaded__ = threaded
            else:
                func.__threaded__ = threaded
                event.subscribers.append(func)

            return func

        return wrapped


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

# if PLATFORM != "Window":
#    signal.signal(signal.SIGWINCH, ON_TERMINATE.emit)

del ON_TERMINATE_EVENT
