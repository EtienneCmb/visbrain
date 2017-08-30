"""This script contains some usefull signal processing functions."""

import numpy as np
from warnings import warn


__all__ = ('normalize', 'movingaverage', 'derivative', 'tkeo', 'soft_thresh',
           'zerocrossing', 'power_of_ten')


def normalize(x, tomin=0., tomax=1.):
    """Normalize the array x between tomin and tomax.

    Parameters
    ----------
    x : array_like
        The array to normalize
    tomin : int/float | 0.
        Minimum of returned array

    tomax : int/float | 1.
        Maximum of returned array

    Returns
    -------
    xn : array_like
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
            np.multiply(x, tomax, out=x)
            np.divide(x, xM, out=x)
            return x
    else:
        return x


def movingaverage(x, window, sf):
    """Perform a moving average.

    Equivalent to a lowpass filter where lowpass frequency is defined by:
        LowpassFreq = (1 / window) * 1000
        e.g. if window = 100, LowpassFreq = 10 Hz

    Parameters
    ----------
    x : array_like
        Signal
    window : int
        Time (ms) window to compute moving average
    sf : int
        Downsampling frequency
    """
    window = int(window / (1000. / sf))
    weights = np.repeat(1., window) / window
    sma = np.convolve(x, weights, 'same')
    return sma


def derivative(x, window, sf):
    """Compute first derivative of signal.

    Equivalent to np.gradient function

    Parameters
    ----------
    x : array_like
        Signal
    window : int
        Time (ms) window to compute first derivative
    sf : int
        Downsampling frequency
    """
    length = x.size
    step = int(window / (1000 / sf))
    tail = np.zeros(shape=(int(step / 2),))
    deriv = np.r_[tail, x[step:length] - x[0:length - step], tail]
    deriv = np.abs(deriv)
    # Check size
    if deriv.size < length:
        missing_pts = length - deriv.size
        tail = np.zeros(missing_pts)
        deriv = np.r_[deriv, tail]

    return deriv


def tkeo(x):
    """Calculate the TKEO of a given recording by using 2 samples.

    github.com/lvanderlinden/OnsetDetective/blob/master/OnsetDetective/tkeo.py

    Parameters
    ----------
    x : array_like
        Row vector of data.

    Returns
    -------
    a_tkeo : array_like
        Row vector containing the tkeo per sample.
    """
    # Create two temporary arrays of equal length, shifted 1 sample to the
    # right and left and squared:
    i = x[1:-1] * x[1:-1]
    j = x[2:] * x[:-2]

    # Calculate the difference between the two temporary arrays:
    a_tkeo = i - j
    return a_tkeo


def soft_thresh(x, thresh):
    """Function to solve soft thresholding problem.

    Written by Simon Lucey 2012 to solve the problem :
    arg min_{x} ||x - b||_{2}^{2} + lambda*||x||_{1}

    Parameters
    ----------
    x : array_like
        Data
    thresh : float
        Weighting on the l1 penalty

    Returns
    -------
    x_thresh : array_like
        Solution to the problem (vector with same size as x vector)
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


def zerocrossing(data):
    """Find zero-crossings index of a signal.

    Parameters
    ----------
    x: array_like
        Data

    Returns
    -------
    index : array_like
        Row vector containing zero-crossing index.
    """
    pos = data > 0
    npos = ~pos
    return ((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:])).nonzero()[0] + 1


def power_of_ten(x, e=3):
    """Power of ten format.

    Parameters
    ----------
    x : float
        The floating point to transform.
    e : int | 2
        If x is over 10 ** -e and bellow 10 ** e, this function doesn't
        change the format.

    Returns
    -------
    xtronc: float
        The troncate version of x.
    power: int
        The power of ten to retrieve x.
    """
    sign = np.sign(x)
    x = np.abs(x)
    stx = str(x)
    if 0 < x <= 10 ** -e:  # x is a power of e- :
        if stx.find('e-') + 1:  # Format : 'xe-y'
            sp = stx.split('e-')
            return float(sp[0]), -int(sp[1])
        else:  # Format : 0.000x
            sp = stx.split('.')[1]
            l = 0
            while sp[l] == '0':
                l += 1
            l += 1
            return (sign * x) * (10 ** l), -l
    elif x >= 10 ** e:  # x is a power of e :
        if stx.find('e') + 1:  # Format : 'xey'
            sp = stx.split('e')
            return float(sp[0]), -int(sp[1])
        else:
            k = e
            while x % (10 ** k) != x:
                k += 1
            return (sign * x) / (10 ** (k - 1)), k - 1
    else:
        return sign * x, 0
