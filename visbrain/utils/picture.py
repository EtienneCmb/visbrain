"""Set of functions for picture managment."""
import numpy as np
from scipy.misc import imresize


__all__ = ['piccrop', 'picresize']


def piccrop(im, margin=10):
    """Automatic picture cropping.

    Args:
        im: np.ndarray
            The array of image data. Could be a (N, M) or (N, M, 3/4).

    Kargs:
        margin: int, optional, (def: 10)
            Number of pixels before and after to condider for cropping
            security.

    Returns:
        imas: np.ndarray
            The cropped figure.
    """
    # ================= Size checking =================
    if im.ndim < 2:
        raise ValueError("im must have at least two dimensions.")
    elif im.ndim == 3:
        imas = im[..., 0:3].mean(axis=2)
    else:
        imas = im

    # ================= Derivative =================
    imdiff_x = np.diff(imas, axis=1)
    imdiff_y = np.diff(imas, axis=0)

    # ================= Cropping start / finish =================
    # x-axis :
    idx_x = np.where(imdiff_x != 0)[1]
    if idx_x.size:
        xm = max(0, idx_x.min()-margin)
        xM = min(imas.shape[1], idx_x.max()+margin)
        sl_x = slice(xm, xM)
    else:
        sl_x = slice(None)
    # y-axis :
    idx_y = np.where(imdiff_y)[0]
    if idx_y.size:
        ym = max(0, idx_y.min()-margin)
        yM = min(imas.shape[0], idx_y.max()+margin)
        sl_y = slice(ym, yM)
    else:
        sl_y = slice(None)

    return im[sl_y, sl_x, ...]


def picresize(im, axis=0, extend=False):
    """For a list of pictures, resize them all to the same size.

    Inspect each picture in the list, get all shapes and use the smallest or
    the largest picture as the reference for resizing all other pictures.

    Args:
        im: list
            List of np.ndarray of shapes (N, M) or (N, M, 3/4)

    Kargs:
        axis: int, optional, (def: 0)
            Specify which axis is considered as the reference. Use 0 and all
            figures will have the same height otherwise use 1 for width.

        extend: bool, optional, (def: False)
            Specify if the reference picture have to be the smallest
            (False - downsize all pictures) or the largest
            (True - extend all others).

    Returns:
        imr: list
            List of resized pictures.
    """
    # ================= Checking =================
    if not isinstance(im, list):
        raise ValueError("im must be a list of pictures.")
    if axis not in [0, 1]:
        raise ValueError("axis parameter must either be 0 or 1.")

    # ================= Shapes =================
    sh = np.array([float(k.shape[axis]) for k in im])
    factors = sh.max() / sh if extend else sh.min() / sh

    # ================= Resize =================
    return [imresize(k, i) for k, i in zip(im, factors)]
