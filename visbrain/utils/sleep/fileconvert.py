"""Group functions for file managment.

This file contains a bundle of functions that can be used to load several
specific files including *.eeg, *.edf...
"""

import numpy as np
import os
import datetime

from ..others import check_downsampling

__all__ = ['load_sleepdataset']


def load_sleepdataset(path, downsample=None):
    """Load a sleep dataset (elan, edf, brainvision).

    Parameters
    ----------
    path : string
        Filename (with full path) to sleep dataset.
    downsample : float (def 100.)
        Downsampling frequency

    Returns
    -------
    sf : int
        The sampling frequency.
    data : array_like
        The data organised as well (n_channels, n_points)
    chan : list
        The list of channel's names.
    N : int
        Number of samples in the original data
    start_time: array_like
        Starting time of the recording (hh:mm:ss)

    Example
    -------
    >>> import os
    >>>  # Define path where the file is located
    >>> pathfile = 'mypath/'
    >>> path = os.path.join(pathfile, 'myfile.*')
    >>> sf, data, chan, N, start_time = load_sleepdataset(path, 100.)
    """
    # Test if file exist :
    assert os.path.isfile(path)

    # Extract file extension :
    file, ext = os.path.splitext(path)
    ext = ext.lower()

    # Switch between differents types :
    if ext == '.eeg':
        # ELAN :
        if os.path.isfile(path + '.ent'):
            # Apply an automatic downsampling to 100 Hz
            return elan2array(path, downsample)

        # BRAINVISION :
        elif os.path.isfile(file + '.vhdr'):
            return brainvision2array(path, downsample)

        # None :
        else:
            raise ValueError("No header file found in this directory. You "
                             "should have a *.ent (ELAN) or *.vhdr "
                             "(BRAINVISION)")

    # EDF :
    elif ext == '.edf':
        return edf2array(path, downsample)

    elif ext == '.trc':
        return micromed2array(path, downsample)

    # None :
    else:
        raise ValueError("*" + ext + " files are currently not supported.")


def elan2array(path, downsample=None):
    """Read Elan eeg file into NumPy.

    Elan format specs: http: // elan.lyon.inserm.fr/

    Parameters
    ----------
    path : str
        Filename(with full path) to Elan .eeg file
    downsample : float | None
        The downsampling frequency.

    Returns
    -------
    sf : int
        The sampling frequency.
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    N : int
        Number of samples in the original data
    start_time : array_like
        Starting time of the recording (hh:mm:ss)
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
    sf = 1. / float(ent[8])

    # Record starting time
    if ent[4] != "No time":
        rec_time = ent[4]
        hour, minutes, sec = ent[4].split(':')
        start_time = datetime.time(int(hour), int(minutes), int(sec))

        rec_date = ent[3]
        day, month, year = ent[3].split(':')
        start_date = datetime.date(int(year) + 1900, int(month), int(day))
    else:
        start_time = datetime.time(0, 0, 0)
        start_date = datetime.date(1900, 1, 1)

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

    # Get original signal length :
    N = m_raw.shape[1]

    # Get downsample factor :
    if downsample is not None:
        # Check down-sampling :
        downsample = check_downsampling(sf, downsample)
        ds = int(np.round(sf / downsample))
    else:
        ds = 1

    # Multiply by gain :
    data = m_raw[chan_list, ::ds] * \
        Gain[chan_list][..., np.newaxis].astype(np.float32)

    return sf, downsample, data, list(chan), N, start_time


def edf2array(path, downsample=None):
    """Read European Data Format (EDF) file into NumPy.

    Use phypno class for reading EDF files:
        http: // phypno.readthedocs.io / api / phypno.ioeeg.edf.html

    Parameters
    ----------
        path: str
            Filename(with full path) to EDF file
        downsample : float | None
            The downsampling frequency.

    Returns
    -------
    sf : int
        The sampling frequency.
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    N : int
        Number of points in the original data
    start_time: array_like
        Starting time of the recording (hh:mm:ss)
    """
    assert os.path.isfile(path)

    from .edf import Edf

    edf = Edf(path)

    # Return header informations
    _, start_time, sf, chan, n_samples, _ = edf.return_hdr()
    start_time = start_time.time()

    # Keep only data channels (e.g excludes marker chan)
    freqs = np.unique(edf.hdr['n_samples_per_record'])
    sf = freqs.max()

    if len(freqs) != 1:
        bad_chans = np.where(edf.hdr['n_samples_per_record'] < sf)
        chan = np.delete(chan, bad_chans)

    # Load all samples of selected channels
    np.seterr(divide='ignore', invalid='ignore')
    data = edf.return_dat(chan, 0, n_samples)

    # Get original signal length :
    N = data.shape[1]

    # Get downsample factor :
    if downsample is not None:
        # Check down-sampling :
        downsample = check_downsampling(sf, downsample)
        ds = int(np.round(sf / downsample))
    else:
        ds = 1

    return float(sf), downsample, data[:, ::ds], list(chan), N, start_time


def brainvision2array(path, downsample=None):
    """Read BrainVision file.

    Poor man's version of https: // gist.github.com / breuderink / 6266871

    Assumes that data are saved with the following parameters:
        - Data format: Binary
        - Orientation: Multiplexed
        - Format: int16

    Parameters
    ----------
    path : str
        Filename(with full path) to .eeg file
    downsample : float | None
        The downsampling frequency.

    Returns
    -------
    sf : float
        The sampling frequency.
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    N : int
        Number of points in the original data
    start_time : array_like
        Starting time of the recording (hh:mm:ss)

    Example
    -------
    >>> import os
    >>>  # Define path where the file is located
    >>> pathfile = 'mypath/'
    >>> path = os.path.join(pathfile, 'myfile.eeg')
    >>> sf, ds, data, chan, N, start_time = brainvision2array(path)
    """
    import re

    assert os.path.splitext(path)[1] == '.eeg'

    header = os.path.splitext(path)[0] + '.vhdr'
    marker = os.path.splitext(path)[0] + '.vmrk'

    assert os.path.isfile(path)
    assert os.path.isfile(header)

    # Read header
    ent = np.genfromtxt(header, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)

    ent = np.char.decode(ent, "utf-8")

    # Check header version
    h_vers = int(re.findall('\d+', ent[0])[0])

    for item in ent:
        if 'NumberOfChannels=' in item:
            n_chan = int(re.findall('\d+', item)[0])
        elif 'SamplingInterval=' in item:
            si = float(re.findall("[-+]?\d*\.\d+|\d+", item)[0])
            sf = 1 / (si * 0.000001)
        elif 'DataFormat' in item:
            data_format = item.split('=')[1]
        elif 'BinaryFormat' in item:
            binary_format = item.split('=')[1]
        elif 'DataOrientation' in item:
            data_orient = item.split('=')[1]

    # Check binary format
    assert "BINARY" in data_format
    assert "INT_16" in binary_format
    assert "MULTIPLEXED" in data_orient

    # Extract channel labels and resolution
    start_label = np.array(np.where(np.char.find(ent, 'Ch1=') == 0)).min()
    chan = {}
    resolution = np.empty(shape=n_chan)

    for i, j in enumerate(range(start_label, start_label + n_chan)):
        chan[i] = re.split('\W+', ent[j])[1]
        resolution[i] = float(ent[j].split(",")[2])

    chan = np.array(list(chan.values())).flatten()

    # Read marker file (if present) to extract recording time
    if os.path.isfile(marker):
        vmrk = np.genfromtxt(marker, delimiter='\n', usecols=[0],
                             dtype=None, skip_header=0)

        vmrk = np.char.decode(vmrk)
        for item in vmrk:
            if 'New Segment' in item:
                st = re.split('\W+', item)[-1]

        start_date = datetime.date(int(st[0:4]), int(st[4:6]), int(st[6:8]))
        start_time = datetime.time(int(st[8:10]), int(st[10:12]),
                                   int(st[12:14]))
    else:
        start_date = datetime.date(1900, 1, 1)
        start_time = datetime.time(0, 0, 0)

    with open(path, 'rb') as f:
        raw = f.read()
        size = int(len(raw) / 2)

        ints = np.ndarray((n_chan, int(size / n_chan)),
                          dtype='<i2', order='F', buffer=raw)

        data = np.float32(np.diag(resolution)).dot(ints)

    # Get original signal length :
    N = data.shape[1]

    # Get downsample factor :
    if downsample is not None:
        # Check down-sampling :
        downsample = check_downsampling(sf, downsample)
        ds = int(np.round(sf / downsample))
    else:
        ds = 1

    return sf, downsample, data[:, ::ds], list(chan), N, start_time


def micromed2array(path, downsample=None):
    """Read Micromed (*.trc) file version 4.

    Poor man's version of micromedio.py from Neo package
    (https://pythonhosted.org/neo/)

    Parameters
    ----------
    path : str
        Filename(with full path) to .trc file
    downsample : float | None
        The downsampling frequency.

    Returns
    -------
    sf : float
        The sampling frequency.
    downsample : float
        The downsampling frequency
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    N : int
        Number of samples in the original signal
    start_time: array_like
        Starting time of the recording (hh:mm:ss)
    """
    import struct

    def read_f(f, fmt):
        return struct.unpack(fmt, f.read(struct.calcsize(fmt)))

    with open(path, 'rb') as f:
        # Read header
        f.seek(175, 0)
        header_version, = read_f(f, 'b')
        assert header_version == 4

        f.seek(138, 0)
        data_start_offset, n_chan, _, sf, nbytes = read_f(f, 'IHHHH')

        f.seek(128, 0)
        day, month, year, hour, minute, sec = read_f(f, 'bbbbbb')
        start_date = datetime.date(year + 1900, month, day)
        start_time = datetime.time(hour, minute, sec)

        # Raw data
        f.seek(data_start_offset, 0)
        m_raw = np.fromstring(f.read(), dtype='u'+str(nbytes))
        m_raw = m_raw.reshape((int(m_raw.size/n_chan), n_chan)).transpose()

        # Read label / gain
        gain = []
        chan = []
        logical_ground = []
        data = np.empty(shape=m_raw.shape, dtype=np.float32)

        f.seek(176, 0)
        zone_names = ['ORDER', 'LABCOD']
        zones = {}
        for zname in zone_names:
            zname2, pos, length = read_f(f, '8sII')
            zones[zname] = zname2, pos, length

        zname2, pos, length = zones['ORDER']
        f.seek(pos, 0)
        code = np.fromfile(f, dtype='u2', count=n_chan)

        for c in range(n_chan):
            zname2, pos, length = zones['LABCOD']
            f.seek(pos + code[c] * 128 + 2, 0)

            chan = np.append(chan, f.read(6).decode('utf-8').strip())
            ground = f.read(6).decode('utf-8').strip()
            logical_min, logical_max, logic_ground_chan, physical_min, \
                physical_max = read_f(f, 'iiiii')

            logical_ground = np.append(logical_ground, logic_ground_chan)

            gain = np.append(gain, float(physical_max - physical_min) /
                             float(logical_max-logical_min+1))

    # Multiply by gain
    m_raw = m_raw - logical_ground[:, np.newaxis]
    data = m_raw * gain[:, np.newaxis].astype(np.float32)

    # Get original signal length :
    N = data.shape[1]

    # Get downsample factor :
    if downsample is not None:
        # Check down-sampling :
        downsample = check_downsampling(sf, downsample)
        ds = int(np.round(sf / downsample))
    else:
        ds = 1

    return sf, downsample, data[:, ::ds], list(chan), N, start_time
