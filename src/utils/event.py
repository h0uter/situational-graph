# OBSERVER PATTERN
from typing import Callable

subscriptions: dict[str, list[Callable]] = {}


def subscribe(topic: str, callback_fn: Callable):
    if topic not in subscriptions:
        subscriptions[topic] = []
    subscriptions[topic].append(callback_fn)


def post_event(topic: str, message):
    if not (topic in subscriptions):
        return

    for callback_fn in subscriptions[topic]:
        callback_fn(message)
