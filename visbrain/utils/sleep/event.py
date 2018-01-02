"""Goup of functions for index / event managment."""

import numpy as np

__all__ = ('_events_distance_fill', '_events_to_index', '_index_to_events')


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
