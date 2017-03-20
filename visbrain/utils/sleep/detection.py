# -*- coding: utf-8 -*-

"""Group functions for automatic detection of sleep parameters.

Perform:
- REM detection
- Spindles detection
- Peak detection
"""
import numpy as np
from scipy.signal import hilbert
from ..filtering import filt, morlet

__all__ = ['peakdetect', 'remdetect', 'spindlesdetect']


###########################################################################
# SPINDLES DETECTION
###########################################################################

def spindlesdetect(elec, sf, threshold, hypno, nrem_only, min_freq=12.,
                   max_freq=14., min_dur_ms=500, max_dur_ms=1500,
                   method='wavelet'):
    """Perform a sleep spindles detection.

    Args:
        elec: np.ndarray
            eeg signal (preferably central electrodes)

        sf: float
            Downsampling frequency

        threshold: float
            Number of standard deviation to use as threshold
            Threshold is defined as: mean + X * std(derivative)

        hypno: np.ndarray
            Hypnogram vector, same length as elec
            Vector with only 0 if no hypnogram is loaded

        rem_only: boolean
            Perfom detection only on NREM sleep period

    Kargs:
        min_freq: float, optional (def 12)
            Lower bandpass frequency

        max_freq: float, optional (def 14)
            Higher bandpass frequency

        method: string
            Method to extract complex decomposition. Use either 'hilbert' or
            'wavelet'.

    Return:
        idx_spindles: np.ndarray
            Array of supra-threshold indices

        number: int
            Number of detected spindles

        density: float
            Number of spindles per minute

    """
    # Find if hypnogram is loaded :
    hypLoaded = True if np.unique(hypno).size > 1 and nrem_only else False

    if hypLoaded:
        data = elec.copy()
        data[(np.where(np.logical_or(hypno < 1, hypno == 4)))] = 0.
        length = np.count_nonzero(data)
        idx_zero = np.where(data == 0)[0]
    else:
        data = elec
        length = max(data.shape)

    # Get complex decomposition of filtered data :
    if method == 'hilbert':
        # Bandpass filter
        data_filt = filt(sf, [min_freq, max_freq], data, order=4)
        # Hilbert transform on odd-length signals is twice longer. To avoid
        # this extra time, simply set to zero padding.
        # See https://github.com/scipy/scipy/issues/6324
        if data.size % 2:
            analytic = hilbert(data_filt)
        else:
            analytic = hilbert(data_filt[:-1], len(data_filt))
    elif method == 'wavelet':
        analytic = morlet(data, sf, np.mean([min_freq, max_freq]))

    # Get amplitude and phase :
    amplitude = np.abs(analytic)
    phase = np.unwrap(np.angle(analytic))
    # Phase derivative (instantaneaous frequencies) :
    inst_freq = np.diff(phase) / (2.0 * np.pi) * sf
    inst_freq = np.append(inst_freq, 0.)  # What for?

    if hypLoaded:
        amplitude[idx_zero] = np.nan

    thresh = np.nanmean(amplitude) + threshold * np.nanstd(amplitude)

    # Amplitude criteria
    with np.errstate(divide='ignore', invalid='ignore'):
        idx_sup_thr = np.where(amplitude > thresh)[0]

    if idx_sup_thr.size > 0:

        # Get where spindles start / end and duration :
        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr,
                                                                 sf)
        # Get where min_dur < spindles duration < max_dur :
        good_dur = np.where(np.logical_and(duration_ms > min_dur_ms,
                                           duration_ms < max_dur_ms))[0]

        good_idx = _events_removal(idx_start, idx_stop, good_dur)

        idx_sup_thr = idx_sup_thr[good_idx]

        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)

        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)


def _events_duration(index, sf):
    """Compute spindles/REM duration in ms.

    Args:
        index: np.ndarray
            Index of events locations.

        sf: float
            The sampling frequency.

    Returns:
        number: int
            Number of events

        duration_ms: np.ndarray
            Duration of each event

        idx_start: np.ndarray
            Array of integers where each event begin.

        idx_end: np.ndarray
            Array of integers where each event finish.
    """
    # Find boolean values where each spindle start :
    bool_break = (index[1:] - index[:-1]) != 1
    # Get spindles number :
    number = bool_break.sum()
    # Build starting / ending spindles index :
    idx_start = np.hstack([np.array([0]), np.where(bool_break)[0]+1])
    idx_stop = np.hstack((idx_start[1::], len(index)))
    # Compute duration :
    duration_ms = np.diff(idx_start) * (1000. / sf)

    return number, duration_ms, idx_start, idx_stop


def _events_removal(idx_start, idx_stop, good_dur):
    """Remove events that do not have the good duration.

    Args:
        idx_start: np.ndarray
            Starting indices of event.

        idx_stop: np.ndarray
            Ending indices of event.

        good_dur: np.ndarray
            Indices of event having a proper duration.

    Return:
        good_idx: np.ndarray
            Row vector containing the extending version of indices.
    """
    # Get where good duration start / end :
    start = idx_start[good_dur]
    stop = idx_stop[good_dur]

    # Extend each spindle duration (start -> stop) :
    extend = np.array([np.arange(i, j) for i, j in zip(start, stop)])

    # Get it as a flatten array :
    if extend.size:
        return np.hstack(extend.flat)
    else:
        return np.array([], dtype=int)

###########################################################################
# REM DETECTION
###########################################################################


def remdetect(eog, sf, hypno, rem_only, threshold, min_dur_ms=100,
              min_distance_ms=100, moving_ms=100, deriv_ms=40):
    """Perform a rapid eye movement (REM) detection.

    Function to perform a semi-automatic detection of rapid eye movements
    (REM) during REM sleep.

    Args:
        eog: np.ndarray
            EOG signal (preferably after artefact rejection using ICA)

        sf: int
            Downsampling frequency

       hypno: np.ndarray
            Hypnogram vector, same length as data
            Vector with only 0 if no hypnogram is loaded

        rem_only: boolean
            Perfom detection only on REM sleep period

        threshold: float
            Number of standard deviation of the derivative signal
            Threshold is defined as: mean + X * std(derivative)

        min_dur_ms: int, optional (def 30)
            Minimum duration (ms) of rapid eye movement

       min_distance_ms: int, optional (def 100)
            Minimum distance (ms) between two saccades to consider them as
            unique events

        moving_ms: int, optional (def 100)
            Time (ms) window of the moving average

        deriv_ms: int, optional (def 40)
            Time (ms) window of derivative computation
            Default is 40 ms step  since most of naturally occurring human
            saccades have magnitudes of 15 degrees or less and last thus
            no more than 30 - 40 ms (the maximum velocity of a saccade is
            above 500 degrees/sec, see Bahill et al., 1975)

    Return:
        idx_sup_thr: np.ndarray
            Array of supra-threshold indices

        number: int
            Number of detected REMs

        density: float
            Number of REMs per minute

    """
    eog = np.array(eog)

    if rem_only and 4 in hypno:
        eog[(np.where(hypno < 4))] = 0
        length = np.count_nonzero(eog)
        idx_zero = np.where(eog == 0)
    else:
        length = max(eog.shape)

    # Smooth signal with moving average
    sm_sig = _movingaverage(eog, moving_ms, sf)

    # Compute first derivative
    deriv = _derivative(sm_sig, deriv_ms, sf)

    # Smooth derivative
    deriv = _movingaverage(deriv, moving_ms, sf)

    # Define threshold
    if rem_only and 4 in hypno:
        deriv[idx_zero] = np.nan

    thresh = np.nanmean(deriv) + threshold * np.nanstd(deriv)

    # Find supra-threshold values
    with np.errstate(divide='ignore', invalid='ignore'):
        idx_sup_thr = np.where(deriv > thresh)[0]

    if idx_sup_thr.size:

        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr,
                                                                 sf)

        # Get where min_dur < REM duration:
        good_dur = np.where(duration_ms > min_dur_ms)[0]
        good_dur = np.append(good_dur, len(good_dur))
        good_idx = _events_removal(idx_start, idx_stop, good_dur)

        idx_sup_thr = idx_sup_thr[good_idx]

        # Remove first event
        idx_sup_thr = np.delete(idx_sup_thr, 0)

        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)

        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)

def _movingaverage(x, window, sf):
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


def _derivative(x, window, sf):
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

###########################################################################
# PEAKS DETECTION
###########################################################################


def peakdetect(y_axis, x_axis=None, lookahead=200, delta=0):
    """Perform a peak detection.

    Converted from/based on a MATLAB script at:
    http://billauer.co.il/peakdet.html

    function for detecting local maxima and minima in a signal.
    Discovers peaks by searching for values which are surrounded by lower
    or larger values for maxima and minima respectively

    keyword arguments:
    y_axis -- A list containing the signal over which to find peaks

    x_axis -- A x-axis whose values correspond to the y_axis list and is used
        in the return to specify the position of the peaks. If omitted an
        index of the y_axis is used.
        (default: None)

    lookahead -- distance to look ahead from a peak candidate to determine if
        it is the actual peak
        (default: 200)
        '(samples / period) / f' where '4 >= f >= 1.25' might be a good value

    delta -- this specifies a minimum difference between a peak and
        the following points, before a peak may be considered a peak. Useful
        to hinder the function from picking up false peaks towards to end of
        the signal. To work well delta should be set to delta >= RMSnoise * 5.
        (default: 0)
            When omitted delta function causes a 20% decrease in speed.
            When used Correctly it can double the speed of the function


    return: two lists [max_peaks, min_peaks] containing the positive and
        negative peaks respectively. Each cell of the lists contains a tuple
        of: (position, peak_value)
        to get the average peak value do: np.mean(max_peaks, 0)[1] on the
        results to unpack one of the lists into x, y coordinates do:
        x, y = zip(*max_peaks)
    """
    max_peaks = []
    min_peaks = []
    dump = []   # Used to pop the first hit which almost always is false

    # check input data
    x_axis, y_axis = _datacheck(x_axis, y_axis)
    # store data length for later use
    length = len(y_axis)

    # perform some checks
    if lookahead < 1:
        raise ValueError("Lookahead must be '1' or above in value")
    if not (np.isscalar(delta) and delta >= 0):
        raise ValueError("delta must be a positive number")

    # maxima and minima candidates are temporarily stored in
    # mx and mn respectively
    mn, mx = np.Inf, -np.Inf

    # Only detect peak if there is 'lookahead' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-lookahead],
                                       y_axis[:-lookahead])):
        if y > mx:
            mx = y
            mxpos = x
        if y < mn:
            mn = y
            mnpos = x

        # ==== Look for max ====
        if y < mx - delta and mx != np.Inf:
            # Maxima peak candidate found
            # look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index + lookahead].max() < mx:
                max_peaks.append([mxpos, mx])
                dump.append(True)
                # set algorithm to only find minima now
                mx = np.Inf
                mn = np.Inf
                if index + lookahead >= length:
                    # end is within lookahead no more peaks can be found
                    break
                continue
            # else:  #slows shit down this does
            #    mx = ahead
            #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]

        # ==== Look for max ====
        if y > mn + delta and mn != -np.Inf:
            # Minima peak candidate found
            # look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index + lookahead].min() > mn:
                min_peaks.append([mnpos, mn])
                dump.append(False)
                # set algorithm to only find maxima now
                mn = -np.Inf
                mx = -np.Inf
                if index + lookahead >= length:
                    # end is within lookahead no more peaks can be found
                    break
            # else:  #slows shit down this does
            #    mn = ahead
            #    mnpos = x_axis[np.where(y_axis[index:index+lookahead]==mn)]

    # Remove the false hit on the first value of the y_axis
    try:
        if dump[0]:
            max_peaks.pop(0)
        else:
            min_peaks.pop(0)
        del dump
    except IndexError:
        # no peaks were found, should the function return empty lists?
        pass

    return [max_peaks, min_peaks]


def _datacheck(x_axis, y_axis):
    """Check inputs for peak detection."""
    if x_axis is None:
        x_axis = range(len(y_axis))

    if len(y_axis) != len(x_axis):
        raise ValueError("Input vectors y_axis and x_axis must have same "
                         "length")

    # Needs to be a numpy array
    y_axis = np.array(y_axis)
    x_axis = np.array(x_axis)
    return x_axis, y_axis
