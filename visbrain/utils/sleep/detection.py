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
from scipy.signal import hilbert, detrend, welch

from ..filtering import filt, morlet, morlet_power
from ..sigproc import derivative, tkeo, smoothing, normalization
from .event import (_events_distance_fill, _index_to_events, _events_to_index)

__all__ = ('kcdetect', 'spindlesdetect', 'remdetect', 'slowwavedetect',
           'mtdetect', 'peakdetect')

###########################################################################
# K-COMPLEX DETECTION
###########################################################################


def kcdetect(data, sf, proba_thr, amp_thr, hypno, nrem_only, tmin, tmax,
             kc_min_amp, kc_max_amp, fmin=.5, fmax=4., delta_thr=.75,
             smoothing_s=20, spindles_thresh=2., range_spin_sec=20,
             min_distance_ms=500.):
    """Perform a K-complex detection.

    Parameters
    ----------
    data : array_like
        eeg signal (preferably central electrodes)
    sf : float
        Downsampling frequency
    proba_thr : float
        Probability threshold (between 0 and 1)
    amp_thr : float
        Amplitude threshold
    hypno : array_like
        Hypnogram vector, same length as data
        Vector with only 0 if no hypnogram is loaded
    nrem_only : bool
        Perfom detection only on NREM sleep period
    tmin : float
        Minimum duration (ms) of K-complex
    tmax : float
        Maximum duration (ms) of K-complex
    kc_min_amp : float
        Minimum amplitude of K-complex
    kc_max_amp : float
        Maximum amplitude of K-complex
    fmin : float | .5
        High-pass cutoff frequency
    fmax : float | 4.
        Low-pass cutoff frequency
    delta_thr : float | .75
        Delta normalized power threshold. Value must be between 0 and 1.
        0 = No thresholding by delta bandpower
    smoothing_s : int | 20
        Time window (sec) for smoothing of delta band power
    spindles_thresh : float | 2.
        Number of standard deviations to compute spindles detection
    range_spin_sec : int | 20
        Duration of lookahead window for spindles detection (sec)
        Check for spindles that are comprised within
        -range_spin_sec/2 < KC < range_spin_sec/2
    min_distance_ms : float | 500.
        Minimum distance (ms) between two unique K-complexes

    Returns
    -------
    idx_kc : array_like
        Indices of detected K-complexes of shape (n_events, 2)
    """
    # Find if hypnogram is loaded :
    hyploaded = True if np.unique(hypno).size > 1 and nrem_only else False

    # PRE DETECTION
    # Compute delta band power using wavelet
    freqs = np.array([0.1, 4., 8., 12., 16., 30.])
    delta_npow = morlet_power(data, freqs, sf, norm=True)[0]
    delta_nfpow = smoothing(delta_npow, smoothing_s * sf)
    idx_no_delta = np.where(delta_nfpow < delta_thr)[0]
    idx_loc_delta = np.where(delta_npow > np.median(delta_npow))[0]

    # MAIN DETECTION
    # Bandpass filtering
    sig_filt = filt(sf, np.array([fmin, fmax]), data)
    # Taiger-Keaser energy operator
    sig_tkeo = tkeo(sig_filt)
    # Define hard and soft thresholds
    hard_thr = np.nanmean(sig_tkeo) + amp_thr * np.nanstd(sig_tkeo)
    soft_thr = 0.8 * hard_thr

    with np.errstate(divide='ignore', invalid='ignore'):
        idx_hard = np.where(sig_tkeo > hard_thr)[0]
        idx_soft = np.where(sig_tkeo > soft_thr)[0]

    # Find threshold-crossing indices of soft threshold
    idx_zc_soft = _events_to_index(idx_soft).flatten()

    if idx_hard.size == 0:
        return np.array([], dtype=int)

    # Initialize K-complexes index vector
    idx_kc = np.array([], dtype=int)
    # Fill gap between events separated by less than min_distance_ms
    idx_hard = _events_distance_fill(idx_hard, min_distance_ms, sf)
    # Get where K-complex start / end :
    idx_start, idx_stop = _events_to_index(idx_hard).T

    # Find true beginning / end using soft threshold
    for s in idx_start:
        d = s - idx_zc_soft
        soft_beg = d[d > 0].min()
        soft_end = np.abs(d[d < 0]).min()
        idx_kc = np.append(idx_kc, np.arange(s - soft_beg, s + soft_end))

    # Check if spindles are present in range_spin_sec
    idx_spin = spindlesdetect(data, sf, spindles_thresh, hypno, False)[0]
    idx_start, idx_stop = _events_to_index(idx_kc).T
    spin_bool = np.array([], dtype=np.bool)

    for idx, val in enumerate(idx_start):
        step = 0.5 * range_spin_sec * sf
        is_spin = np.in1d(np.arange(val - step, val + step, 1),
                          idx_spin, assume_unique=True)
        spin_bool = np.append(spin_bool, any(is_spin))

    kc_spin = np.where(spin_bool)[0]
    idx_kc_spin = _index_to_events(np.c_[idx_start, idx_stop][kc_spin])

    # Compute probability
    proba = np.zeros(shape=data.shape)
    proba[idx_kc] += 0.1
    proba[idx_no_delta] += 0.1
    proba[idx_loc_delta] += 0.1
    proba[idx_kc_spin] += 0.1

    if hyploaded:
        proba[hypno == -1] += -0.1
        proba[hypno == 0] += -0.2
        proba[hypno == 1] += 0
        proba[hypno == 2] += 0.1
        proba[hypno == 3] += -0.1
        proba[hypno == 4] += -0.2

    # Smooth and normalize probability vector
    proba = proba / 0.5 if hyploaded else proba / 0.4
    proba = smoothing(proba, sf)
    # Keep only proba >= proba_thr (user defined threshold)
    idx_kc = np.intersect1d(idx_kc, np.where(proba >= proba_thr)[0], True)

    if idx_kc.size == 0:
        return np.array([], dtype=int)

    # Morphological criteria
    idx_start, idx_stop = _events_to_index(idx_kc).T
    duration_ms = (idx_stop - idx_start) * (1000 / sf)

    # Remove events with bad duration
    good_dur = np.where(np.logical_and(duration_ms > tmin,
                                       duration_ms < tmax))[0]
    idx_kc = _index_to_events(np.c_[idx_start, idx_stop][good_dur])

    # Remove events with bad amplitude
    idx_start, idx_stop = _events_to_index(idx_kc).T
    amp = np.zeros(shape=idx_start.size)
    for i, (start, stop) in enumerate(zip(idx_start, idx_stop)):
        amp[i] = np.ptp(data[start:stop])
    good_amp = np.where(np.logical_and(amp > kc_min_amp,
                                       amp < kc_max_amp))[0]

    return np.c_[idx_start, idx_stop][good_amp]


###########################################################################
# SPINDLES DETECTION
###########################################################################

def spindlesdetect(data, sf, threshold, hypno, nrem_only, fmin=12., fmax=14.,
                   tmin=300, tmax=3000, method='wavelet', min_distance_ms=300,
                   sigma_thr=0.2, adapt_band=True, return_full=False):
    """Perform a sleep spindles detection.

    Parameters
    ----------
    data : array_like
        eeg signal (preferably central electrodes)
    sf : float
        Downsampling frequency
    threshold : float
        Number of standard deviation to use as threshold
        Threshold is defined as: mean + X * std(derivative)
    hypno : array_like
        Hypnogram vector, same length as data
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
    min_distance_ms : int | 300
        Minimum distance (in ms) between two spindles to consider them as
        two distinct spindles
    sigma_thr : float | 0.2
        Sigma band-wise normalized power threshold (between 0 and 1)
    adapt_band : bool | True
        If true, adapt sigma band limit by finding the peak sigma freq.
    return_full : bool | False
        If true, return more variables (start, stop, sigma, hard and soft
        thresh) Used in function write_fig_spindles

    Returns
    -------
    idx_spindles : array_like
        Indices of detected spindles of shape (n_events, 2)
    """
    # Pre-detection
    if adapt_band:
        # Find peak sigma frequency
        f, pxx_den = welch(data, sf)
        mfs = f[pxx_den == pxx_den[np.where((f >= 11) & (f < 16))].max()][0]
        fmin = mfs - 1
        fmax = mfs + 1

    # Compute relative sigma power
    freqs = np.array([0.5, 4., 8., fmin, fmax])
    sigma_npow = morlet_power(data, freqs, sf, norm=True)[-1]
    sigma_nfpow = smoothing(sigma_npow, sf * (tmin / 1000))
    # Vector of sigma power supra-threshold values
    idx_sigma = np.where(sigma_nfpow > sigma_thr)[0]

    # Get complex decomposition of filtered data :
    if method == 'hilbert':
        # Bandpass filter
        data_filt = filt(sf, [fmin, fmax], data, order=4)
        if data.size % 2:
            analytic = hilbert(data_filt)
        else:
            analytic = hilbert(data_filt[:-1], len(data_filt))
    elif method == 'wavelet':
        analytic = morlet(data, sf, np.mean([fmin, fmax]))

    # Get envelope
    amplitude = np.abs(analytic)

    # Check "Detect only for NREM sleep"
    if np.unique(hypno).size > 1 and nrem_only:
        idx_zero = np.where(np.logical_or(hypno < 1, hypno == 4))[0]
        amplitude[idx_zero] = np.nan
        length = max(data.shape) - idx_zero.size
    else:
        length = max(data.shape)

    # Define hard and soft thresholds
    hard_thr = np.nanmean(amplitude) + threshold * np.nanstd(amplitude)
    soft_thr = 0.5 * hard_thr

    with np.errstate(divide='ignore', invalid='ignore'):
        idx_hard = np.where(amplitude > hard_thr)[0]
        idx_soft = np.where(amplitude > soft_thr)[0]

    # Find threshold-crossing indices of soft threshold
    idx_zc_soft = _events_to_index(idx_soft).flatten()

    if idx_hard.size > 0:
        # Initialize spindles vector
        idx_spindles = np.array([], dtype=int)

        # Keep only period with high relative sigma power
        idx_hard = np.intersect1d(idx_hard, idx_sigma, True)

        # Fill gap between events separated by less than min_distance_ms
        idx_hard = _events_distance_fill(idx_hard, min_distance_ms, sf)

        # Get where spindles start / end :
        idx_start, idx_stop = _events_to_index(idx_hard).T

        # Find true beginning / end using soft threshold
        for s in idx_start:
            d = s - idx_zc_soft
            # Find distance to nearest soft threshold crossing before start
            soft_beg = d[d > 0].min()
            # Find distance to nearest soft threshold crossing after end
            soft_end = np.abs(d[d < 0]).min()
            idx_spindles = np.append(idx_spindles, np.arange(
                                     s - soft_beg, s + soft_end))

        # Fill gap between events separated by less than min_distance_ms
        idx_spindles = _events_distance_fill(idx_spindles, min_distance_ms, sf)

        # Get duration
        idx_start, idx_stop = _events_to_index(idx_spindles).T
        duration_ms = (idx_stop - idx_start) * (1000 / sf)

        # Remove events with bad duration
        good_dur = np.where(np.logical_and(duration_ms > tmin,
                                           duration_ms < tmax))[0]

        if idx_spindles.size == 0:
            return np.array([], dtype=int)

        if return_full:
            # Compute number, duration, density
            idx_start, idx_stop = np.c_[idx_start, idx_stop][good_dur].T
            number = idx_start.size
            duration_ms = (idx_stop - idx_start) * (1000 / sf)
            density = number / (length / sf / 60.)

            # Compute mean power of each spindles
            pwrs = np.zeros(shape=number)
            for i, (start, stop) in enumerate(zip(idx_start, idx_stop)):
                ind_pwr = morlet_power(data[start:stop], [fmin, fmax], sf,
                                       norm=False)[0]
                pwrs[i] = np.mean(ind_pwr)
            # Normalize by dividing by the mean
            normalization(pwrs, norm=2)

            return (idx_spindles, number, density, duration_ms, pwrs,
                    idx_start, idx_stop, hard_thr, soft_thr, idx_sigma,
                    fmin, fmax, sigma_nfpow, amplitude, sigma_thr)
        else:
            return np.c_[idx_start, idx_stop][good_dur]


###########################################################################
# REM DETECTION
###########################################################################


def remdetect(data, sf, hypno, rem_only, threshold, tmin=300, tmax=800,
              min_distance_ms=300, smoothing_ms=200, deriv_ms=50):
    """Perform a rapid eye movement (REM) detection.

    Function to perform a semi-automatic detection of rapid eye movements
    (REM) during REM sleep.

    Parameters
    ----------
    data: array_like
        EOG signal
    sf: float
        Downsampling frequency
    hypno: array_like
        Hypnogram vector, same length as data
        Vector with only 0 if no hypnogram is loaded
    rem_only: bool
        Perfom detection only on REM sleep period
    threshold: float
        Number of standard deviation of the derivative signal
        Threshold is defined as: mean + X * std(derivative)
    tmin : int | 300
        Minimum duration (ms) of rapid eye movement
    tmax : int | 1500
        Maximum duration (ms) of rapid eye movement
    min_distance_ms : int | 300
        Minimum distance (ms) between two saccades to consider them as two
        distinct events.
    smoothing_ms : int | 200 (= 5 Hz)
        Time (ms) window of the smoothing.
    deriv_ms : int | 50
        Time (ms) window of derivative computation

    Returns
    -------
    idx_rem: array_like
        Indices of detected REMs of shape (n_events, 2)
    """
    # Compute relative beta power
    freqs = np.array([0.5, 4., 8., 12, 40])
    beta_npow = morlet_power(data, freqs, sf, norm=True)[-1]
    beta_nfpow = smoothing(beta_npow, sf * (tmin / 1000))
    # Vector of beta power supra-threshold values
    idx_beta = np.where(beta_nfpow < np.percentile(beta_nfpow, 60))[0]

    # Compute smoothed derivative
    sm_sig = smoothing(data, sf * (smoothing_ms / 1000))
    deriv = derivative(sm_sig, deriv_ms, sf)
    deriv = smoothing(deriv, sf * (smoothing_ms / 1000))

    if rem_only and 4 in hypno:
        idx_zero = np.where(hypno < 4)[0]
        deriv[idx_zero] = np.nan

    # Define hard and soft thresholds
    hard_thr = np.nanmean(deriv) + threshold * np.nanstd(deriv)
    soft_thr = 0.5 * hard_thr

    with np.errstate(divide='ignore', invalid='ignore'):
        idx_hard = np.where(deriv > hard_thr)[0]
        idx_soft = np.where(deriv > soft_thr)[0]

    # Find threshold-crossing indices of soft threshold
    idx_zc_soft = _events_to_index(idx_soft).flatten()

    if idx_hard.size == 0:
        return np.array([], dtype=int)

    # Initialize rem vector
    idx_rem = np.array([], dtype=int)

    # Keep only period with low relative beta power (i.e. remove artefact)
    idx_hard = np.intersect1d(idx_hard, idx_beta, True)

    # Fill gap between events separated by less than min_distance_ms
    idx_hard = _events_distance_fill(idx_hard, min_distance_ms, sf)

    # Get where spindles start / end :
    idx_start, idx_stop = _events_to_index(idx_hard).T

    # Find true beginning / end using soft threshold
    for s in idx_start:
        d = s - idx_zc_soft
        # Find distance to nearest soft threshold crossing before start
        soft_beg = d[d > 0].min()
        # Find distance to nearest soft threshold crossing after end
        soft_end = np.abs(d[d < 0]).min()
        idx_rem = np.append(idx_rem, np.arange(s - soft_beg, s + soft_end))

    # Fill gap between events separated by less than min_distance_ms
    idx_rem = _events_distance_fill(idx_rem, min_distance_ms, sf)

    # Get duration
    idx_start, idx_stop = _events_to_index(idx_rem).T
    duration_ms = (idx_stop - idx_start) * (1000 / sf)

    # Remove events with bad duration
    good_dur = np.where(np.logical_and(duration_ms > tmin,
                                       duration_ms < tmax))[0]

    return np.c_[idx_start, idx_stop][good_dur]


###########################################################################
# SLOW WAVE DETECTION
###########################################################################


def slowwavedetect(data, sf, threshold, min_amp=70., max_amp=400., tmin=1000.,
                   fmin=.5, fmax=4., smoothing_s=20):
    """Perform a Slow Wave detection.

    Parameters
    ----------
    data : array_like
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
    tmin : float | 1000.
        Minimum duration (ms) of slow waves
    fmin  : float | .5
        High-pass frequency
    fmax  : float | 2.
        Low-pass frequency
    smoothing_s  : int | 20
        Smoothing window in seconds

    Returns
    -------
    idx_sw : array_like
        Indices of slow waves of shape (n_events, 2)
    """
    filt_fmax = np.minimum(45, sf / 2.0 - 0.75)  # protect Nyquist
    data_filt = filt(sf, [.1, filt_fmax], data)

    # Compute relative delta band-power
    delta_nfpow = morlet_power(data_filt, [fmin, fmax, 8, 12, 16, 30], sf,
                               norm=True)[0, :]
    delta_nfpow = smoothing(delta_nfpow, smoothing_s * sf)

    # Normalized power criteria
    idx_sw = np.where(delta_nfpow > threshold)[0]

    if idx_sw.size == 0:
        return np.array([], dtype=int)

    # Get where slow waves start / end :
    idx_start, idx_stop = _events_to_index(idx_sw).T
    duration_ms = (idx_stop - idx_start) * (1000 / sf)

    # Check amplitude and duration
    amp = np.zeros(shape=idx_start.shape)
    for idx, (start, stop) in enumerate(zip(idx_start, idx_stop)):
        amp[idx] = np.ptp(data[start:stop])
    good_amp = np.where(np.logical_and(amp > min_amp, amp < max_amp))[0]
    good_dur = np.where(duration_ms > tmin)[0]
    good_event = np.intersect1d(good_amp, good_dur, True)
    idx_sw = np.c_[idx_start, idx_stop][good_event]

    if idx_sw.size == 0:
        return np.array([], dtype=int)

    return idx_sw


###########################################################################
# MUSCLE TWITCHES DETECTION
###########################################################################


def mtdetect(data, sf, threshold, hypno, rem_only, fmin=0., fmax=50.,
             tmin=800, tmax=2500, min_distance_ms=1000, min_amp=50,
             max_amp=400):
    """Perform a detection of muscle twitches (MT).

    Sampling frequency must be at least 1000 Hz.

    Parameters
    ----------
    data : array_like
        EMG signal
    sf : float
        Downsampling frequency
    threshold : float
        Number of standard deviation to use as threshold
        Threshold is defined as: mean + X * std(hilbert envelope)
    hypno : array_like
        Hypnogram vector, same length as data
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
    min_amp : int | 50
        Minimum amplitude of Muscle Twitches
    max_amp : int | 400
        Maximum amplitude of Muscle Twitches. Above this threshold,
        detected events are probably artefacts

    Returns
    -------
    idx_mt : array_like
        Indices of MTs of shape (n_events, 2)
    """
    # PRE DETECTION
    # Morlet envelope
    analytic = morlet(data, sf, np.mean([fmin, fmax]))
    amplitude = np.abs(analytic)
    amplitude = smoothing(amplitude, sf * (tmin / 1000))
    # Morlet power in delta band
    delta_nfpow = morlet_power(data, [0.5, 4], sf, norm=False)
    idx_high_delta = np.where(delta_nfpow > np.percentile(delta_nfpow, 75))[0]

    if rem_only and 4 in hypno:
        idx_zero = np.where(hypno < 4)[0]
        amplitude[idx_zero] = np.nan

    # Define hard threshold
    hard_thr = np.nanmean(amplitude) + threshold * np.nanstd(amplitude)

    with np.errstate(divide='ignore', invalid='ignore'):
        idx_hard = np.where(amplitude > hard_thr)[0]

    if idx_hard.size == 0:
        return np.array([], dtype=int)

    # Keep only MT in period with low relative delta power
    idx_hard = np.setdiff1d(idx_hard, idx_high_delta, True)

    # Fill gap between events separated by less than min_distance_ms
    idx_hard = _events_distance_fill(idx_hard, min_distance_ms, sf)

    # MORPHOLOGICAL CRITERIA
    idx_start, idx_stop = _events_to_index(idx_hard).T
    duration_ms = (idx_stop - idx_start) * (1000 / sf)

    # Remove events with bad duration
    good_dur = np.where(np.logical_and(duration_ms > tmin,
                                       duration_ms < tmax))[0]
    idx_mt = _index_to_events(np.c_[idx_start, idx_stop][good_dur])

    # Remove events with bad amplitude
    idx_start, idx_stop = _events_to_index(idx_mt).T
    amp = np.zeros(shape=idx_start.size)
    for i, (start, stop) in enumerate(zip(idx_start, idx_stop)):
        amp[i] = np.ptp(data[start:stop])
    good_amp = np.where(np.logical_and(amp > min_amp,
                                       amp < max_amp))[0]
    idx_mt = np.c_[idx_start, idx_stop][good_amp]

    # Compute number, duration, density
    if idx_mt.size == 0:
        return np.array([], dtype=int)

    return idx_mt


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
        A vector containing peak indices of shape (n_events, 2)
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

        return np.c_[index, index]
    else:
        return np.array([])
