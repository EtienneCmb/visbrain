"""write hypnogram data.

- write_hypno_txt : as text file
- write_hypno_hyp : as hyp file
"""
import numpy as np
import os

__all__ = ['write_hypno_txt', 'write_hypno_hyp']


def write_hypno_txt(filename, hypno, sf, sfori, N, window=1.):
    """Save hypnogram in txt file format (*.txt).

    Header is in file filename_description.txt

    Args:
        filename: str
            Filename (with full path) of the file to save

        hypno: np.ndarray
            Hypnogram array, same length as data

        sf: float
            Sampling frequency of the data (after downsampling)

        sfori: int
            Original sampling rate of the raw data

        N: int
            Original number of points in the raw data

    Kargs:
        window: float, optional, (def 1)
            Time window (second) of each point in the hypno
            Default is one value per second
            (e.g. window = 30 = 1 value per 30 second)
    """
    base = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    descript = os.path.join(dirname, os.path.splitext(
                                              base)[0] + '_description.txt')

    # Save hypno
    step = int(hypno.shape / np.round(N / sfori))
    np.savetxt(filename, hypno[::step].astype(int), fmt='%s')

    # Save header file
    hdr = np.array([['time ' + str(window)], ['W 0'], ['N1 1'], ['N2 2'],
                    ['N3 3'], ['REM 4'], ['Art -1']]).flatten()
    np.savetxt(descript, hdr, fmt='%s')


def write_hypno_hyp(filename, hypno, sf, sfori, N):
    """Save hypnogram in Elan file format (*.hyp).

    Args:
        filename: str
            Filename (with full path) of the file to save

        hypno: np.ndarray
            Hypnogram array, same length as data

        sf: int
            Sampling frequency of the data (after downsampling)

        sfori: int
            Original sampling rate of the raw data

        N: int
            Original number of points in the raw data
    """
    # Check data format
    sf = int(sf)
    hypno = hypno.astype(int)
    hypno[hypno == 4] = 5
    step = int(hypno.shape / np.round(N / sfori))

    hdr = np.array([['time_base 1.000000'],
                    ['sampling_period ' + str(np.round(1/sfori, 8))],
                    ['epoch_nb ' + str(int(N / sfori))],
                    ['epoch_list']]).flatten()

    # Save
    export = np.append(hdr, hypno[::step].astype(str))
    np.savetxt(filename, export, fmt='%s')
