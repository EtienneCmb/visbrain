"""Group of functions for physiological processing."""
from re import findall
import logging

import numpy as np
from itertools import product
from scipy.stats import zscore

from .sigproc import smoothing

__all__ = ('find_non_eeg', 'rereferencing', 'bipolarization', 'commonaverage',
           'tal2mni', 'mni2tal', 'generate_eeg')

logger = logging.getLogger('visbrain')


def find_non_eeg(channels, pattern=['eog', 'emg', 'ecg', 'abd', 'lfp']):
    """Find non-EEG channels.

    Parameters
    ----------
    channels : list
        List of channel names.
    pattern : list | ['eog', 'emg', 'ecg', 'abd', 'lfp']
        List of patterns for non-EEG channels.

    Returns
    -------
    noneeg : array_like
        NumPy vector of boolean values. True if any of the strings in `pattern`
        is found in the channel label string
    """
    # Set channels in lower case :
    channels = np.char.lower(np.asarray(channels))
    # Pre-allocation :
    noneeg = np.zeros((len(channels),), dtype=bool)
    # Search patterns :
    for k in pattern:
        # Add to non-eeg if we find the pattern anywhere in the channel string
        noneeg += np.char.find(channels, k) >= 0
    return noneeg


###############################################################################
###############################################################################
#                               RE-REFERENCING
###############################################################################
###############################################################################

def rereferencing(data, chans, reference, to_ignore=None):
    """Re-reference data.

    Parameters
    ----------
    data : array_like
        The array of data of shape (nchan, npts).
    chans : list
        List of channel names of length nchan.
    reference : int
        The index of the channel to consider as a reference.
    to_ignore : list | None
        List of channels to ignore in the re-referencing.

    Returns
    -------
    datar : array_like
        The re-referenced data.
    channelsr : list
        List of re-referenced channel names.
    consider : list
        List of boolean values of channels that have to be considered
        during the ploting processus.
    """
    # Get shapes :
    nchan, npts = data.shape
    # Get data to use as the reference :
    ref = data[[reference], :]
    name = chans[reference]
    # Build ignore vector :
    consider = np.ones((nchan,), dtype=bool)
    consider[reference] = False
    # Find if some channels have to be ignored :
    if to_ignore is None:
        sl = slice(nchan)
    elif isinstance(to_ignore, (tuple, list, np.ndarray)):
        to_ignore = np.asarray(to_ignore)
        sl = np.arange(nchan)[~to_ignore]
        consider[to_ignore] = False
    # Re-reference data :
    data[sl, :] -= ref
    # Build channel names :
    chan = [k + '-' + name if consider[num]
            else k for num, k in enumerate(chans)]

    return data, chan, consider


def bipolarization(data, chans, to_ignore=None):
    """Bipolarize data.

    Channel labels are cleaned and for each channel a "name" and "number" are
    extracted using the following steps:
        1- Remove spaces and remove everything after "-" or "." in channel name
        2- Set as channel "number" the last series of digits in the label
        3- Set as channel "name" everything in the cleaned label preceding the
            channel number
    For example the name and number of channel "EEG1,2-A1" are "EEG1," and "2".
    Bipolarization is done by substracting channels with the same name for
    successive numbers.

    Parameters
    ----------
    data : array_like
        The array of data of shape (nchan, npts).
    chans : list
        List of channel names of length nchan.
    to_ignore : list | None
        List of channels to ignore in the bipolarization.

    Returns
    -------
    datar : array_like
        The re-referenced data.
    channelsr : list
        List of re-referenced channel names.
    consider : list
        List of boolean values of channels that have to be considered
        during the ploting processus.
    """
    # Variables :
    nchan, npts = data.shape
    consider = np.ones((nchan,), dtype=bool)

    # Preprocess channel names by separating channel names / number:
    chnames, chnums = [], []
    for num, c in enumerate(chans):
        # Remove spaces and everything after "." and "-"
        c = c.split('.')[0]
        c = c.split('-')[0]
        c = c.strip().replace(' ', '')
        # Get only the name / number :
        if findall(r'\d+', c):
            # Last series of digits in label are the channel "number"
            number = findall(r'\d+', c)[-1]
            # Everything before the channel number is the channel "name"
            # (Everything after channel number disappears)
            name = number.join(c.split(number)[0:-1])
        else:
            number = ''
            name = c
        chnums.append(number)
        chnames.append(name)
        # Save the cleaned channel label
        chans[num] = name + number

    # Find if some channels have to be ignored :
    if to_ignore is None:
        sl = range(nchan)
    elif isinstance(to_ignore, (tuple, list, np.ndarray)):
        to_ignore = np.asarray(to_ignore)
        sl = np.arange(nchan)[~to_ignore]
        consider[to_ignore] = False

    # Bipolarize :
    for num in reversed(range(nchan)):
        # If there's a number :
        if chnums[num] and (num in sl):
            # Get the name of the channel to find :
            chan_to_find = chnames[num] + str(int(chnums[num]) - 1)
            # Search if exist in channel list :
            if chan_to_find in chans:
                # Get the index :
                ind = chans.index(chan_to_find)
                # Substract to data :
                data[num, :] -= data[ind, :]
                # Update channel name :
                chans[num] = chans[num] + '-' + chan_to_find
            else:
                consider[num] = False
        else:
            consider[num] = False

    return data, chans, consider


def commonaverage(data, chans, to_ignore=None):
    """Re-referencement using common average.

    Parameters
    ----------
    data : array_like
        The array of data of shape (nchan, npts).
    chans : list
        List of channel names of length nchan.
    to_ignore : list | None
        List of channels to ignore in the re-referencing.

    Returns
    -------
    datar : array_like
        The re-referenced data.
    channelsr : list
        List of re-referenced channel names.
    consider : list
        List of boolean values of channels that have to be considered
        during the ploting processus.
    """
    # Variables :
    nchan, npts = data.shape
    consider = np.ones((nchan,), dtype=bool)
    # Find if some channels have to be ignored :
    if to_ignore is not None:
        consider[to_ignore] = False
    # Get the mean across  EEG channels :
    eegmean = data[consider].mean(0, keepdims=True)
    # Remove the mean on EEG channels :
    data[consider, :] -= eegmean
    # Update channel name :
    for k in range(len(chans)):
        chans[k] = chans[k] + '-m' if consider[k] else chans[k]
    return data, chans, consider


###############################################################################
###############################################################################
#                               XYZ CONVERSION
###############################################################################
###############################################################################

def _spm_matrix(p):
    """Matrix transformation.

    Parameters
    ----------
    p : array_like
        Vector of floats for defining each tranformation. p must be a vector of
        length 9.

    Returns
    -------
    Pr : array_like
        The tranformed array.
    """
    q = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]
    p.extend(q[len(p):12])

    # Translation t :
    t = np.array([[1, 0, 0, p[0]],
                  [0, 1, 0, p[1]],
                  [0, 0, 1, p[2]],
                  [0, 0, 0, 1]])
    # Rotation 1 :
    r1 = np.array([[1, 0, 0, 0],
                   [0, np.cos(p[3]), np.sin(p[3]), 0],
                   [0, -np.sin(p[3]), np.cos(p[3]), 0],
                   [0, 0, 0, 1]])
    # Rotation 2 :
    r2 = np.array([[np.cos(p[4]), 0, np.sin(p[4]), 0],
                   [0, 1, 0, 0],
                   [-np.sin(p[4]), 0, np.cos(p[4]), 0],
                   [0, 0, 0, 1]])
    # Rotation 3 :
    r3 = np.array([[np.cos(p[5]), np.sin(p[5]), 0, 0],
                   [-np.sin(p[5]), np.cos(p[5]), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    # Translation z :
    z = np.array([[p[6], 0, 0, 0],
                  [0, p[7], 0, 0],
                  [0, 0, p[8], 0],
                  [0, 0, 0, 1]])
    # Translation s :
    s = np.array([[1, p[9], p[10], 0],
                  [0, 1, p[11], 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])
    return np.linalg.multi_dot([t, r1, r2, r3, z, s])


def tal2mni(xyz):
    """Transform Talairach coordinates into MNI.

    Parameters
    ----------
    xyz : array_like
        Array of Talairach coordinates of shape (n_sources, 3)

    Returns
    -------
    xyz_r : array_like
        Array of MNI coordinates of shape (n_sources, 3)
    """
    # Check xyz to be (n_sources, 3) :
    if (xyz.ndim != 2) or (xyz.shape[1] != 3):
        raise ValueError("The shape of xyz must be (N, 3).")
    n_sources = xyz.shape[0]

    # Transformation matrices, different zooms above/below AC :
    rotn = np.linalg.inv(_spm_matrix([0., 0., 0., .05]))
    upz = np.linalg.inv(_spm_matrix([0., 0., 0., 0., 0., 0., .99, .97, .92]))
    downz = np.linalg.inv(_spm_matrix([0., 0., 0., 0., 0., 0., .99, .97, .84]))

    # Apply rotation and translation :
    xyz = np.dot(rotn, np.c_[xyz, np.ones((n_sources, ))].T)
    tmp = np.array(xyz)[2, :] < 0.
    xyz[:, tmp] = np.dot(downz, xyz[:, tmp])
    xyz[:, ~tmp] = np.dot(upz, xyz[:, ~tmp])
    return np.array(xyz[0:3, :].T)


def mni2tal(xyz):
    """Transform MNI coordinates into Talairach.

    Parameters
    ----------
    xyz : array_like
        Array of MNI coordinates of shape (n_sources, 3)

    Returns
    -------
    xyz_r : array_like
        Array of Talairach coordinates of shape (n_sources, 3)
    """
    # Check xyz to be (n_sources, 3) :
    if (xyz.ndim != 2) or (xyz.shape[1] != 3):
        raise ValueError("The shape of xyz must be (N, 3).")
    n_sources = xyz.shape[0]

    # Transformation matrices, different zooms above/below AC :
    up_t = _spm_matrix([0., 0., 0., .05, 0., 0., .99, .97, .92])
    down_t = _spm_matrix([0., 0., 0., .05, 0., 0., .99, .97, .84])
    xyz = np.c_[xyz, np.ones((n_sources, ))].T

    tmp = np.array(xyz)[2, :] < 0.
    xyz[:, tmp] = np.dot(down_t, xyz[:, tmp])
    xyz[:, ~tmp] = np.dot(up_t, xyz[:, ~tmp])
    return np.array(xyz[0:3, :].T)


def generate_eeg(sf=512., n_pts=1000, n_channels=1, n_trials=1, n_sines=100,
                 f_min=.5, f_max=160., smooth=50, noise=10, random_state=0):
    """Generate random eeg signals.

    Parameters
    ----------
    sf : float | 512.
        The sampling frequency
    n_pts : int | 1000
        The number of time points.
    n_channels : int | 1
        Number of channels
    n_trials : int | 1
        Number of trials
    n_sines : int | 100
        Number of sines composing each epoch.
    f_min : float | .5
        Minimum frequency for sines.
    f_max : float | 160.
        Maximum frequency for sines.
    smooth : float | 50.
        The smoothing factor. Use larger smoothing to reduce high frequencies.
    noise : float | 10.
        Noise level.
    random_state : int | 0
        Fix the random state for the reproducibility.

    Returns
    -------
    data : array_like
        Dataset as a (n_channels, n_trials, n_pts) array.
    time : array_like
        A (n_pts,) vector containing time values.
    """
    _rnd = np.random.RandomState(random_state)
    n_pts += 100  # edge effect compensation
    signal = np.zeros((n_channels, n_trials, n_pts), dtype=float)
    time = np.arange(n_pts).reshape(-1, 1) / sf
    f_sines = np.linspace(f_min, f_max, num=n_sines, endpoint=True)
    phy = _rnd.uniform(0., 2. * np.pi, (n_pts, n_sines))
    sines = np.sin(2. * np.pi * f_sines.reshape(1, -1) * time + phy)
    amp_log = np.logspace(0, 1, n_sines, base=.1)

    for k, i in product(range(n_channels), range(n_trials)):
        amp = amp_log * _rnd.normal(0., 1., n_sines)
        sig = smoothing(np.dot(sines, amp), smooth, 'hanning')
        sig += _rnd.randn(*sig.shape) / (noise * sig.std())
        signal[k, i] = sig
    signal = zscore(signal, -1)
    signal = signal[..., 50:-50]
    time = time[50:-50]
    return np.squeeze(signal), time
