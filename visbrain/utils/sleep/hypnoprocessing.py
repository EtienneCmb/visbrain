"""Hypnogram related functions."""

import numpy as np

__all__ = ('transient', 'sleepstats')


def transient(data, xvec=None):
    """Perform a transient detection on hypnogram.

    Parameters
    ----------
    data : array_like
        The hypnogram data.
    xvec : array_like | None
        The time vector to use. If None, np.arange(len(data)) will be used
        instead.

    Returns
    -------
    t : array_like
        Hypnogram's transients.
    st : array_like
        Either the transient index (as type int) if xvec is None, or the
        converted version if xvec is not None.
    stages : array_like
        The stages for each segment.
    """
    # Transient detection :
    t = list(np.nonzero(np.abs(data[:-1] - data[1:]))[0])
    # Add first and last points :
    idx = np.vstack((np.array([-1] + t) + 1, np.array(t + [len(data) - 1]))).T
    # Get stages :
    stages = data[idx[:, 0]]
    # Convert (if needed) :
    if (xvec is not None) and (len(xvec) == len(data)):
        st = idx.copy().astype(float)
        st[:, 0] = xvec[idx[:, 0]]
        st[:, 1] = xvec[idx[:, 1]]
    else:
        st = idx

    return np.array(t), st, stages.astype(int)


def sleepstats(hypno, sf_hyp):
    """Compute sleep stats from an hypnogram vector.

    Sleep statistics specifications:
    ======================================================================

    All values except SE and percentages are expressed in minutes

    - Time in Bed (TIB): total duration of the hypnogram.

    - Total Dark Time (TDT): duration of the hypnogram from beginning
      to last period of sleep.

    - Sleep Period Time (SPT): duration from first to last period of sleep.

    - Wake After Sleep Onset (WASO): duration of wake periods within SPT

    - Sleep Efficiency (SE): TST / TDT * 100 (%).

    - Total Sleep Time (TST): SPT - WASO.

    - W, N1, N2, N3 and REM: sleep stages duration.

    - % (W, ... REM): sleep stages duration expressed in percentages of TDT.

    - Latencies: latencies of sleep stages from the beginning of the record.

    ======================================================================

    Parameters
    ----------
    hypno : array_like
        Hypnogram vector
    sf_hyp : float
        The sampling frequency of the hypnogram

    Returns
    -------
    stats: dict
        Sleep statistics (expressed in minutes)
    """
    stats = {}
    tov = np.nan

    # Downsample to 1 value per second
    hypno = hypno[::int(sf_hyp)]

    stats['TIB'] = len(hypno)
    stats['TDT'] = np.where(hypno != 0)[0].max() if np.nonzero(
        hypno)[0].size else tov

    # Duration of each sleep stages
    stats['Art'] = hypno[hypno == -1].size
    stats['W'] = hypno[hypno == 0].size
    stats['N1'] = hypno[hypno == 1].size
    stats['N2'] = hypno[hypno == 2].size
    stats['N3'] = hypno[hypno == 3].size
    stats['REM'] = hypno[hypno == 4].size

    # Sleep stage latencies
    stats['LatN1'] = np.where(hypno == 1)[0].min() if 1 in hypno else tov
    stats['LatN2'] = np.where(hypno == 2)[0].min() if 2 in hypno else tov
    stats['LatN3'] = np.where(hypno == 3)[0].min() if 3 in hypno else tov
    stats['LatREM'] = np.where(hypno == 4)[0].min() if 4 in hypno else tov

    if not np.isnan(stats['LatN1']) and not np.isnan(stats['TDT']):
        hypno_s = hypno[stats['LatN1']:stats['TDT']]

        stats['SPT'] = hypno_s.size
        stats['WASO'] = hypno_s[hypno_s == 0].size
        stats['TST'] = stats['SPT'] - stats['WASO']
    else:
        stats['SPT'] = tov
        stats['WASO'] = tov
        stats['TST'] = tov

    # Convert to minutes
    for key, value in stats.items():
        stats[key] = value / 60

    stats['SE'] = np.round(stats['TST'] / stats['TDT'] * 100., 2)
    stats['Units'] = 'minutes'

    return stats
