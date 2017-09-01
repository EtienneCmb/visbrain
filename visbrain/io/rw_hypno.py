"""write/Read hypnogram data.

- write_hypno_txt : as text file
- write_hypno_hyp : as hyp file
- read_hypno : read either *.hyp or *.txt hypnogram data
- load_hypno_hyp : load *.hyp hypnogram data
- load_hypno_txt : load *.txt hypnogram data
"""
import numpy as np
import os
from warnings import warn

__all__ = ['write_hypno_txt', 'write_hypno_hyp', 'read_hypno',
           'load_hypno_hyp', 'load_hypno_txt']


def _oversample_hypnogram(hypno, n):
    """Oversample hypnogram.

    Parameters
    ----------
    hypno : array_like
        Hypnogram data of shape (N,) with N < n.
    n : int
        The destination length.

    Returns
    -------
    hypno : array_like
        The hypnogram of shape (n,)
    """
    # Get the repetition number :
    rep_nb = int(np.round(n / len(hypno)))
    # Repeat hypnogram :
    hypno = np.repeat(hypno, rep_nb)
    npts = len(hypno)
    # Complete (if needed) :
    if len(hypno) != n:
        hypno = np.append(hypno, hypno[-1] * np.ones((npts - n,)))
    return hypno.astype(int)


def write_hypno_txt(filename, hypno, sf, sfori, n, window=1.):
    """Save hypnogram in txt file format (txt).

    Header is in file filename_description.txt

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : float
        Sampling frequency of the data (after downsampling)
    sfori : int
        Original sampling rate of the raw data
    n : int
        Original number of points in the raw data
    window : float | 1
        Time window (second) of each point in the hypno
        Default is one value per second
        (e.g. window = 30 = 1 value per 30 second)
    """
    base = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    descript = os.path.join(dirname, os.path.splitext(
        base)[0] + '_description.txt')

    # Save hypno
    step = int(hypno.shape / np.round(n / sfori))
    np.savetxt(filename, hypno[::step].astype(int), fmt='%s')

    # Save header file
    hdr = np.array([['time ' + str(window)], ['W 0'], ['N1 1'], ['N2 2'],
                    ['N3 3'], ['REM 4'], ['Art -1']]).flatten()
    np.savetxt(descript, hdr, fmt='%s')


def write_hypno_hyp(filename, hypno, sf, sfori, n):
    """Save hypnogram in Elan file format (hyp).

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : int
        Sampling frequency of the data (after downsampling)
    sfori : int
        Original sampling rate of the raw data
    n : int
        Original number of points in the raw data
    """
    # Check data format
    sf = int(sf)
    hypno = hypno.astype(int)
    hypno[hypno == 4] = 5
    step = int(hypno.shape / np.round(n / sfori))

    hdr = np.array([['time_base 1.000000'],
                    ['sampling_period ' + str(np.round(1 / sfori, 8))],
                    ['epoch_nb ' + str(int(n / sfori))],
                    ['epoch_list']]).flatten()

    # Save
    export = np.append(hdr, hypno[::step].astype(str))
    np.savetxt(filename, export, fmt='%s')


def read_hypno(path, npts):
    """Load hypnogram file.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    Wake:   0
    N1:     1
    N2:     2
    N3:     3
    REM:    4
    Art:    -1  (optional)

    Parameters
    ----------
    path : string
        Filename (with full path) to hypnogram file.
    npts : int
        Data length.

    Returns
    -------
    hypno : array_like
        The hypnogram vector with same length as downsampled data.
    """
    # Test if file exist :
    assert os.path.isfile(path)

    # Extract file extension :
    file, ext = os.path.splitext(path)

    # Try loading file :
    try:
        if ext in ['.hyp', '.txt', '.csv']:
            # ----------- ELAN -----------
            if ext == '.hyp':
                hypno = load_hypno_hyp(path, npts)

            # ----------- TXT / CSV -----------
            elif ext in ['.txt', '.csv']:
                hypno = load_hypno_txt(path, npts)

            # Complete hypnogram if needed :
            n = len(hypno)
            if n < npts:
                hypno = np.append(hypno, hypno[-1] * np.ones((npts - n,)))
            elif n > npts:
                raise ValueError("The length of the hypnogram \
                                 vector must be" + str(npts) +
                                 " (Currently : " + str(n) + ".")

            return hypno.astype(np.float32)

    except:
        warn("\nAn error ocurred while trying to load the hypnogram. An empty"
             " one will be used instead.")
        return None


def load_hypno_hyp(path, npts):
    """Read Elan hypnogram (hyp).

    Parameters
    ----------
    path : str
        Filename(with full path) to Elan .hyp file
    npts : int
        Data length.

    Returns
    -------
    hypno : array_like
        The hypnogram vector with same length as downsampled data.
    """
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)

    hyp = np.char.decode(hyp)

    # Sampling rate of original .eeg file
    # sf = 1 / float(hyp[1].split()[1])

    # Extract hypnogram values
    hypno = np.array(hyp[4:], dtype=np.int)

    # Replace values according to Iber et al 2007
    hypno[hypno == -2] = -1
    hypno[hypno == 4] = 3
    hypno[hypno == 5] = 4

    # Get the repetition number :
    rep = int(np.floor(npts / len(hypno)))

    # Resample to get same number of points as in eeg file
    hypno = np.repeat(hypno, rep)

    return hypno


def load_hypno_txt(path, npts):
    """Read text files (.txt / .csv) hypnogram.

    Parameters
    ----------
    path : str
        Filename(with full path) to hypnogram(.txt)
    npts : int
        Data length.

    Returns
    -------
    hypno : array_like
        The hypnogram vector with same length as downsampled data.
    """
    assert os.path.isfile(path)

    file, ext = os.path.splitext(path)

    header = file + '_description.txt'
    assert os.path.isfile(header)

    # Load header file
    labels = np.genfromtxt(header, dtype=str, delimiter=" ", usecols=0)
    values = np.genfromtxt(header, dtype=int, delimiter=" ", usecols=1)
    desc = {label: row for label, row in zip(labels, values)}

    # Load hypnogram file
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)

    if not np.issubdtype(hyp.dtype, np.integer):
        hyp = np.char.decode(hyp)
        hypno = np.array([s for s in hyp if s.lstrip('-').isdigit()],
                         dtype=int)
    else:
        hypno = hyp.astype(int)

    hypno = swap_hyp_values(hypno, desc)

    # Get the repetition number :
    rep = int(np.floor(npts / len(hypno)))

    # Resample to get same number of points as in eeg file
    hypno = np.repeat(hypno, rep)

    return hypno


def swap_hyp_values(hypno, desc):
    """Swap values in hypnogram vector.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    e.g from the DREAM bank EDF database
    Stage   Orig. val    New val
    W       5           0
    N1      3           1
    N2      2           2
    N3      1           3
    REM     0           4

    Parameters
    ----------
    hypno : array_like
        The hypnogram vector
    description : str
        Path to a .txt file containing labels and values of each sleep
        stage separated by a space

    Returns
    -------
    hypno_s : array_like
        Hypnogram with swapped values
    """
    # Swap values
    hypno_s = -1 * np.ones(shape=(hypno.shape), dtype=int)

    if 'Art' in desc:
        hypno_s[hypno == desc['Art']] = -1

    if 'Nde' in desc:
        hypno_s[hypno == desc['Nde']] = -1

    if 'Mt' in desc:
        hypno_s[hypno == desc['Mt']] = -1

    if 'W' in desc:
        hypno_s[hypno == desc['W']] = 0

    if 'N1' in desc:
        hypno_s[hypno == desc['N1']] = 1

    if 'N2' in desc:
        hypno_s[hypno == desc['N2']] = 2

    if 'N3' in desc:
        hypno_s[hypno == desc['N3']] = 3

    if 'N4' in desc:
        hypno_s[hypno == desc['N4']] = 3

    if 'REM' in desc:
        hypno_s[hypno == desc['REM']] = 4

    return hypno_s
