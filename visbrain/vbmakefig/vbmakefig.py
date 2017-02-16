"""Docstring."""

import numpy as np
# import pandas as pd

from scipy.misc import imread, imsave, imshow
import matplotlib.pyplot as plt

from picmath import *


__all__ = ['MakeFigure']


class MakeFigure(object):

    """docstring for vbMakeFigure.
    """

    def __init__(self, path, autoresize=False, verbose=0):
        self._data = []
        self._width = 0
        self._height = 0

    def __len__(self):
        return len(self._data)

    def add_colorbar(self):
        """
        """
        pass

    def render(self, position='row', alignh='left', alignv='center',
               background='w', interspace=None, title=None):
        """
        """
        pass

    def save(self, name, ext='.png', dpi=300):
        """
        """
        pass

    def show(self):
        """
        """
        pass








def _alignh(shapes, method='sup', inter=0, before=0, after=0):
    """Align arrays according to their shape at a specific axis. This function
    can be used to align either horizontaly or verticaly.

    Args:
        shapes: array of shape (N,)
            Array containing the shape of each picture

    Kargs:
        method: string, optional, (def: 'left')
            The method to use for the aligment. Could be 'sup', 'center' or
            'inf'. For horizontal alignement, 'sup' correspond to 'left' and
            'inf' to 'right'; For a vertical alignement, 'sup' correspond
            'top' and 'inf'to 'bottom'.

        inter: int, optional, (def: 0)
            Add some inter-space between each picture for the specified axis.

        before: int, optional, (def: 0)
            Add some space before the first picture.

        after: int, optional, (def: 0)
            Add some space after the last picture.

    Returns:
        index: list
            List of slices for each picture. Each slice specify
            where each picture start and finish.
    """
    # Be sure the shapes is a vector :
    shapes = shapes.ravel()

    index = []
    # Left :
    if method is 'sup':
        q = 0
        for k in shapes:
            index.append(slice(q, q + shapes[k] + inter))
            q += shapes[k]
    # Center :
    elif method is 'center':
        pass
    elif method is 'inf':
        pass




def _fill(data, shapes):
    """
    """
    pass





if __name__ == '__main__':
    shapes = [(3, 5, 4), (4, 8, 4), (5, 7, 4), (14, 3, 4)]
    x = [np.random.randint(0, 100, size=k) for k in shapes]

    hw = picsize(shapes, interh=2, beforeh=5, afterh=10)

    print(np.array(shapes))
    print(hw)

    y = piccomplete(x[0].astype(int), (3, 4, 4), picposh='center', val=1)
    print(y, y.shape)
