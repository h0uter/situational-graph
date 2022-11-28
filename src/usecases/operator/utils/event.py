# OBSERVER PATTERN
from typing import Callable


subscribers: dict[str, list[Callable]] = {}


def subscribe(event_type: str, callback_fn: Callable):
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(callback_fn)


def post_event(event_type: str, event_data):
    if not (event_type in subscribers):
        return

    for callback_fn in subscribers[event_type]:
        callback_fn(event_data)
