"""Perform a semi-automatic Rapid Eye Movements detection.

"""
import numpy as np

__all__ = ['remdetect']


def _datacheck_remdetect(x_axis, y_axis):
    if x_axis is None:
        x_axis = range(len(y_axis))

    if len(y_axis) != len(x_axis):
        raise ValueError("Input vectors y_axis and x_axis must have same "
                         "length")

    # Needs to be a numpy array
    y_axis = np.array(y_axis)
    x_axis = np.array(x_axis)
    return x_axis, y_axis

def movingaverage (x, window, sf):
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
    weights = np.repeat(1.0, window)/window
    sma = np.convolve(x, weights, 'same')
    return sma


def derivative (x, window, sf):
    """Compute first derivative of signal.

    Args:
        x: np.ndarray
            Signal

        window: int
            Time (ms) window to compute first derivative

        sf: int
            Downsampling frequency

    """
    length = x.size
    step = int(window / ( 1000 / sf ))
    tail = np.zeros(shape=(int(step/2),))

    deriv = np.hstack((tail, x[step:length] - x[0:length-step], tail))

    deriv = np.abs(deriv)

    return deriv

def remdetect(eog, sf, x_axis=None, threshold=3, moving_ms=100, deriv_ms=40):
    """Perform a rapid eye movement (REM) detection

    Function to perform a semi-automatic detection of rapid eye movements
    (REM) during REM sleep.

    Args:
        eog: np.ndarray
            EOG signal (preferably after artefact rejection using ICA)

        sf: int
            Downsampling frequency

        x_axis: np.ndarray, optional
            A x-axis whose values correspond to the y_axis list and is used in
            the return to specify the position of REMs

        threshold: float, optional (def 3)
            Number of standard deviation of the derivative signal
            Threshold is defined as: mean + X * std(derivative)

        moving_ms: int, optional (def 100)
            Time (ms) window of the moving average

        deriv_ms: int, optional (def 40)
            Time (ms) window of derivative computation
            Default is 40 ms step  since most of naturally occurring human
            saccades have magnitudes of 15 degrees or less and last thus
            no more than 30 – 40 ms (the maximum velocity of a saccade is
            above 500°/sec, see Bahill et al., 1975)

    Return:
        idx_sup_thr: np.ndarray
            Array of supra-threshold indices

        nb_rem: int
            Number of detected REMs

        density_rem: float
            Number per minutes of REMs

    """

    # check input data
    x_axis, eog = _datacheck_remdetect(x_axis, eog)

    length = max(eog.shape)

    # Smooth signal with moving average
    sm_sig = movingaverage(eog, moving_ms, sf)

    # Compute first derivative
    deriv = derivative(sm_sig, deriv_ms, sf)

    # Smooth derivative
    deriv = movingaverage(deriv, moving_ms, sf)

    # Define threshold
    thresh = np.mean(deriv) + threshold * np.std(deriv)

    # Find supra-threshold values
    idx_sup_thr = np.array(np.where(deriv > thresh)).flatten()

    # Remove first value which is almost always a false positive
    idx_sup_thr = np.delete(idx_sup_thr, 0)

    # Number and density of REM
    rem = np.diff(idx_sup_thr, n=1)
    nb_rem = np.array(np.where(rem > 1)).size
    density_rem = nb_rem / (length / sf / 60)

    return idx_sup_thr, nb_rem, density_rem
