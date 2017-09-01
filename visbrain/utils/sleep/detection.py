# -*- coding: utf-8 -*-

"""Group functions for automatic detection of sleep parameters.

Perform:
- REM detection
- Muscle Twitches detection
- Spindles detection
- Slow wave detection
- KCs detection
- Peak detection
"""
import numpy as np
from scipy.signal import hilbert, detrend

from ..filtering import filt, morlet, morlet_power, welch_power
from ..sigproc import movingaverage, derivative, tkeo
from .event import (_events_duration, _events_removal, _events_distance_fill,
                    _events_amplitude)

__all__ = ('kcdetect', 'spindlesdetect', 'remdetect', 'slowwavedetect',
           'mtdetect', 'peakdetect')

###########################################################################
# K-COMPLEX DETECTION
###########################################################################


def kcdetect(elec, sf, proba_thr, amp_thr, hypno, nrem_only, tmin, tmax,
             kc_min_amp, kc_max_amp, fmin=.5, fmax=4., delta_thr=.75,
             moving_s=20, spindles_thresh=1., range_spin_sec=20,
             kc_peak_min_distance=100., min_distance_ms=500.):
    """Perform a K-complex detection.

    Parameters
    ----------
    elec : array_like
        eeg signal (preferably central electrodes)
    sf : float
        Downsampling frequency
    proba_thr : float
        Probability threshold (between 0 and 1)
    amp_thr : float
        Amplitude threshold
    hypno : array_like
        Hypnogram vector, same length as elec
        Vector with only 0 if no hypnogram is loaded
    nrem_only : bool
        Perfom detection only on NREM sleep period
    tmin : float
        Minimum duration (ms) of K-complexes
    tmax : float
        Maximum duration (ms) of K-complexes
    kc_min_amp : float
        Minimum amplitude of K-complexes
    kc_max_amp : float
        Maximum amplitude of K-complexes
    fmin : float | .5
        High-pass cutoff frequency
    fmax : float | 4.
        Low-pass cutoff frequency
    delta_thr : float | .75
        Delta normalized power threshold. Value must be between 0 and 1.
        0 = No thresholding by delta bandpower
    moving_s : int | 20
        Moving average window (sec) for smoothing of delta band power
    spindles_thresh : float | 1.
        Number of standard deviations to compute spindles detection
    range_spin_sec : int | 20
        Duration of lookahead window for spindles detection (sec)
        Check for spindles that are comprised within -range_spin_sec/2 <
        KC < range_spin_sec/2
    kc_peak_min_distance : float | 100.
        Minimum distance (ms) between the minimum and maxima of a KC
    min_distance_ms : float | 500.
        Minimum distance (ms) between two KCs to be considered unique.

    Returns
    -------
    idx_kc : array_like
        Array of supra-threshold indices
    number : int
        Number of detected K-complexes
    density : float
        Number of K-complexes per minutes of data
    duration_ms : float
        Duration (ms) of each K-complex detected
    """
    # Find if hypnogram is loaded :
    hyploaded = True if np.unique(hypno).size > 1 and nrem_only else False

    data = elec
    length = max(data.shape)

    # PRE DETECTION
    # Compute delta band power
    # Morlet's wavelet
    freqs = np.array([0.5, 4., 8., 12., 16.])
    delta_npow, _, _, _ = morlet_power(data, freqs, sf, norm=True)
    delta_nfpow = movingaverage(delta_npow, moving_s * 1000, sf)
    # local_delta_nfpow = movingaverage(delta_npow, sf, sf)
    idx_no_delta = np.where(delta_nfpow < delta_thr)[0]
    idx_loc_delta = np.where(delta_npow > np.mean(delta_npow))[0]

    # MAIN DETECTION
    # Bandpass filtering
    sig_filt = filt(sf, np.array([fmin, fmax]), data)
    # Taiger-Keaser energy operator
    sig_transformed = tkeo(sig_filt)
    # Initial thresholding of the TKEO's amplitude
    thresh = np.mean(sig_transformed) + amp_thr * np.std(sig_transformed)
    idx_sup_thr = np.where(sig_transformed >= thresh)[0]

    if idx_sup_thr.size > 0:
        # Check if spindles are present in range_spin_sec
        idx_spin, _, _, _ = spindlesdetect(data, sf, spindles_thresh, hypno,
                                           nrem_only=False)

        number, _, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)

        spin_bool = np.array([], dtype=np.bool)
        for i, j in enumerate(idx_start):
            step = 0.5 * range_spin_sec * sf
            st_spin = idx_sup_thr[j]
            is_spin = np.in1d(np.arange(st_spin - step, st_spin + step, 1),
                              idx_spin, assume_unique=True)
            spin_bool = np.append(spin_bool, any(is_spin))
        kc_spin = np.where(spin_bool)[0]
        idx_kc_spin = idx_sup_thr[_events_removal(idx_start, idx_stop,
                                                  kc_spin)]

        # Compute probability
        proba = np.zeros(shape=data.shape)
        proba[idx_sup_thr] += 0.1
        proba[idx_no_delta] += 0.1
        proba[idx_loc_delta] += 0.1
        proba[idx_kc_spin] += 0.1

        if hyploaded:
            proba[np.where(hypno == -1)[0]] += -0.1
            proba[np.where(hypno == 0)[0]] += -0.2
            proba[np.where(hypno == 2)[0]] += 0
            proba[np.where(hypno == 2)[0]] += 0.1
            proba[np.where(hypno == 3)[0]] += -0.1
            proba[np.where(hypno == 4)[0]] += -0.2

        # Smooth and normalize probability vector
        proba = proba / 0.5 if hyploaded else proba / 0.4
        proba = movingaverage(proba, sf, sf)

        # Keep only proba >= proba_thr (user defined threshold)
        idx_sup_thr = np.intersect1d(idx_sup_thr, np.where(
            proba >= proba_thr)[0], True)

    if idx_sup_thr.size > 0:
        # K-COMPLEX MORPHOLOGY
        idx_sup_thr = _events_distance_fill(idx_sup_thr, min_distance_ms, sf)
        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)

        kc_amp, distance_ms = _events_amplitude(data, idx_sup_thr,
                                                idx_start, idx_stop, sf)
        good_dur = np.where(np.logical_and(duration_ms > tmin,
                                           duration_ms < tmax))[0]

        good_amp = np.where(np.logical_and(kc_amp > kc_min_amp,
                                           kc_amp < kc_max_amp))[0]
        good_dist = np.where(distance_ms > kc_peak_min_distance)[0]

        good_event = np.intersect1d(good_amp, good_dur, True)
        good_event = np.intersect1d(good_event, good_dist, True)
        good_idx = _events_removal(idx_start, idx_stop, good_event)

        idx_sup_thr = idx_sup_thr[good_idx]
        idx_sup_thr = _events_distance_fill(idx_sup_thr, min_distance_ms, sf)

        # Export info
        number, duration_ms, idx_start, idx_stop = _events_duration(
            idx_sup_thr, sf)

        density = number / (length / sf / 60.)
        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)


###########################################################################
# SPINDLES DETECTION
###########################################################################

def spindlesdetect(elec, sf, threshold, hypno, nrem_only, fmin=12., fmax=14.,
                   tmin=500, tmax=2000, method='wavelet', min_distance_ms=500,
                   sigma_thr=0.25):
    """Perform a sleep spindles detection.

    Parameters
    ----------
    elec : array_like
        eeg signal (preferably central electrodes)
    sf : float
        Downsampling frequency
    threshold : float
        Number of standard deviation to use as threshold
        Threshold is defined as: mean + X * std(derivative)
    hypno : array_like
        Hypnogram vector, same length as elec
        Vector with only 0 if no hypnogram is loaded
    nrem_only : bool
        Perfom detection only on NREM sleep period
    fmin : float | 12
        Lower bandpass frequency
    fmax : float | 14
        Higher bandpass frequency
    method: {'wavelet', 'hilbert'}
        Method to extract complex decomposition. Use either 'hilbert' or
        'wavelet'.
    min_distance_ms : int | 500
        Minimum distance (in ms) between two spindles to consider them as
        two distinct spindles
    sigma_thr : float | 0.25
        Sigma band-wise normalized power threshold (between 0 and 1)

    Returns
    -------
    idx_spindles : array_like
        Array of supra-threshold indices
    number : int
        Number of detected spindles
    density : float
        Number of spindles per minutes of data
    duration_ms : float
        Duration (ms) of each spindles detected

    """
    # Find if hypnogram is loaded :
    hyploaded = True if np.unique(hypno).size > 1 and nrem_only else False

    if hyploaded:
        data = elec.copy()
        data[(np.where(np.logical_or(hypno < 1, hypno == 4)))] = 0.
        length = np.count_nonzero(data)
        idx_zero = np.where(data == 0)[0]
    else:
        data = elec
        length = max(data.shape)

    # Pre-detection
    # Compute relative sigma power
    freqs = np.array([0.5, 4., 8., fmin, fmax])
    _, _, _, sigma_npow = morlet_power(data, freqs, sf, norm=True)
    sigma_nfpow = movingaverage(sigma_npow, sf, sf)
    idx_sigma = np.where(sigma_nfpow > sigma_thr)[0]

    # Get complex decomposition of filtered data :
    if method == 'hilbert':
        # Bandpass filter
        data_filt = filt(sf, [fmin, fmax], data, order=4)
        # Hilbert transform on odd-length signals is twice longer. To avoid
        # this extra time, simply set to zero padding.
        # See https://github.com/scipy/scipy/issues/6324
        if data.size % 2:
            analytic = hilbert(data_filt)
        else:
            analytic = hilbert(data_filt[:-1], len(data_filt))
    elif method == 'wavelet':
        analytic = morlet(data, sf, np.mean([fmin, fmax]))

    amplitude = np.abs(analytic)

    if hyploaded:
        amplitude[idx_zero] = np.nan

    # Define threshold
    thresh = np.nanmean(amplitude) + threshold * np.nanstd(amplitude)

    with np.errstate(divide='ignore', invalid='ignore'):
        idx_sup_thr = np.where(amplitude > thresh)[0]

    if idx_sup_thr.size > 0:

        idx_sup_thr = np.intersect1d(idx_sup_thr, idx_sigma, True)
        idx_sup_thr = _events_distance_fill(idx_sup_thr, min_distance_ms, sf)

        # Get where spindles start / end and duration :
        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr,
                                                               sf)

        # Get where min_dur < spindles duration < max_dur :
        good_dur = np.where(np.logical_and(duration_ms > tmin,
                                           duration_ms < tmax))[0]

        good_idx = _events_removal(idx_start, idx_stop, good_dur)

        idx_sup_thr = idx_sup_thr[good_idx]

        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)

        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)


###########################################################################
# REM DETECTION
###########################################################################


def remdetect(elec, sf, hypno, rem_only, threshold, tmin=200, tmax=1500,
              min_distance_ms=200, moving_ms=200, deriv_ms=30,
              amplitude_art=400):
    """Perform a rapid eye movement (REM) detection.

    Function to perform a semi-automatic detection of rapid eye movements
    (REM) during REM sleep.

    Parameters
    ----------
    elec: array_like
        EOG signal (preferably after artefact rejection using ICA)
    sf: int
        Downsampling frequency
    hypno: array_like
        Hypnogram vector, same length as data
        Vector with only 0 if no hypnogram is loaded
    rem_only: bool
        Perfom detection only on REM sleep period
    threshold: float
        Number of standard deviation of the derivative signal
        Threshold is defined as: mean + X * std(derivative)
    tmin : int | 200
        Minimum duration (ms) of rapid eye movement
    tmax : int | 1500
        Maximum duration (ms) of rapid eye movement
    min_distance_ms : int | 200
        Minimum distance (ms) between two saccades to consider them as two
        distinct events.
    moving_ms : int | 200
        Time (ms) window of the moving average.
    deriv_ms : int | 30
        Time (ms) window of derivative computation
    amplitude_art : int | 400
        Remove extreme values from the signal

    Returns
    -------
    idx_sup_thr: array_like
        Array of supra-threshold indices
    number: int
        Number of detected REMs
    density: float
        Number of REMs per minute
    duration_ms: float
        Duration (ms) of each REM detected
    """
    if rem_only and 4 in hypno:
        elec[(np.where(hypno < 4))] = 0
        length = np.count_nonzero(elec)
        idx_zero = np.where(elec == 0)
    else:
        length = max(elec.shape)

    # Smooth signal with moving average
    sm_sig = movingaverage(elec, moving_ms, sf)
    # Compute first derivative
    deriv = derivative(sm_sig, deriv_ms, sf)
    # Smooth derivative
    deriv = movingaverage(deriv, moving_ms, sf)
    # Define threshold
    if rem_only and 4 in hypno:
        id_th = np.setdiff1d(np.arange(elec.size), idx_zero)
    else:
        id_th = np.arange(elec.size)
    # Remove extreme values
    id_th = np.setdiff1d(id_th, np.where(np.abs(sm_sig) > amplitude_art)[0])
    # Find supra-threshold values
    thresh = np.mean(deriv[id_th]) + threshold * np.std(deriv[id_th])
    idx_sup_thr = np.where(deriv > thresh)[0]

    if idx_sup_thr.size:

        # Find REMs separated by less than min_distance_ms
        idx_sup_thr = _events_distance_fill(idx_sup_thr, min_distance_ms, sf)

        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)

        # Get where min_dur < REM duration < tmax
        good_dur = np.where(np.logical_and(duration_ms > tmin,
                                           duration_ms < tmax))[0]
        good_idx = _events_removal(idx_start, idx_stop, good_dur)
        idx_sup_thr = idx_sup_thr[good_idx]

        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)

        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)

###########################################################################
# SLOW WAVE DETECTION
###########################################################################


def slowwavedetect(elec, sf, threshold, min_amp=70., max_amp=400., fmin=.5,
                   fmax=2., welch_win_s=12, moving_s=30, min_duration_ms=500.):
    """Perform a Slow Wave detection.

    Parameters
    ----------
    elec : array_like
        eeg signal (preferably frontal electrodes)
    sf : float
        Downsampling frequency
    threshold : float
        First threshold: bandwise-normalized delta power Value must be between
        0 and 1.
    min_amp : float | 70.
        Secondary threshold: minimum amplitude (uV) of the raw signal.
        Slow waves are generally defined by amplitude > 70 uV.
    max_amp : float | 400.
        Maximum amplitude of slow wave
    fmin  : float | .5
        High-pass frequency
    fmax  : float | 2.
        Lowpass frequency
    welch_win_s  : int | 12
        Time (sec) window for computation of normalized bandpower with
        Welch's method
    moving_s : int | 30
        Time (sec) window of moving average to be applied on delta power
    min_duration_ms : float | 500.
        Minimum duration (ms) of slow waves

    Returns
    -------
    idx_sup_thr : array_like
        Array of supra-threshold indices
    number : int
        Number of detected slow-wave
    duration_ms : float
        Duration (ms) of each slow wave period detected
    """
    length = max(elec.shape)

    # Get complex decomposition of filtered data in the main EEG freq band:
    # Using Morlet's wavelet - a bit longer
    # freqs = np.array([fmin, fmax, 8., 12., 16.])
    # delta_npow, _, _, _ = morlet_power(elec, freqs, sf, norm=True)
    # delta_nfpow = movingaverage(delta_npow, moving_s * 1000, sf)

    # Using Welch's method
    delta_nfpow = welch_power(elec, fmin, fmax, sf, welch_win_s, norm=True)
    delta_nfpow = np.repeat(delta_nfpow, welch_win_s * sf)
    delta_nfpow = movingaverage(delta_nfpow, 3 * welch_win_s * sf, sf)

    # Normalized power criteria
    idx_sup_thr = np.where(delta_nfpow > threshold)[0]

    if idx_sup_thr.size:

        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)

        sw_amp, _ = _events_amplitude(elec, idx_sup_thr, idx_start,
                                      idx_stop, sf)

        good_amp = np.where(np.logical_and(sw_amp > min_amp,
                                           sw_amp < max_amp))[0]

        good_dur = np.where(duration_ms > min_duration_ms)[0]
        good_event = np.intersect1d(good_amp, good_dur, True)
        good_idx = _events_removal(idx_start, idx_stop, good_event)
        idx_sup_thr = idx_sup_thr[good_idx]

        # Export info
        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)
        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)

###########################################################################
# MUSCLE TWITCHES DETECTION
###########################################################################


def mtdetect(elec, sf, threshold, hypno, rem_only, fmin=0., fmax=50.,
             tmin=800, tmax=2500, min_distance_ms=1000, welch_win_s=15,
             delta_thr=.5, min_amp=10, max_amp=400):
    """Perform a detection of muscle twicthes (MT).

    Sampling frequency must be at least 1000 Hz.

    Parameters
    ----------
    elec : array_like
        EMG signal
    sf : float
        Downsampling frequency
    threshold : float
        Number of standard deviation to use as threshold
        Threshold is defined as: mean + X * std(hilbert envelope)
    hypno : array_like
        Hypnogram vector, same length as elec
        Vector with only 0 if no hypnogram is loaded
    rem_only : bool
        Perfom detection only on NREM sleep period
    fmin : float | 0.
        Lower bandpass frequency
    fmax : float | 50.
        Higher bandpass frequency
    tmin : int | 800
        Minimum duration (ms) of MT
    tmax : int | 2500
        Maximum duration (ms) of MT
    min_distance_ms : int | 1000
        Minimum distance (in ms) between 2 MTs to consider them as
        two distinct events
    welch_win_s : int | 15
        Time window (s) of Welch spectrum
    delta_thr : float | .5
        Threshold of delta normalized bandpower, above which detected
        events are probably artefacts.
    max_amp : int | 400
        Maximum amplitude of Muscle Twitches. Above this threshold,
        detected events are probably artefacts.

    Returns
    -------
    idx_sup_thr : array_like
        Array of supra-threshold indices
    number : int
        Number of detected MTs
    density : float
        Number of MTs per minutes of data
    duration_ms : float
        Duration (ms) of each MT detected
    """
    if rem_only and 4 in hypno:
        elec[(np.where(hypno < 4))] = 0
        length = np.count_nonzero(elec)
        idx_zero = np.where(elec == 0)
    else:
        length = max(elec.shape)

    # Morlet's envelope
    analytic = morlet(elec, sf, np.mean([fmin, fmax]))
    amplitude = np.abs(analytic)
    amplitude = movingaverage(amplitude, sf, sf)

    # Define threshold
    if rem_only and 4 in hypno:
        id_th = np.setdiff1d(np.arange(elec.size), idx_zero)
    else:
        # Remove period with too much delta power (N2 - N3)
        delta_nfpow = welch_power(elec, 0.5, 2, sf, welch_win_s, norm=True)
        delta_nfpow = np.repeat(delta_nfpow, welch_win_s * sf)
        id_th = np.setdiff1d(np.arange(elec.size), np.where(
            delta_nfpow > delta_thr)[0])

    # Remove extreme values
    id_th = np.setdiff1d(id_th, np.where(abs(elec) > 400)[0])

    # Find supra-threshold values
    thresh = np.mean(amplitude[id_th]) + threshold * np.std(amplitude[id_th])
    idx_sup_thr = np.where(amplitude > thresh)[0]

    if idx_sup_thr.size:

        # Find MTs separated by less than min_distance_ms
        idx_sup_thr = _events_distance_fill(idx_sup_thr, min_distance_ms, sf)

        _, _, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)

        # Amplitude criteria
        mt_amp, _ = _events_amplitude(elec, idx_sup_thr, idx_start, idx_stop,
                                      sf)
        good_amp = np.where(np.logical_and(mt_amp > min_amp,
                                           mt_amp < max_amp))[0]
        good_idx = _events_removal(idx_start, idx_stop, good_amp)

        # Duration criteria
        _, duration_ms, idx_start, idx_stop = _events_duration(idx_sup_thr, sf)
        good_dur = np.where(np.logical_and(duration_ms > tmin,
                                           duration_ms < tmax))[0]
        good_idx = _events_removal(idx_start, idx_stop, good_dur)

        # Keep only good events
        idx_sup_thr = idx_sup_thr[good_idx]
        number, duration_ms, _, _ = _events_duration(idx_sup_thr, sf)
        density = number / (length / sf / 60.)

        return idx_sup_thr, number, density, duration_ms

    else:
        return np.array([], dtype=int), 0., 0., np.array([], dtype=int)


###########################################################################
# PEAKS DETECTION
###########################################################################


def peakdetect(sf, y_axis, x_axis=None, lookahead=200, delta=1., get='max',
               threshold='auto'):
    """Perform a peak detection.

    Converted from/based on a MATLAB script at:
    http://billauer.co.il/peakdet.html
    Original script :
    https://github.com/DiamondLightSource/auto_tomo_calibration-experimental/
    blob/master/old_code_scripts/peak_detect.py

    function for detecting local maxima and minima in a signal.
    Discovers peaks by searching for values which are surrounded by lower
    or larger values for maxima and minima respectively

    Parameters
    ----------
    sf : float
        The sampling frequency.
    y_axis : array_like
        Row vector containing the data.
    x_axis : array_like
        Row vector for the time axis. If omitted an index of the y_axis is
        used.
    lookahead : int | 200
        Distance to look ahead from a peak candidate to determine if
        it is the actual peak.
        '(samples / period) / f' where '4 >= f >= 1.25' might be a good
        value
    delta : float | 1.
        This specifies a minimum difference between a peak and the
        following points, before a peak may be considered a peak. Useful
        to hinder the function from picking up false peaks towards to end
        of the signal. To work well delta should be set to
        delta >= RMSnoise * 5.
        When omitted delta function causes a 20% decrease in speed.
        When used Correctly it can double the speed of the function
    get : string | 'max'
        Get either minimum values ('min'), maximum ('max') or min and max
        ('minmax').
    threshold : string/float | None
        Use a threshold to ignore values. Use None for no threshold, 'auto'
        to use the signal deviation or a float number for specific
        threshold.

    Returns
    -------
    index : array_like
        A row vector containing the index of maximum / minimum.
    number : int
        Number of peaks.
    density : float
        Density of peaks.
    """
    # ============== CHECK DATA ==============
    if x_axis is None:
        x_axis = range(len(y_axis))
    # Check length :
    if len(y_axis) != len(x_axis):
        raise ValueError("Input vectors y_axis and x_axis must have same "
                         "length")
    # Needs to be a numpy array
    y_axis, x_axis = np.asarray(y_axis), np.asarray(x_axis)

    # store data length for later use
    length = len(y_axis)

    # Lookahead  & delta checking :
    if lookahead < 1:
        raise ValueError("Lookahead must be '1' or above in value")
    if not (np.isscalar(delta) and delta >= 0):
        raise ValueError("delta must be a positive number")

    # Check get :
    if get not in ['min', 'max', 'minmax']:
        raise ValueError("The get parameter must either be 'min', 'max' or"
                         " 'minmax'")

    # ============== PRE-ALLOCATION ==============
    max_peaks, min_peaks = [], []
    dump = []   # Used to pop the first hit which almost always is false

    # maxima and minima candidates are temporarily stored in
    # mx and mn respectively
    mn, mx = np.Inf, -np.Inf

    # ============== THRESHOLD ==============
    if threshold is not None:
        if threshold is 'auto':
            threshold = np.std(y_axis)
        # Detrend / demean y-axis :
        y_axisp = detrend(y_axis)
        y_axisp -= y_axisp.mean()
        # Find values above threshold :
        above = np.abs(y_axisp) >= threshold
        zp = zip(np.arange(length)[above], x_axis[above], y_axis[above])
    else:
        zp = zip(np.arange(length)[:-lookahead], x_axis[:-lookahead],
                 y_axis[:-lookahead])

    # ============== FIND MIN / MAX PEAKS ==============
    # Only detect peak if there is 'lookahead' amount of points after it
    for index, x, y in zp:
        if y > mx:
            mx = y
        if y < mn:
            mn = y

        # ==== Look for max ====
        if y < mx - delta and mx != np.Inf:
            # Maxima peak candidate found
            # look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index + lookahead].max() < mx:
                max_peaks.append(index)
                dump.append(True)
                # set algorithm to only find minima now
                mx = np.Inf
                mn = np.Inf
                if index + lookahead >= length:
                    # end is within lookahead no more peaks can be found
                    break
                continue

        # ==== Look for max ====
        if y > mn + delta and mn != -np.Inf:
            # Minima peak candidate found
            # look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index + lookahead].min() > mn:
                min_peaks.append(index)
                dump.append(False)
                # set algorithm to only find maxima now
                mn = -np.Inf
                mx = -np.Inf
                if index + lookahead >= length:
                    # end is within lookahead no more peaks can be found
                    break

    if min_peaks and max_peaks:
        # ============== CLEAN ==============
        # Remove the false hit on the first value of the y_axis
        if threshold is None:
            if dump[0]:
                max_peaks.pop(0)
            else:
                min_peaks.pop(0)
            del dump

        # ============== MIN / MAX / MINMAX ==============
        if get == 'max':
            index = np.array(max_peaks)
        elif get == 'min':
            index = np.array(min_peaks)
        elif get == 'minmax':
            index = np.vstack((min_peaks, max_peaks))
        number = len(index)
        density = number / (len(y_axis) / sf / 60.)

        return index, number, density
    else:
        return np.array([]), 0., 0.
