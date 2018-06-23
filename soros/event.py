from collections import defaultdict
from functools import wraps


class Hub:
    """
    A hub for publishing and subscribing to.
    """
    def __init__(self):
        self._subscribers = defaultdict(set)

    def add_subscriber(self, subscriber, *keys):
        for key in keys:
            self._subscribers[key].add(subscriber)

    def publish(self, key, *args, **kwargs):
        for subscriber in self._subscribers[key]:
            subscriber(*args, **kwargs)

    def remove_subscriber(self, subscriber, *keys):
        for key in keys:
            try:
                self._subscribers[key].remove(subscriber)
            except KeyError:
                pass


hub = Hub()


def subscribe(*keys):
    def wrapper(func):
        hub.add_subscriber(func, *keys)

        @wraps(func)
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)
        return decorator
    return wrapper



