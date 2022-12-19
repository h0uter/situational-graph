# OBSERVER PATTERN
from enum import Enum
from typing import Callable


subscriptions: dict[Enum, list[Callable]] = {}


def subscribe(topic: Enum, callback_fn: Callable):
    if topic not in subscriptions:
        subscriptions[topic] = []
    subscriptions[topic].append(callback_fn)


def post_event(topic: Enum, message: object):
    if not (topic in subscriptions):
        return

    for callback_fn in subscriptions[topic]:
        callback_fn(message)
