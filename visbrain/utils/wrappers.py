"""Wrappers."""
from functools import wraps


__all__ = ['wrap_properties']


def wrap_properties(fn):
    """Run properties if not None."""
    @wraps(fn)
    def wrapper(self, value):
        if value is not None:
            fn(self, value)
    return wrapper
