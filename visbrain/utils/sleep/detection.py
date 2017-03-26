# -*- coding: utf-8 -*-

"""Group functions for automatic detection of sleep parameters.

Perform:
- REM detection
- Spindles detection
- Slow wave detection
- KCs detection
- Peak detection
"""
import numpy as np
from scipy.signal import hilbert, daub

from ..filtering import filt, morlet, morlet_power
from ..sigproc import movingaverage, derivative, tkeo, soft_thresh
from .event import (_events_duration, _events_removal, _events_distance_fill,
                    _events_mean_freq, _event_amplitude)

__all__ = ['peakdetect', 'remdetect', 'spindlesdetect', 'slowwavedetect',
           'kcdetect']

###########################################################################
# K-COMPLEX DETECTION
###########################################################################


def kcdetect(elec, sf, threshold, hypno, nrem_only):
    """Perform a K-complex detection.

    Args:
        elec: np.ndarray
            eeg signal (preferably central electrodes)

        sf: float
            Downsampling frequency

        threshold: float
            Threshold to use for KC detection

        hypno: np.ndarray
            Hypnogram vector, same length as elec
            Vector with only 0 if no hypnogram is loaded

        nrem_only: boolean
            Perfom detection only on NREM sleep period

    Return:
        idx_kc: np.ndarray
            Array of supra-threshold indices

        number: int
            Number of detected K-complexes

        density: float
            Number of K-complexes per minutes of data

        duration_ms: float
            Duration (ms) of each K-complex detected
    """
    # Find if hypnogram is loaded :
    hypLoaded = True if np.unique(hypno).size > 1 and nrem_only else False

    # if hypLoaded:
    #     data = elec.copy()
    #     data[(np.where(np.logical_or(hypno < 1, hypno == 4)))] = 0.
    #     length = np.count_nonzero(data)
    #     idx_zero = np.where(data == 0)[0]
    # else:
    #     data = elec
    #     length = max(data.shape)

    data = elec
    length = max(data.shape)

    print(np.abs(data.max()-data.min()))

    # Main parameters (raw values per algorithm construction)
    delta_thr = 0.75
    moving_s = 30
    spindles_thresh = 1
    range_spin_sec = 60
    threshold = 3
    kc_min_amp = 75
    kc_max_amp = 500
    fMin = 0.5
    fMax = 4
    tMin = 300
    tMax = 3000
    min_distance_ms = 500
    daub_coeff = 6
    daub_mult = 10

    # PRE DETECTION
    # Compute delta band power
    freqs = np.array([0.5, 4., 8., 12., 16.])
    delta_npow, _, _, _ = morlet_power(data, freqs, sf, norm=True)
    delta_nfpow = movingaverage(delta_npow, moving_s * 1000, sf)
    idx_delta = np.where(delta_nfpow > delta_thr)[0]

    # Compute spindles detection
    spindles, _, _, _ = spindlesdetect(data, sf, spindles_thresh, hypno,
                                       nrem_only=False)

    # MAIN DETECTION
    sig_filt = filt(sf, np.array([fMin, fMax]), data)
    wavelet = daub_mult * daub(daub_coeff)
    sig_transformed = np.convolve(sig_filt, wavelet, mode='same')
    sig_transformed = tkeo(sig_transformed)

    thresh = np.mean(sig_transformed) + threshold * np.std(sig_transformed)

    # Enveloppe amplitude criteria
    val_sup_thr = soft_thresh(sig_transformed, thresh)
    idx_sup_thr = np.where(val_sup_thr != 0)[0]

    if idx_sup_thr.size > 0:

        # PROBABILITY
        # Find epoch with slow wave
        idx_kc_delta = np.intersect1d(idx_sup_thr, idx_delta)
        idx_no_delta = np.setdiff1d(idx_sup_thr, idx_kc_delta)

        # Check if spindles are present in range_spin_sec
        number, _, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)
        spin_bool = np.array([], dtype=np.bool)
        for i, j in enumerate(idx_start):
            step = 0.5 * range_spin_sec * sf
            is_spin = np.in1d(np.arange(j - step, j + step, 1),
                              spindles, assume_unique=True)
            spin_bool = np.append(spin_bool, any(is_spin))

        good_kc = np.where(spin_bool)[0]
        good_idx = _events_removal(idx_start, idx_stop, good_kc)

        # Compute probability
        proba = np.zeros(shape=data.shape)
        proba[idx_sup_thr] += 0.1
        proba[idx_no_delta] *= 3
        proba[good_idx] *= 2

        if hypLoaded:
            proba[np.where(hypno == 0)[0]] *= .2
            proba[np.where(hypno == 2)[0]] *= 3.
            proba[np.where(hypno == 3)[0]] *= .5
            proba[np.where(hypno == 4)[0]] *= .2
            proba[np.where(hypno == -1)[0]] *= .5

        idx_sup_thr = np.intersect1d(idx_sup_thr, np.where(proba >= 0.3)[0])

        # K-COMPLEX MORPHOLOGY
        # 1 - Get where KC start / end and duration :
        _, _, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)

        # 2 - Get where min_dur <  KC duration < max_dur :
        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)
        good_dur = np.where(np.logical_and(duration_ms > tMin,
                                           duration_ms < tMax))[0]

        idx_dur = _events_removal(idx_start, idx_stop, good_dur)
        idx_sup_thr = idx_sup_thr[idx_dur]

        # 3 - Check amplitude > kc_min_amp
        _, _, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)
        kc_amp, distance_ms = _event_amplitude(data, idx_start, idx_stop, sf)
        print("Amplitude:\n", kc_amp)
        # print("Distance (ms)\n", distance_ms)
        good_amp = np.where(np.logical_and(kc_amp > kc_min_amp,
                                           kc_amp < kc_max_amp))[0]
        idx_amp = _events_removal(idx_start, idx_stop, good_amp)
        # idx_sup_thr = idx_sup_thr[idx_amp]

        # Export info
        number, duration_ms, idx_start, idx_stop = _events_duration(
            idx_sup_thr, sf)
        # mfreq = _events_mean_freq(data, idx_start, idx_stop, sf)
        density = number / (length / sf / 60.)
        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)


###########################################################################
# SPINDLES DETECTION
###########################################################################

def spindlesdetect(elec, sf, threshold, hypno, nrem_only, min_freq=12.,
                   max_freq=14., min_dur_ms=500, max_dur_ms=1500,
                   method='wavelet', min_distance_ms=1000):
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

        nrem_only: boolean
            Perfom detection only on NREM sleep period

    Kargs:
        min_freq: float, optional (def 12)
            Lower bandpass frequency

        max_freq: float, optional (def 14)
            Higher bandpass frequency

        method: string
            Method to extract complex decomposition. Use either 'hilbert' or
            'wavelet'.

        min_distance_ms: int, optional (def 1000)
            Minimum distance (in ms) between two spindles to consider them as
            two distinct spindles

    Return:
        idx_spindles: np.ndarray
            Array of supra-threshold indices

        number: int
            Number of detected spindles

        density: float
            Number of spindles per minutes of data

        duration_ms: float
            Duration (ms) of each spindles detected

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

        # Fill gap between spindles separated by less than min_distance_ms
        idx_sup_thr = _events_distance_fill(idx_sup_thr, min_distance_ms, sf)

        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)

        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)


###########################################################################
# REM DETECTION
###########################################################################


def remdetect(eog, sf, hypno, rem_only, threshold, min_dur_ms=50,
              max_dur_ms=500, min_distance_ms=200, moving_ms=100, deriv_ms=40):
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

        min_distance_ms: int, optional (def 50)
            Minimum distance (ms) between two saccades to consider them as two
            distinct events

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

        duration_ms: float
            Duration (ms) of each REM detected

    """
    eog = np.array(eog)

    if rem_only and 4 in hypno:
        eog[(np.where(hypno < 4))] = 0
        length = np.count_nonzero(eog)
        idx_zero = np.where(eog == 0)
    else:
        length = max(eog.shape)

    # Smooth signal with moving average
    sm_sig = movingaverage(eog, moving_ms, sf)

    # Compute first derivative
    deriv = derivative(sm_sig, deriv_ms, sf)

    # Smooth derivative
    deriv = movingaverage(deriv, moving_ms, sf)

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

        # Get where min_dur < REM duration
        good_dur = np.where(np.logical_and(duration_ms > min_dur_ms,
                                           duration_ms < max_dur_ms))[0]
        good_dur = np.append(good_dur, len(good_dur))
        good_idx = _events_removal(idx_start, idx_stop, good_dur)
        idx_sup_thr = idx_sup_thr[good_idx]

        # Find REMs separated by less than min_distance_ms
        idx_sup_thr = _events_distance_fill(idx_sup_thr, min_distance_ms, sf)

        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)

        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)

###########################################################################
# SLOW WAVE DETECTION
###########################################################################


def slowwavedetect(elec, sf, threshold, amplitude, fMin=0.5, fMax=4,
                   moving_s=30):
    """Perform a Slow Wave detection.

    Args:
        elec: np.ndarray
            eeg signal (preferably frontal electrodes)

        sf: float
            Downsampling frequency

        threshold: float
            First threshold: number of standard deviation of delta power
            Formula: mean + X * std(derivative)

        amplitude: float
            Secondary threshold: minimum amplitude (mV) of the raw signal.
            Slow waves are generally defined by amplitude > 75 mV.

    Kargs:
        fMin: float, optional (def 0.5)
            High-pass frequency

        fMax: float, optional (def 4)
            Lowpass frequency

        moving_s: int, optional (def 30)
            Time (sec) window of the moving average

    Return:
        idx_sup_thr: np.ndarray
            Array of supra-threshold indices

        number: int
            Number of detected slow-wave

        duration_ms: float
            Duration (ms) of each slow wave period detected

    """
    # Get complex decomposition of filtered data in the main EEG freq band:
    freqs = np.array([fMin, fMax, 8., 12., 16.])
    delta_npow, _, _, _ = morlet_power(elec, freqs, sf, norm=True)

    # Smooth
    delta_nfpow = movingaverage(delta_npow, moving_s * 1000, sf)

    # Normalized power criteria
    thresh = np.nanmean(delta_nfpow) + threshold * np.nanstd(delta_nfpow)
    idx_sup_thr = np.where(delta_nfpow > thresh)[0]

    # Raw signal amplitude criteria
    raw_thresh = amplitude / 2
    idx_sup_raw = np.where(abs(elec) > raw_thresh)[0]
    idx_sup_thr = np.intersect1d(idx_sup_thr, idx_sup_raw)

    number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)

    return idx_sup_thr, number, duration_ms

    # WELCH METHOD
    # WARNING: only return one value per epoch (and not per ms)
    # delta_spec_norm = welch_power(elec, fMin, fMax, sf,
    #                             window_s=30, norm=True)

    # WAVELET AMPLITUDE
    # analytic = morlet(elec, sf, np.mean([fMin, fMax]))
    # amplitude = np.abs(analytic)
    # # Clip extreme values
    # amplitude = np.clip(amplitude, 0, 10 * np.std(amplitude))
    # thresh = np.mean(amplitude) + threshold * np.std(amplitude)
    # idx_sup_thr = np.where(amplitude > thresh)[0]
    # number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
    # return idx_sup_thr, number, duration_ms

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
