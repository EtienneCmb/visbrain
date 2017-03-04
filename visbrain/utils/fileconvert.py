"""Group functions for file managment.

This file contains a bundle of functions that can be used to load several
specific files including *.eeg, *.edf...
"""

import numpy as np
import os

__all__ = ['elan2array']


def elan2array(path, ds_freq=100):
    """Read Elan .eeg file into NumpPy

    Elan format specs: http://elan.lyon.inserm.fr/

    An Elan dataset is separated into 3 files :
    - .eeg          raw data file
    - .eeg.ent      hearder file

    Args:
        path: str
            Filename (with full path) to Elan .eeg file

    Kargs:
        ds_freq: int (def 100)
            Downsampling frequency

    Return:
        sf: int
            The sampling frequency.

        data: np.ndarray
            The data organised as well (n_channels, n_points)

        chan: list
            The list of channel's names.


    Example:
        >>> import os
        >>> # Define path where the file is located
        >>> pathfile = 'mypath/'
        >>> path = os.path.join(pathfile, 'myfile.eeg')
        >>> sf, data, chan, = elan2array(path)
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
                      shape=(nb_chan, nb_samples), order={'F'})

    # Downsample to 100 Hz
    ds_factor = np.int(sf / ds_freq)
    m_ds = m_raw[:, ::ds_factor]

    # Multiply by gain
    data = np.diag(Gain[chan_list]).dot(m_ds[chan_list, ])

    return float(sf), data.astype(np.float32), list(chan)


def edf2array(path):
    """Read European Data Format (EDF) file into NumPy

    Use phypno class for reading EDF files:
        http://phypno.readthedocs.io/api/phypno.ioeeg.edf.html

    Args:
        path: str
            Filename (with full path) to EDF file

    Return:
        sf: int
            The sampling frequency.

        data: np.ndarray
            The data organised as well (n_channels, n_points)

        chan: list
            The list of channel's names.


    Example:
        >>> import os
        >>> # Define path where the file is located
        >>> pathfile = 'mypath/'
        >>> path = os.path.join(pathfile, 'myfile.edf')
        >>> sf, data, chan, = edf2array(path)
    """

    assert os.path.isfile(path)

    from edf import Edf

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
    """Read BrainVision file

    Poor man's version of https://gist.github.com/breuderink/6266871

    Assumes that data are saved with the following parameters:
        - Data format: Binary
        - Orientation: Multiplexed
        - Format: int16


    Args:
        path: str
            Filename (with full path) to .eeg file

    Return:
        sf: int
            The sampling frequency.

        data: np.ndarray
            The data organised as well (n_channels, n_points)

        chan: list
            The list of channel's names.


    Example:
        >>> import os
        >>> # Define path where the file is located
        >>> pathfile = 'mypath/'
        >>> path = os.path.join(pathfile, 'myfile.eeg')
        >>> sf, data, chan, = brainvision2array(path)
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
    n_samples = int(re.findall('\d+', ent[11])[0])
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

        data = np.diag(resolution).dot(ints)

    return float(sf), data.astype(np.float32), list(chan)
