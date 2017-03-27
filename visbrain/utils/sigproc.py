"""This script contains some usefull signal processing functions."""

import numpy as np
from warnings import warn


__all__ = ['is_power2', 'normalize', 'movingaverage', 'derivative', 'tkeo', 'soft_thresh']

def is_power2(x):
    """Function to check if a number is a power of 2"""
    return x != 0 and ((x & (x - 1)) == 0)

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
            coef = (tomax - tomin) / (xM - xm)
            np.subtract(x, xM, out=x)
            np.multiply(x, coef, out=x)
            np.add(x, tomax, out=x)
            return x
            # return tomax - (((tomax - tomin) * (xM - x)) / (xM-xm))
        else:
            warn('Normalization has been ignored because minimum '
                 'and maximum are both equal to ' + str(xm))
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


def tkeo(x):
    """Calculates the TKEO of a given recording by using 2 samples.

    github.com/lvanderlinden/OnsetDetective/blob/master/OnsetDetective/tkeo.py

    Args:
       x: 1d np.array
        Data

    Returns:
        aTkeo: 1d np.array
           1D numpy array containing the tkeo per sample
    """
    # Create two temporary arrays of equal length, shifted 1 sample to the
    # right and left and squared:
    i = x[1:-1] * x[1:-1]
    j = x[2:] * x[:-2]

    # Calculate the difference between the two temporary arrays:
    aTkeo = i - j
    return aTkeo


def soft_thresh(x, thresh):
    """Function to solve soft thresholding problem
     arg min_{x} ||x - b||_{2}^{2} + lambda*||x||_{1}

    Args:
        x: 1d np.array
            Data
        thresh: float
            weighting on the l1 penalty
    Returns:
        x_thresh: 1d np.array
            Solution to the problem (vector with same size as x vector)
     Written by Simon Lucey 2012
     """
    th = thresh / 2
    k = np.where(x > th)[0]
    # First find elements that are larger than the threshold
    x_thresh = np.zeros(x.shape)
    x_thresh[k] = x[k] - th
    # Next find elements that are less than abs
    k = np.where(abs(x) <= th)[0]
    x_thresh[k] = 0
    #  Finally find elements that are less than -th
    k = np.where(x < -th)
    x_thresh[k] = x[k] + th
    return x_thresh
