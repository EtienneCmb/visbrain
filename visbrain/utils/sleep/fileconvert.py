"""Group functions for file managment.

This file contains a bundle of functions that can be used to load several
specific files including *.eeg, *.edf...
"""

import numpy as np
import os

__all__ = ['load_sleepdataset', 'load_hypno', 'save_hypnoToElan',
           'save_hypnoTotxt']


def load_sleepdataset(path, downsample=100):
    """Load a sleep dataset (elan, edf, brainvision).

    Args:
        path: string
            Filename (with full path) to sleep dataset.

    Kargs:
        downsample: int (def 100)
            Downsampling frequency

    Return:
        sf: int
            The sampling frequency.

        data: np.ndarray
            The data organised as well (n_channels, n_points)

        chan: list
            The list of channel's names.

        resampling: bool
            A boolean value if data need a resampling after loading.
    """
    # Test if file exist :
    assert os.path.isfile(path)

    # Extract file extension :
    file, ext = os.path.splitext(path)

    # Switch between differents types :
    if ext == '.eeg':
        # ELAN :
        if os.path.isfile(path + '.ent'):
            # Apply an automatic downsampling to 100 Hz
            sf, data, chan = elan2array(path)
            return sf, data, chan

        # BRAINVISION :
        elif os.path.isfile(file + '.vhdr'):
            sf, data, chan = brainvision2array(path)
            return sf, data, chan

        # None :
        else:
            raise ValueError("No header file found in this directory. You "
                             "should have a *.ent (ELAN) or *.vhdr "
                             "(BRAINVISION)")

    # EDF :
    elif ext == '.edf':
        sf, data, chan = edf2array(path)
        return sf, data, chan

    # None :
    else:
        raise ValueError("*" + ext + " files are currently not supported.")


def load_hypno(path, ds_freq):
    """Load hypnogram file.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    Wake:   0
    N1:     1
    N2:     2
    N3:     3
    REM:    4
    Art:    -1  (optional)

    Args:
        path: string
            Filename (with full path) to hypnogram file

        ds_freq: int
            Down-sampling frequency

    Return:
        hypno: np.ndarray
            The hypnogram vector with same length as downsampled data.
    """
    # Test if file exist :
    assert os.path.isfile(path)

    # Extract file extension :
    file, ext = os.path.splitext(path)

    # Try loading file :
    try:
        # Switch between differents types :
        if ext == '.hyp':
            # ELAN :
            return elan_hyp(path, ds_freq)

        elif ext == '.txt' or ext == '.csv':
            return txt_hyp(path, ds_freq)

    except:
        return None


def elan_hyp(path, ds_freq):
    """Read Elan hypnogram (.hyp)

    Args:
        path: str
            Filename(with full path) to Elan .hyp file

        ds_freq: int
            Downsampling frequency

    Return:
        hypno: np.ndarray
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

    # Resample to get same number of points as in eeg file
    hypno = np.repeat(hypno, ds_freq)

    return hypno


def txt_hyp(path, ds_freq):
    """Read text files (.txt / .csv) hypnogram.

    Args:
        path: str
            Filename(with full path) to hypnogram(.txt)

        ds_freq: int
            Downsampling frequency

    Return:
        hypno: np.ndarray
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

    if np.issubdtype(hyp.dtype, np.integer) == False:
        hyp = np.char.decode(hyp)
        hypno = np.array([s for s in hyp if s.lstrip('-').isdigit()],
                         dtype=int)
    else:
        hypno = hyp.astype(int)

    hypno = swap_hyp_values(hypno, desc)

    # Resample to get same number of points as in eeg file
    hypno = np.repeat(hypno, ds_freq * desc['time'])

    return hypno


def swap_hyp_values(hypno, desc):
    """Swap values in hypnogram vector.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    Args:
        hypno: np.ndarray
            The hypnogram vector

        description: str
            Path to a .txt file containing labels and values of each sleep
            stage separated by a space

    Return:
    hypno_s: np.ndarray
        Hypnogram with swapped values

        e.g from the DREAM bank EDF database
        Stage   Orig. val    New val
        W       5           0
        N1      3           1
        N2      2           2
        N3      1           3
        REM     0           4
    """
    # assert os.path.isfile(desc)

    # labels = np.genfromtxt(desc, dtype=str, delimiter=" ", usecols=0)
    # values = np.genfromtxt(desc, dtype=int, delimiter=" ", usecols=1)
    # hyp = {label: row for label, row in zip(labels, values)}

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


def elan2array(path):
    """Read Elan eeg file into NumPy.

    Elan format specs: http: // elan.lyon.inserm.fr/
    An Elan dataset is separated into 3 files:
    - .eeg          raw data file
    - .eeg.ent      hearder file
    - .pos          events file

    Args:
        path: str
            Filename(with full path) to Elan .eeg file

    Return:
        sf: int
            The sampling frequency.

        data: np.ndarray
            The data organised as well(n_channels, n_points)

        chan: list
            The list of channel's names.

    Example:
        >> > import os
        >> >  # Define path where the file is located
        >> > pathfile = 'mypath/'
        >> > path = os.path.join(pathfile, 'myfile.eeg')
        >> > sf, data, chan, = elan2array(path)
    """
    header = path + '.ent'

    assert os.path.isfile(path)
    assert os.path.isfile(header)

    # Read .ent file
    ent = np.genfromtxt(header, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)

    ent = np.char.decode(ent)

    # eeg file version
    eeg_version = ent[0]

    if eeg_version == 'V2':
        nb_oct = 2
        formread = '>i2'
    elif eeg_version == 'V3':
        nb_oct = 4
        formread = '>i4'

    # Sampling rate
    sf = np.int(1 / float(ent[8]))

    # Channels
    nb_chan = np.int(ent[9])
    nb_chan = nb_chan

    # Last 2 channels do not contain data
    nb_chan_data = nb_chan - 2
    chan_list = np.arange(0, nb_chan_data)
    chan = ent[10:10 + nb_chan_data]

    # Gain
    Gain = np.zeros(nb_chan)
    offset1 = 9 + 3 * nb_chan
    offset2 = 9 + 4 * nb_chan
    offset3 = 9 + 5 * nb_chan
    offset4 = 9 + 6 * nb_chan

    for i in np.arange(1, nb_chan + 1):

        MinAn = float(ent[offset1 + i])
        MaxAn = float(ent[offset2 + i])
        MinNum = float(ent[offset3 + i])
        MaxNum = float(ent[offset4 + i])

        Gain[i - 1] = (MaxAn - MinAn) / (MaxNum - MinNum)

    # Load memmap
    nb_bytes = os.path.getsize(path)
    nb_samples = int(nb_bytes / (nb_oct * nb_chan))

    m_raw = np.memmap(path, dtype=formread, mode='r',
                      shape=(nb_chan, nb_samples), order={'F'}).copy()

    # Multiply by gain :
    data = m_raw[chan_list, ] * \
        Gain[chan_list][..., np.newaxis].astype(np.float32)

    return float(sf), data, list(chan)


def edf2array(path):
    """Read European Data Format (EDF) file into NumPy.

    Use phypno class for reading EDF files:
        http: // phypno.readthedocs.io / api / phypno.ioeeg.edf.html

    Args:
        path: str
            Filename(with full path) to EDF file

    Return:
        sf: int
            The sampling frequency.

        data: np.ndarray
            The data organised as well(n_channels, n_points)

        chan: list
            The list of channel's names.

    Example:
        >> > import os
        >> >  # Define path where the file is located
        >> > pathfile = 'mypath/'
        >> > path = os.path.join(pathfile, 'myfile.edf')
        >> > sf, data, chan, = edf2array(path)
    """
    assert os.path.isfile(path)

    from .edf import Edf

    edf = Edf(path)

    # Return header informations
    _, _, sf, chan, n_samples, _ = edf.return_hdr()

    # Keep only data channels (e.g excludes marker chan)
    freqs = np.unique(edf.hdr['n_samples_per_record'])
    sf = freqs.max()

    if len(freqs) != 1:
        bad_chans = np.where(edf.hdr['n_samples_per_record'] < sf)
        chan = np.delete(chan, bad_chans)

    # Load all samples of selected channels
    np.seterr(divide='ignore', invalid='ignore')
    data = edf.return_dat(chan, 0, n_samples)

    return float(sf), data.astype(np.float32), list(chan)


def brainvision2array(path):
    """Read BrainVision file.

    Poor man's version of https: // gist.github.com / breuderink / 6266871

    Assumes that data are saved with the following parameters:
        - Data format: Binary
        - Orientation: Multiplexed
        - Format: int16

    Args:
        path: str
            Filename(with full path) to .eeg file

    Return:
        sf: int
            The sampling frequency.

        data: np.ndarray
            The data organised as well(n_channels, n_points)

        chan: list
            The list of channel's names.

    Example:
        >> > import os
        >> >  # Define path where the file is located
        >> > pathfile = 'mypath/'
        >> > path = os.path.join(pathfile, 'myfile.eeg')
        >> > sf, data, chan, = brainvision2array(path)
    """
    import re

    assert os.path.splitext(path)[1] == '.eeg'

    header = os.path.splitext(path)[0] + '.vhdr'

    assert os.path.isfile(path)
    assert os.path.isfile(header)

    # Read header
    ent = np.genfromtxt(header, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)

    ent = np.char.decode(ent)

    # Channels info
    n_chan = int(re.findall('\d+', ent[10])[0])
    # n_samples = int(re.findall('\d+', ent[11])[0])
    sf = int(re.findall('\d+', ent[14])[0])

    # Extract channel labels and resolution
    start_label = np.array(np.where(np.char.find(ent, 'Ch1=') == 0)).min()

    chan = {}
    resolution = np.empty(shape=n_chan)

    for i, j in enumerate(range(start_label, start_label + n_chan)):
        chan[i] = re.split('\W+', ent[j])[1]
        resolution[i] = float(ent[j].split(",")[2])

    chan = np.array(list(chan.values())).flatten()

    # Check binary format
    assert "MULTIPLEXED" in ent[8]
    assert "BINARY" in ent[6]
    assert "INT_16" in ent[22]

    with open(path, 'rb') as f:
        raw = f.read()
        size = int(len(raw) / 2)
        ints = np.ndarray((n_chan, int(size / n_chan)),
                          dtype='<i2', order='F', buffer=raw)

        data = np.float32(np.diag(resolution)).dot(ints)

    return float(sf), data, list(chan)


def save_hypnoToElan(filename, hypno, sf):
        """Save hypnogram in Elan file format (*.hyp).

        Args:
            filename: str
                Filename (with full path) of the file to save

            hypno: np.ndarray
                Hypnogram array, same length as data

            sf: int
                Sampling frequency of the data (after downsampling)
        """
        hdr = np.array([['time_base 1.000000'],
                        ['sampling_period ' + str(round(1/sf, 8))],
                        ['epoch_nb ' + str(int(hypno.size / sf))],
                        ['epoch_list']]).flatten()

        # Check data format
        sf = int(sf)
        hypno = hypno.astype(int)
        # Save
        export = np.append(hdr, hypno[::sf].astype(str))
        np.savetxt(filename, export, fmt='%s')


def save_hypnoTotxt(filename, hypno, sf, window=1.):
        """Save hypnogram in txt file format (*.txt).

        Header is in file filename_description.txt

        Args:
            filename: str
                Filename (with full path) of the file to save

            hypno: np.ndarray
                Hypnogram array, same length as data

            sf: float
                Sampling frequency of the data (after downsampling)

        Kargs:
            window: float, optional, (def 1)
                Time window (second) of each point in the hypno
                Default is one value per second
                (e.g. window = 30 = 1 value per 30 second)
        """
        base = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        descript = os.path.join(dirname,
                                os.path.splitext(base)[0] + '_description.txt')

        # Save hypno
        ds_fac = int(sf * window)
        np.savetxt(filename, hypno[::ds_fac].astype(int), fmt='%s')

        # Save header file
        hdr = np.array([['time ' + str(window)], ['W 0'], ['N1 1'], ['N2 2'],
                        ['N3 3'], ['REM 4'], ['Art -1']]).flatten()
        np.savetxt(descript, hdr, fmt='%s')