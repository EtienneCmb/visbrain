"""Get informations about hypnogram."""

import numpy as np


__all__ = ['sleepstats']


def sleepstats(hypno, sf=100, time_window=30.):
    """Compute sleep stats from an hypnogram vector.

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
    # Get a step (integer) and resample to get one value per 30 seconds :
    step = int(round(sf * time_window))
    hypno = hypno[::step]

    stats = {}
    tov = np.nan

    stats['TIB_0'] = hypno.size
    stats['TDT_1'] = np.where(hypno != 0)[0].max() if np.nonzero(
                                                        hypno)[0].size else tov

    # Duration of each sleep stages
    stats['Art_2'] = hypno[hypno == -1].size
    stats['W_3'] = hypno[hypno == 0].size
    stats['N1_4'] = hypno[hypno == 1].size
    stats['N2_5'] = hypno[hypno == 2].size
    stats['N3_6'] = hypno[hypno == 3].size
    stats['REM_7'] = hypno[hypno == 4].size

    # Sleep stage latencies
    stats['LatN1_8'] = np.where(hypno == 1)[0].min() if 1 in hypno else tov
    stats['LatN2_9'] = np.where(hypno == 2)[0].min() if 2 in hypno else tov
    stats['LatN3_10'] = np.where(hypno == 3)[0].min() if 3 in hypno else tov
    stats['LatREM_11'] = np.where(hypno == 4)[0].min() if 4 in hypno else tov

    if not np.isnan(stats['LatN1_8']) and not np.isnan(stats['TDT_1']):
        hypno_s = hypno[stats['LatN1_8']:stats['TDT_1']]

        stats['SPT_12'] = hypno_s.size
        stats['WASO_13'] = hypno_s[hypno_s == 0].size
        stats['TST_14'] = stats['SPT_12'] - stats['WASO_13']
    else:
        stats['SPT_12'] = np.nan
        stats['WASO_13'] = np.nan
        stats['TST_14'] = np.nan

    # Convert to minutes
    for key, value in stats.items():
        stats[key] = value / (60. / time_window)

    stats['SE_15'] = stats['TST_14'] / stats['TDT_1'] * 100.

    # Percentages of TDT
    stats['%Art_16'] = stats['Art_2'] / stats['TDT_1'] * 100.
    stats['%W_17'] = stats['W_3'] / stats['TDT_1'] * 100.
    stats['%N1_18'] = stats['N1_4'] / stats['TDT_1'] * 100.
    stats['%N2_19'] = stats['N2_5'] / stats['TDT_1'] * 100.
    stats['%N3_20'] = stats['N3_6'] / stats['TDT_1'] * 100.
    stats['%REM_21'] = stats['REM_7'] / stats['TDT_1'] * 100.

    return stats
