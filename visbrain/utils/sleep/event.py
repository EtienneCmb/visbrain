"""Goup of functions for index / event managment."""

import numpy as np
from scipy.signal import hilbert

__all__ = ('_events_duration', '_events_removal', '_events_distance_fill',
           '_events_mean_freq', '_events_amplitude', '_events_to_index',
           '_index_to_events')


def _events_duration(index, sf):
    """Compute spindles/REM duration in ms.

    Parameters
    ----------
    index : array_like
        Index of events locations.
    sf : float
        The sampling frequency.

    Returns
    -------
    number : int
        Number of events
    duration_ms : array_like
        Duration of each event
    idx_start : array_like
        Array of integers where each event begin.
    idx_end : array_like
        Array of integers where each event finish.
    """
    # Find boolean values where each spindle start :
    bool_break = (index[1:] - index[:-1]) != 1
    # Get event number :
    number = bool_break.sum() + 1
    # Build starting / ending spindles index :
    idx_start = np.hstack([np.array([0]), np.where(bool_break)[0] + 1])
    idx_stop = np.hstack((idx_start[1::], len(index) - 1))
    # Compute duration :
    duration_ms = np.diff(np.hstack((idx_start, idx_stop[-1]))) * (1000. / sf)

    return number, duration_ms, idx_start, idx_stop


def _events_removal(idx_start, idx_stop, good_dur):
    """Remove events that do not have the good duration.

    Parameters
    ----------
    idx_start : array_like
        Starting indices of event.
    idx_stop : array_like
        Ending indices of event.
    good_dur : array_like
        Indices of event having a proper duration.

    Returns
    -------
    good_idx : array_like
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


def _events_distance_fill(index, min_distance_ms, sf):
    """Remove events that do not have the good duration.

    Parameters
    ----------
    index : array_like
        Indices of supra-threshold events.
    min_distance_ms : int
        Minimum distance (ms) between two events to consider them as two
        distinct events
    sf : float
        Sampling frequency of the data (Hz)

    Returns
    -------
    f_index : array_like
        Filled (corrected) Indices of supra-threshold events
    """
    # Convert min_distance_ms
    min_distance = min_distance_ms / 1000. * sf
    idx_diff = np.diff(index)
    condition = idx_diff > 1
    idx_distance = np.where(condition)[0]
    distance = idx_diff[condition]
    bad = idx_distance[np.where(distance < min_distance)[0]]
    # Fill gap between events separated with less than min_distance_ms
    if len(bad) > 0:
        fill = np.hstack([np.arange(index[j] + 1, index[j + 1])
                          for i, j in enumerate(bad)])
        f_index = np.sort(np.append(index, fill))
        return f_index
    else:
        return index


def _events_mean_freq(x, idx_sup_thr, idx_start, idx_stop, sf):
    """Remove events that do not have the good duration.

    Parameters
    ----------
    x : array_like
        Array of data of shape (N,)
    idx_sup_thr : array_like
        Vector of supra-threshold events
    idx_start : array_like
        Starting indices of event.
    idx_stop : array_like
        Ending indices of event.
    sf : int
        Sampling frequency of the data (Hz)

    Returns
    -------
    mfreq : array_like
        Mean frequency of each event (Hz)
    """
    if x.size % 2:
        analytic = hilbert(x)
    else:
        analytic = hilbert(x[:-1], len(x))
    phase = np.unwrap(np.angle(analytic))
    inst_freq = abs(np.diff(phase) / (2.0 * np.pi) * sf)
    mfreq = np.array([])
    # Loop on each event
    for i, j in zip(idx_start, idx_stop):
        idx_event = np.arange(idx_sup_thr[i], idx_sup_thr[j])
        mfreq = np.append(mfreq, np.mean(inst_freq[idx_event]))

    return mfreq


def _events_amplitude(x, idx_sup_thr, idx_start, idx_stop, sf):
    """Find amplitude range of events.

    Parameters
    ----------
    x : array_like
        Array of data of shape (N,)
    idx_sup_thr : array_like
        Vector of supra-threshold events
    idx_start : array_like
        Starting indices of event.
    idx_stop : array_like
        Ending indices of event.
    sf : int
        Sampling frequency of the data (Hz)

    Returns
    -------
    amp_range : array_like
        Amplitude range (max - min) of each event
    distance_ms : array_like
        Distance (ms) between min and max
    """
    amp_range = np.array([])
    distance_ms = np.array([])
    # Loop on each event
    for i, j in zip(idx_start, idx_stop):
        idx_event = np.arange(idx_sup_thr[i], idx_sup_thr[j])
        if idx_event.size > 0:
            amp_range = np.append(amp_range, np.ptp(x[idx_event]))
            distance = np.abs(np.argmax(x[idx_event]) - np.argmin(
                x[idx_event]))
            distance_ms = np.append(distance_ms, distance / sf * 1000)
        else:
            amp_range = 0.
            distance_ms = 0.

    return amp_range, distance_ms


def _events_to_index(x):
    """Convert a continuous vector of indices into an 2D array (start, end).

    Parameters
    ----------
    x : array_like
        Array of indices.

    Returns
    -------
    xidx : array_like
        An array of shape (n_events, 2) where the dimension 2 refer to the
        indices where each event start and finish.
    """
    # Split indices where it stopped :
    sp = np.split(x, np.where(np.diff(x) != 1)[0] + 1)
    # Return (start, end) :
    return np.array([[k[0], k[-1]] for k in sp]).astype(int)


def _index_to_events(x):
    """Convert a 2D (start, end) array into a continuous one.

    Parameters
    ----------
    x : array_like
        2D array of indicies.

    Returns
    -------
    index : array_like
        Continuous array of indicies.
    """
    index = np.array([])
    for k in range(x.shape[0]):
        index = np.append(index, np.arange(x[k, 0], x[k, 1] + 1))
    return index.astype(int)
