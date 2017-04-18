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


def sleepstats(file, hypno, N, sf=100., sfori=1000., time_window=30.):
    """Compute sleep stats from an hypnogram vector.

    Args:
        file: str
            Filename (with full path) to sleep dataset.

        hypno: np.ndarray
            Hypnogram vector

        N: int
            Original data shape before down-sampling.

    Kargs
        sf: float, optional, (def: 100.)
            The sampling frequency of displayed elements (could be the
            down-sampling frequency)

        sfori: float, optional, (def: 1000.)
            The original sampling frequency before any down-sampling.

        time_window: float, optional, (def: 30.)
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
    step = int(hypno.shape / np.round(N / (sfori * time_window)))
    hypno = hypno[::step]

    stats = {}
    tov = np.nan

    stats['TDT_5'] = np.where(hypno != 0)[0].max() if np.nonzero(
        hypno)[0].size else tov

    # Duration of each sleep stages
    stats['Art_6'] = hypno[hypno == -1].size
    stats['W_7'] = hypno[hypno == 0].size
    stats['N1_8'] = hypno[hypno == 1].size
    stats['N2_9'] = hypno[hypno == 2].size
    stats['N3_10'] = hypno[hypno == 3].size
    stats['REM_11'] = hypno[hypno == 4].size

    # Sleep stage latencies
    stats['LatN1_12'] = np.where(hypno == 1)[0].min() if 1 in hypno else tov
    stats['LatN2_13'] = np.where(hypno == 2)[0].min() if 2 in hypno else tov
    stats['LatN3_14'] = np.where(hypno == 3)[0].min() if 3 in hypno else tov
    stats['LatREM_15'] = np.where(hypno == 4)[0].min() if 4 in hypno else tov

    if not np.isnan(stats['LatN1_12']) and not np.isnan(stats['TDT_5']):
        hypno_s = hypno[stats['LatN1_12']:stats['TDT_5']]

        stats['SPT_16'] = hypno_s.size
        stats['WASO_17'] = hypno_s[hypno_s == 0].size
        stats['TST_18'] = stats['SPT_16'] - stats['WASO_17']
    else:
        stats['SPT_16'] = np.nan
        stats['WASO_17'] = np.nan
        stats['TST_18'] = np.nan

    # Convert to minutes
    for key, value in stats.items():
        stats[key] = value / (60. / time_window)

    # Add global informations
    stats['Filename_0'] = path.basename(file) if file is not None else ''
    stats['Sampling frequency_1'] = str(int(sfori)) + " Hz"
    stats['Down-sampling_2'] = str(int(sf)) + " Hz"
    stats['Units_3'] = 'minutes'
    stats['Duration (TIB)_4'] = np.round(N / (sfori * 60.))

    stats['SE (%)_19'] = np.round(stats['TST_18'] / stats['TDT_5'] * 100., 2)

    # Percentages of TDT
    # stats['%Art_18'] = stats['Art_4'] / stats['TDT_3'] * 100.
    # stats['%W_19'] = stats['W_5'] / stats['TDT_3'] * 100.
    # stats['%N1_20'] = stats['N1_6'] / stats['TDT_3'] * 100.
    # stats['%N2_21'] = stats['N2_7'] / stats['TDT_3'] * 100.
    # stats['%N3_22'] = stats['N3_8'] / stats['TDT_3'] * 100.
    # stats['%REM_23'] = stats['REM_9'] / stats['TDT_3'] * 100.

    return stats

def hypnoplot(file, hypno, sf):
    """Compute sleep stats from an hypnogram vector.

    Args:
        file: str
            Filename (with full path) to sleep dataset.

        hypno: np.ndarray
            Hypnogram vector

        sf: float, optional, (def: 100.)
            The sampling frequency of displayed elements (could be the
            down-sampling frequency)
    """
    # Downsample to get one value per second
    hypno = hypno[::sf]

    # Put REM between Wake and N1 sleep
    hypno[hypno >= 1] += 1
    hypno[hypno == 5] = 1
    idxREM  = np.where(hypno == 1)[0]
    valREM = np.zeros(hypno.size)
    valREM[:] = np.nan
    valREM[idxREM] = 1

    # Start plotting
    plt.figure(num=None, figsize=(10, 4), facecolor='w', edgecolor='k')

    if len(hypno) / 60 < 60:
        xticks = np.arange(0, len(hypno), 10 * 60)
        lw=2
    else:
        xticks = np.arange(0, len(hypno), 30 * 60)
        lw=1.25

    np.put(xticks, 0, 1)
    plt.xticks(xticks, (xticks / 60).astype(int))
    plt.xlim(1, len(hypno))
    plt.plot(hypno, 'k', ls='steps', linewidth=lw)

    # Plot REM epochs
    for i in np.arange(0.6, 1, 0.001):
        plt.plot(np.arange(len(hypno)), i * valREM, 'k', linewidth=0.2)

    # Y-Ticks and Labels
    ylabels = ['Art', 'Wake', 'REM', 'N1', 'N2', 'N3', '']
    plt.yticks([-1,0,1,2,3,4,5], ylabels)

    # X-Ticks and Labels
    plt.xlabel("Time [minutes]")
    plt.ylabel("Sleep Stage")

    # Grid
    plt.gca().yaxis.grid(True,linewidth=0.15)
    plt.gca().xaxis.grid(True, linewidth=0.1)

    # Invert Y axis and despine
    plt.gca().invert_yaxis()
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['top'].set_color('none')

    # Save as 600 dpi .png
    plt.tight_layout()
    plt.savefig(file, format='png', dpi=600)
