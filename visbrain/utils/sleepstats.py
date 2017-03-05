import numpy as np


def sleepstats(hypno, sf=100, time_window=30):
    """Compute sleep stats from an hypnogram vector

    Args:
        path: string
            Filename (with full path) to sleep dataset.

        sf: int (def 100)
            Sampling frequency of hypnogram vector

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

    # Resample to get one value per 30 seconds
    hypno = hypno[::sf * time_window]

    stats = {}

    stats['TIB'] = hypno.size
    stats['TDT'] = np.array(np.where(hypno != 0)).max()

    # Duration of each sleep stages
    stats['Art'] = hypno[hypno == -1].size
    stats['W'] = hypno[hypno == 0].size
    stats['N1'] = hypno[hypno == 1].size
    stats['N2'] = hypno[hypno == 2].size
    stats['N3'] = hypno[hypno == 3].size
    stats['REM'] = hypno[hypno == 4].size

    # Sleep stage latencies
    stats['LatN1'] = np.nan
    stats['LatN2'] = np.nan
    stats['LatN3'] = np.nan
    stats['LatREM'] = np.nan

    if 1 in hypno:
        stats['LatN1'] = np.array(np.where(hypno == 1)).min()
    if 2 in hypno:
        stats['LatN2'] = np.array(np.where(hypno == 2)).min()
    if 3 in hypno:
        stats['LatN3'] = np.array(np.where(hypno == 3)).min()
    if 4 in hypno:
        stats['LatREM'] = np.array(np.where(hypno == 4)).min()

    hypno_s = hypno[stats['LatN1']:stats['TDT']]

    stats['SPT'] = hypno_s.size
    stats['WASO'] = hypno_s[hypno_s == 0].size
    stats['TST'] = stats['SPT'] - stats['WASO']

    # Convert to minutes
    for key, value in stats.items():
        stats[key] = value / (60 / time_window)

    stats['SE'] = stats['TST'] / stats['TDT'] * 100

    # Percentages of TDT
    stats['%Art'] = stats['Art'] / stats['TDT'] * 100
    stats['%W'] = stats['W'] / stats['TDT'] * 100
    stats['%N1'] = stats['N1'] / stats['TDT'] * 100
    stats['%N2'] = stats['N2'] / stats['TDT'] * 100
    stats['%N3'] = stats['N3'] / stats['TDT'] * 100
    stats['%REM'] = stats['REM'] / stats['TDT'] * 100

    return stats
