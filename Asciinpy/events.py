import signal

from threading import Thread
from typing import Any, Callable, Protocol, List
from functools import partial

from Asciinpy.globals import Platform

from .utils import isinstancemethod

__all__ = ["Event", "EventListener", "ON_TERMINATE", "ON_START", "ON_RESIZE", "ON_KEY_PRESS", "ON_MOUSE_CLICK"]

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
    __slots__ = ("subscribers", "name", "threadable")

    def __init__(self, name: str, threadable: bool=True):
        """
        An Event Aggregator that allows observers to listen to certain events and observers in
        this specific case are callables.
        """
        self.name = name
        self.threadable = threadable
        self.subscribers: List[ListeningFunc] = []

    def emit(self, *args, **kwargs):
        if len(self.subscribers) != 0:
            for cb in self.subscribers:
                if cb.__threaded__ and self.threadable:
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
        super().emit(args[0], **kwargs)
        exit(args[0])


ON_TERMINATE = ON_TERMINATE_EVENT("ON_TERMINATE")
ON_START = Event("ON_START", threadable=False)
ON_RESIZE = Event("ON_RESIZE")
ON_KEY_PRESS = Event("ON_KEY_PRESS")
ON_KEY_RELEASE = Event("ON_KEY_RELEASE")
ON_MOUSE_CLICK = Event("ON_MOUSE_CLICK")


# Sigint and sigterm signals will start a system termination call
signal.signal(signal.SIGINT, partial(ON_TERMINATE.emit, signal.SIGINT.value))
signal.signal(signal.SIGTERM, partial(ON_TERMINATE.emit, signal.SIGTERM.value))

if not Platform.is_window:
   signal.signal(signal.SIGWINCH, partial(ON_TERMINATE.emit, signal.SIGWINCH.value)) # type: ignore
