"""Set of functions for picture managment."""
import numpy as np


__all__ = ['autocrop']


def autocrop(im, margin=10):
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
    # Size checking :
    if im.ndim == 3:
        imas = im[..., 0:3].mean(axis=2)
    else:
        imas = im
    # Compute diff :
    imdiff_x = np.diff(imas, axis=1)
    imdiff_y = np.diff(imas, axis=0)
    # Find where cropping start / finish :
    idx_x = np.where(imdiff_x != 0)[1]
    if idx_x.size:
        xm = max(0, idx_x.min()-margin)
        xM = min(imas.shape[1], idx_x.max()+margin)
        sl_x = slice(xm, xM)
    else:
        sl_x = slice(None)
    idx_y = np.where(imdiff_y)[0]
    if idx_y.size:
        ym = max(0, idx_y.min()-margin)
        yM = min(imas.shape[0], idx_y.max()+margin)
        sl_y = slice(ym, yM)
    else:
        sl_y = slice(None)

    return im[sl_y, sl_x, ...]