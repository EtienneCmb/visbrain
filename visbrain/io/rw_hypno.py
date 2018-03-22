"""write/Read hypnogram data.

Write hypnogram data
--------------------
-> write_hypno
    -> Export either using time code
        -> .txt, .csv, .xlsx
    -> Export using one sample per second
        -> .txt, .hyp

Read hypnogram data
-------------------
-> read_hypno
    -> detect_hypno_version
        -> Sample :
            -> .txt, .csv, .xlsx
        -> Tieme :
            -> .txt, .hyp
"""
import os
import logging
import numpy as np

from ..utils import vispy_array, transient
from ..io import is_pandas_installed, is_xlrd_installed

__all__ = ('oversample_hypno', 'write_hypno', 'read_hypno')

logger = logging.getLogger('visbrain')


###############################################################################
###############################################################################
#                              HYPNO CONVERSION
###############################################################################
###############################################################################

def hypno_time_to_sample(df, npts):
    """Convert the hypnogram from a defined timings to a number of samples.

    Parameters
    ----------
    df : pandas.DataFrame
        The data frame that contains timing.
    npts : int, array_like
        Number of time points in the final hypnogram. Alternatively, if npts is
        an array it will be interprated as the time vector.

    Returns
    -------
    hypno : array_like
        Hypnogram data of shape (npts,).
    time : array_like
        Time vector of shape (npts,).
    sf_hyp : float
        Sampling frequency of the hypnogram.
    """
    # Drop lines that contains * :
    drop_rows = np.char.find(np.array(df['Stage']).astype(str), '*')
    df = df.iloc[drop_rows.astype(bool)]
    df.is_copy = False  # avoid pandas warning
    # Replace text by numerical values :
    to_replace = ['Wake', 'N1', 'N2', 'N3', 'REM', 'Art']
    values = [0, 1, 2, 3, 4, -1]
    df.replace(to_replace, values, inplace=True)
    # Get stages and time index :
    stages = np.array(df['Stage']).astype(str)
    time_idx = np.array(df['Time']).astype(float)
    # Compute time vector and sampling frequency :
    if isinstance(npts, np.ndarray):
        time = npts.copy()
    elif isinstance(npts, int):
        time = np.arange(npts) * time_idx[-1] / (npts - 1)
    sf_hyp = 1. / (time[1] - time[0])
    # Find closest time index :
    index = np.abs(time.reshape(-1, 1) - time_idx.reshape(1, -1))
    index = np.r_[0, index.argmin(0) + 1]
    # Fill the hypnogram :
    hypno = np.zeros((len(time),), dtype=int)
    for k in range(len(index) - 1):
        hypno[index[k]:index[k + 1]] = stages[k]
    return hypno, time, sf_hyp


def hypno_sample_to_time(hypno, time):
    """Convert the hypnogram from a number of samples to a defined timings.

    Parameters
    ----------
    hypno : array_like
        Hypnogram data.
    time : array_like
        The time vector.

    Returns
    -------
    df : pandas.DataFrame
        The data frame that contains all of the transient timings.
    """
    # Test if panda is installed :
    is_pandas_installed(True)
    import pandas as pd
    # Transient detection :
    _, tr, stages = transient(hypno, time)
    # Save the hypnogram :
    items = np.array(['Wake', 'N1', 'N2', 'N3', 'REM', 'Art'])
    return pd.DataFrame({'Stage': items[stages], 'Time': tr[:, 1]})


def oversample_hypno(hypno, n):
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
    rep_nb = float(np.floor(n / len(hypno)))

    # Repeat hypnogram :
    hypno = np.repeat(hypno, rep_nb)
    npts = len(hypno)

    # Check size
    if npts < n:
        hypno = np.append(hypno, hypno[-1] * np.ones((n - npts)))
    elif n > npts:
        raise ValueError("The length of the hypnogram  vector must "
                         "be " + str(n) + " (Currently : " + str(npts) + ".")

    return hypno.astype(int)


###############################################################################
###############################################################################
#                               WRITE HYPNO
###############################################################################
###############################################################################

def write_hypno(filename, hypno, version='time', sf=100., npts=1, window=1.,
                time=None, info=None):
    """Save hypnogram data.

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : float | 100.
        Original sampling rate of the raw data
    npts : int | 1
        Original number of points in the raw data
    window : float | 1
        Time window (second) of each point in the hypno
        Default is one value per second
        (e.g. window = 30 = 1 value per 30 second)
    time : array_like | None
        The time vector.
    info : dict | None
        Additional informations to add to the file (prepend with *).
    """
    # Checking :
    assert isinstance(filename, str)
    assert isinstance(hypno, np.ndarray)
    assert version in ['time', 'sample']
    # Extract file extension :
    _, ext = os.path.splitext(filename)
    # Switch between time and sample version :
    if version is 'sample':  # v1 = sample
        # Take a down-sample version of the hypno :
        step = int(len(hypno) / np.round(npts / sf))
        hypno = hypno[::step].astype(int)
        # Export :
        if ext == '.txt':
            _write_hypno_txt_sample(filename, hypno, window=window)
        elif ext == '.hyp':
            _write_hypno_hyp_sample(filename, hypno, sf=sf, npts=npts)
    elif version is 'time':  # v2 = time
        # Get the DataFrame :
        df = hypno_sample_to_time(hypno, time)
        if isinstance(info, dict):
            is_pandas_installed(True)
            import pandas as pd
            info = {'*' + k: i for k, i in info.items()}
            df_info = pd.DataFrame({'Stage': list(info.keys()),
                                    'Time': list(info.values())})
            df = df_info.append(df)
        if ext in ['.txt', '.csv']:
            df.to_csv(filename, header=None, index=None, sep=' ', mode='a')
        elif ext == '.xlsx':
            is_pandas_installed(True)
            is_xlrd_installed(True)
            import pandas as pd
            writer = pd.ExcelWriter(filename)
            df.to_excel(writer, sheet_name='Data', index=False, header=False)
            writer.save()
    logger.info("Hypnogram saved (%s)" % filename)


def _write_hypno_txt_sample(filename, hypno, window=1.):
    """Save hypnogram in txt file format (txt).

    Header is in file filename_description.txt

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
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
    np.savetxt(filename, hypno, fmt='%s')

    # Save header file
    hdr = np.array([['time ' + str(window)], ['W 0'], ['N1 1'], ['N2 2'],
                    ['N3 3'], ['REM 4'], ['Art -1']]).flatten()
    np.savetxt(descript, hdr, fmt='%s')


def _write_hypno_hyp_sample(filename, hypno, sf=100., npts=1):
    """Save hypnogram in Elan file format (hyp).

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : float | 100.
        Original sampling rate of the raw data
    npts : int | 1
        Original number of points in the raw data
    """
    hypno[hypno == 4] = 5

    hdr = np.array([['time_base 1.000000'],
                    ['sampling_period ' + str(np.round(1 / sf, 8))],
                    ['epoch_nb ' + str(int(npts / sf))],
                    ['epoch_list']]).flatten()

    # Save
    export = np.append(hdr, hypno.astype(str))
    np.savetxt(filename, export, fmt='%s')


###############################################################################
###############################################################################
#                                 READ HYPNO
###############################################################################
###############################################################################


def read_hypno(filename, time=None):
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
    filename : string
        Filename (with full path) to hypnogram file.
    time : array_like | None
        The time vector (used to interpolate Excel files).

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp: float
        The hypnogram original sampling frequency (Hz)
    """
    # Test if file exist :
    assert os.path.isfile(filename)

    # Extract file extension :
    file, ext = os.path.splitext(filename)

    # Load the hypnogram :
    if ext == '.hyp':  # v1 = ELAN
        hypno, sf_hyp = _read_hypno_hyp_sample(filename)
    elif ext in ['.txt', '.csv']:  # [v1, v2] = TXT / CSV
        header = os.path.splitext(filename)[0] + '_description.txt'
        if os.path.isfile(header):  # if there's a header -> v1
            hypno, sf_hyp = _read_hypno_txt_sample(filename)
        else:  # v2
            import pandas as pd
            df = pd.read_csv(filename, sep=' ', header=None,
                             names=['Stage', 'Time'])
            hypno, _, sf_hyp = hypno_time_to_sample(df, len(time))
    elif ext == '.xlsx':  # v2 = Excel
        import pandas as pd
        df = pd.read_excel(filename, header=None, names=['Stage', 'Time'])
        hypno, _, sf_hyp = hypno_time_to_sample(df, len(time))

    logger.info("Hypnogram successfully loaded (%s)" % filename)

    return vispy_array(hypno), sf_hyp


def _read_hypno_hyp_sample(path):
    """Read Elan hypnogram (hyp).

    Parameters
    ----------
    path : str
        Filename(with full path) to Elan .hyp file

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp : float
        The hypnogram original sampling frequency (Hz)
    """
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0, encoding='utf-8')

    # Get sampling frequency of hypnogram
    sf_hyp = 1 / float(hyp[0].split()[1])

    # Extract hypnogram values
    hypno = np.array(hyp[4:], dtype=np.int)

    # Replace values according to Iber et al 2007
    hypno[hypno == -2] = -1
    hypno[hypno == 4] = 3
    hypno[hypno == 5] = 4

    return hypno, sf_hyp


def _read_hypno_txt_sample(path):
    """Read text files (.txt / .csv) hypnogram.

    Parameters
    ----------
    path : str
        Filename(with full path) to hypnogram (.txt)

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp : float
        The hypnogram original sampling frequency (Hz)
    """
    assert os.path.isfile(path)

    file, ext = os.path.splitext(path)

    header = file + '_description.txt'
    assert os.path.isfile(header)

    # Load header file
    labels = np.genfromtxt(header, dtype=str, delimiter=" ", usecols=0,
                           encoding='utf-8')
    values = np.genfromtxt(header, dtype=float, delimiter=" ", usecols=1,
                           encoding='utf-8')
    desc = {label: row for label, row in zip(labels, values)}

    # Get sampling frequency of hypnogram
    sf_hyp = 1. / float(desc['time'])

    # Load hypnogram file
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0, encoding='utf-8')

    if not np.issubdtype(hyp.dtype, np.integer):
        hypno = np.array([s for s in hyp if s.lstrip('-').isdigit()],
                         dtype=int)
    else:
        hypno = hyp.astype(int)

    hypno = swap_hyp_values(hypno, desc)

    return hypno, sf_hyp


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
