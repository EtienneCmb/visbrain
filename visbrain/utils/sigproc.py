"""This script contains some usefull signal processing functions."""

import numpy as np
from warnings import warn


__all__ = ['normalize', 'movingaverage', 'derivative']


def normalize(x, tomin=0., tomax=1.):
    """Normalize the array x between tomin and tomax.

    Args:
        x: ndarray
            The array to normalize

    Kargs:
        tomin: int/float (def: 0.)
            Minimum of returned array

        tomax: int/float (def: 1.)
            Maximum of returned array

    Return:
        xn: ndarray
            The normalized array
    """
    if x.size:
        x = np.float32(x)
        xm, xM = np.float32(x.min()), np.float32(x.max())
        if xm != xM:
            coef = (tomax - tomin) / (xM-xm)
            np.subtract(x, xM, out=x)
            np.multiply(x, coef, out=x)
            np.add(x, tomax, out=x)
            return x
            # return tomax - (((tomax - tomin) * (xM - x)) / (xM-xm))
        else:
            warn('Normalization has been ignored because minimum '
                 'and maximum are both equal to '+str(xm))
            return tomax * x / xM
    else:
        return x


def movingaverage(x, window, sf):
    """Perform a moving average.

    Args:
        x: np.ndarray
            Signal

        window: int
            Time (ms) window to compute moving average

        sf: int
            Downsampling frequency

    """
    window = int(window / (1000 / sf))
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(x, weights, 'same')
    return sma


def derivative(x, window, sf):
    """Compute first derivative of signal.

       Equivalent to np.gradient function

    Args:
        x: np.ndarray
            Signal

        window: int
            Time (ms) window to compute first derivative

        sf: int
            Downsampling frequency

    """
    length = x.size
    step = int(window / (1000 / sf))
    tail = np.zeros(shape=(int(step / 2),))

    deriv = np.hstack((tail, x[step:length] - x[0:length - step], tail))

    deriv = np.abs(deriv)

    return deriv
