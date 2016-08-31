import numpy as np
from warnings import warn


__all__ = ['normalize']


def normalize(x, tomin=0.0, tomax=1.0):
    """Normalize the array x between tomin and tomax

    Args:
        x: ndarray
            The array to normalize

    Kargs:
        tomin: int/float (def: 0.0)
            Minimum of returned array

        tomax: int/float (def: 1.0)
            Maximum of returned array

    Return:
        xn: ndarray
            The normalized array
    """
    if x.size:
        xm, xM = x.min(), np.abs(x).max()
        if xm != xM:
            return tomax - (((tomax - tomin) * (xM - x)) / (xM-xm))
        else:
            warn('Normalization has been ignored because minimum '
                 'and maximum are both equal to '+str(xm))
            return x
    else:
        return x