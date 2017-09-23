"""This file contains several functions for memory usage.

Taken from the numpy tricks : http://ipython-books.github.io/featured-01/
"""
import numpy as np


__all__ = ('id', 'arrays_share_data', 'code_timer')


def id(x):
    """Get the memory block address of an array."""
    return x.__array_interface__['data'][0]


def get_data_base(arr):
    """For a given array, finds the base array that "owns" the actual data."""
    base = arr
    while isinstance(base.base, np.ndarray):
        base = base.base
    return base


def arrays_share_data(x, y):
    """Return if two arrays share an offset."""
    return get_data_base(x) is get_data_base(y)


def code_timer(previous=0., verbose=True, prefix='', unit='s'):
    """Time code execution.

    Parameters
    ----------
    previous : float | 0.
        Previous code timing.
    verbose : bool | True
        Print time difference.
    prefix : string | ''
        Prefix to add before printing.
    unit : string | 's'
        Use either 's', 'ms' 'us'.
    """
    from time import time
    assert unit in ['s', 'ms', 'us']

    fact = 1. if unit == 's' else 10e3 if unit == 'ms' else 10e6
    current = time()
    st = abs(current - previous)
    if verbose:
        print(prefix, st * fact, '(' + unit + ')')
    return current
