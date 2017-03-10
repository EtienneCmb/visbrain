"""Hypnogram related functions."""

import numpy as np
from os import path

__all__ = ['sleepstats', 'transient']


def transient(data, xvec=None):
    """Perform a transient detection on hypnogram.

    Args:
        data: np.ndarray
            The hypnogram data.

    Kargs:
        xvec: np.ndarray, optional, (def: None)
            The time vector to use. If None, np.arange(len(data)) will be used
            instead.

    Returns:
        t: np.ndarray
            Hypnogram's transients.

        idx: np.ndarray
            Either the transient index (as type int) if xvec is None, or the
            converted version if xvec is not None.

        stages: np.ndarray
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


def sleepstats(file, hypno, sf=100, time_window=30.):
    """Compute sleep stats from an hypnogram vector.

    Args:
        file: str
            Filename (with full path) to sleep dataset.

        hypno: np.ndarray
            Hypnogram vector

        sf: int (def 100)
            Sampling frequency of hypnogram / data

        time_window: int (def 30)
            Length (seconds) of the time window on which to compute stats

    Return:
        stats: dict
            Sleep statistics (expressed in minutes)


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

    """
    # Get a step (integer) and resample to get one value per 30 seconds :
    step = int(round(sf * time_window))
    hypno = hypno[::step]

    stats = {}
    tov = np.nan

    stats['Duration (TIB)_3'] = hypno.size
    stats['TDT_4'] = np.where(hypno != 0)[0].max() if np.nonzero(
        hypno)[0].size else tov

    # Duration of each sleep stages
    stats['Art_5'] = hypno[hypno == -1].size
    stats['W_6'] = hypno[hypno == 0].size
    stats['N1_7'] = hypno[hypno == 1].size
    stats['N2_8'] = hypno[hypno == 2].size
    stats['N3_9'] = hypno[hypno == 3].size
    stats['REM_10'] = hypno[hypno == 4].size

    # Sleep stage latencies
    stats['LatN1_11'] = np.where(hypno == 1)[0].min() if 1 in hypno else tov
    stats['LatN2_12'] = np.where(hypno == 2)[0].min() if 2 in hypno else tov
    stats['LatN3_13'] = np.where(hypno == 3)[0].min() if 3 in hypno else tov
    stats['LatREM_14'] = np.where(hypno == 4)[0].min() if 4 in hypno else tov

    if not np.isnan(stats['LatN1_11']) and not np.isnan(stats['TDT_4']):
        hypno_s = hypno[stats['LatN1_11']:stats['TDT_4']]

        stats['SPT_15'] = hypno_s.size
        stats['WASO_16'] = hypno_s[hypno_s == 0].size
        stats['TST_17'] = stats['SPT_15'] - stats['WASO_16']
    else:
        stats['SPT_15'] = np.nan
        stats['WASO_16'] = np.nan
        stats['TST_17'] = np.nan

    # Convert to minutes
    for key, value in stats.items():
        stats[key] = value / (60. / time_window)

    # Add global informations
    if file == None:
        stats['Filename_0'] = ''
    else:
        stats['Filename_0'] = path.basename(file)
    stats['Downsampling_1'] = str(int(sf)) + " Hz"
    stats['Units_2'] = 'minutes'

    stats['SE (%)_18'] = np.round(stats['TST_17'] / stats['TDT_4'] * 100., 2)

    # Percentages of TDT
    # stats['%Art_18'] = stats['Art_4'] / stats['TDT_3'] * 100.
    # stats['%W_19'] = stats['W_5'] / stats['TDT_3'] * 100.
    # stats['%N1_20'] = stats['N1_6'] / stats['TDT_3'] * 100.
    # stats['%N2_21'] = stats['N2_7'] / stats['TDT_3'] * 100.
    # stats['%N3_22'] = stats['N3_8'] / stats['TDT_3'] * 100.
    # stats['%REM_23'] = stats['REM_9'] / stats['TDT_3'] * 100.

    return stats
