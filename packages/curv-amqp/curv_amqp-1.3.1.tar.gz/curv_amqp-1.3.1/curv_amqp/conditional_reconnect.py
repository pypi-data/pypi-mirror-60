from typing import Callable


def conditional_reconnect(func: Callable):
    def wrapper(self, *args, **kwargs):
        self.conditional_reconnect()
        return func(self, *args, **kwargs)

    return wrapper
