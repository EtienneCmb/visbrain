"""Group of functions for physiological processing."""

import numpy as np
from re import findall
import os
import sys

__all__ = ('find_non_eeg', 'rereferencing', 'bipolarization', 'commonaverage',
           'tal2mni', 'mni2tal', 'find_roi')


def find_non_eeg(channels, pattern=['eog', 'emg', 'ecg', 'abd']):
    """Find non-EEG channels.

    Parameters
    ----------
    channels : list
        List of channel names.

    pattern : list | ['eog', 'emg', 'ecg', 'abd']
        List of patterns for non-EEG channels.

    Returns
    -------
    iseeg : array_like
        NumPy vector of boolean values.
    """
    # Set channels in lower case :
    channels = np.char.lower(np.asarray(channels))
    # Pre-allocation :
    iseeg = np.zeros((len(channels),), dtype=bool)
    # Search patterns :
    for k in pattern:
        iseeg += np.invert(np.char.find(channels, k).astype(bool))
    return iseeg


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
    else:
        sl = np.arange(nchan)[~to_ignore]
        consider[to_ignore] = False
    # Re-reference data :
    data[sl, :] -= ref
    # Build channel names :
    chan = [k + '-' + name if consider[num]
            else k for num, k in enumerate(chans)]

    return data, chan, consider


def bipolarization(data, chans, to_ignore=None, sep='.'):
    """Bipolarize data.

    Parameters
    ----------
    data : array_like
        The array of data of shape (nchan, npts).

    chans : list
        List of channel names of length nchan.

    to_ignore : list | None
        List of channels to ignore in the re-referencing.

    sep : string | '.'
        Separator to simplify electrode names by removing undesired name
        after the sep. For example, if channel = ['h1.025', 'h2.578']
        and sep='.', the final name will be 'h2-h1'.

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
    for num, k in enumerate(chans):
        # Remove spaces and separation :
        chans[num] = k.strip().replace(' ', '').split(sep)[0]
        # Get only the name / number :
        if findall(r'\d+', k):
            number = findall(r'\d+', k)[0]
            chnums.append(number)
            chnames.append(k.split(number)[0])
        else:
            chnums.append('')
            chnames.append(k)

    # Find if some channels have to be ignored :
    if to_ignore is None:
        sl = range(nchan)
    else:
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
    t = np.matrix([[1, 0, 0, p[0]],
                   [0, 1, 0, p[1]],
                   [0, 0, 1, p[2]],
                   [0, 0, 0, 1]])
    # Rotation 1 :
    r1 = np.matrix([[1, 0, 0, 0],
                    [0, np.cos(p[3]), np.sin(p[3]), 0],
                    [0, -np.sin(p[3]), np.cos(p[3]), 0],
                    [0, 0, 0, 1]])
    # Rotation 2 :
    r2 = np.matrix([[np.cos(p[4]), 0, np.sin(p[4]), 0],
                    [0, 1, 0, 0],
                    [-np.sin([p[4]]), 0, np.cos(p[4]), 0],
                    [0, 0, 0, 1]])
    # Rotation 3 :
    r3 = np.matrix([[np.cos(p[5]), np.sin(p[5]), 0, 0],
                    [-np.sin(p[5]), np.cos(p[5]), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])
    # Translation z :
    z = np.matrix([[p[6], 0, 0, 0],
                   [0, p[7], 0, 0],
                   [0, 0, p[8], 0],
                   [0, 0, 0, 1]])
    # Translation s :
    s = np.matrix([[1, p[9], p[10], 0],
                   [0, 1, p[11], 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    return t * r1 * r2 * r3 * z * s


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
    xyz = rotn * np.c_[xyz, np.ones((n_sources, ))].T
    tmp = np.array(xyz)[2, :] < 0.
    xyz[:, tmp] = downz * xyz[:, tmp]
    xyz[:, ~tmp] = upz * xyz[:, ~tmp]
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
    xyz[:, tmp] = down_t * xyz[:, tmp]
    xyz[:, ~tmp] = up_t * xyz[:, ~tmp]
    return np.array(xyz[0:3, :].T)

def find_roi(xyz, r=5., nearest=True):
    # Check xyz to be (n_sources, 3) :
    if (xyz.ndim != 2) or (xyz.shape[1] != 3):
        raise ValueError("The shape of xyz must be (N, 3).")
    # xyz = tal2mni(xyz)
    n_sources = xyz.shape[0]
    xyz = np.c_[xyz, np.ones((n_sources,))].T

    # Load ROI atlas :
    pathfile = sys.modules[__name__].__file__.split('utils')[0]
    path_to_template = os.path.join(*('brain', 'base', 'templates', 'roi.npz'))
    path = os.path.join(pathfile, path_to_template)
    atlas = np.load(path)

    # Get volumes :
    aal_label, aal_idx = atlas['aal_label'], atlas['aal_idx']
    vol, hdr, brod_idx = atlas['vol'], atlas['hdr'], atlas['brod_idx']
    sh = vol.shape

    # Build AAL label for left and right :
    left = np.full((len(aal_label),), ' (L)')
    right = np.full((len(aal_label),), ' (R)')
    aal_l = np.core.defchararray.add(aal_label, left)
    aal_r = np.core.defchararray.add(aal_label, right)
    aal_label = np.c_[aal_l, aal_r].flatten()
    # print(aal_label.shape, aal_idx.shape, 'AAl : ', aal_idx.min(), aal_idx.max(), 'VOL : ', vol.min(), vol.max())

    # Loop over source :
    info = np.full((n_sources, 5), '-', dtype=object)
    for k in range(n_sources):
        info[k, 2::] = xyz[0:-1, k].ravel()
        # Apply HDR transformation :
        pos = np.linalg.lstsq(hdr, xyz[:, [k]])[0].reshape(-1)
        sub = list(np.around(pos).astype(int))

        if (sub[0] <= sh[0]) and (sub[1] <= sh[1]) and (sub[2] <= sh[2]):

            if nearest:
                pass
            else:
                # Find the Brodmann area :
                brod = brod_idx[sub[0], sub[1], sub[2]]
                if brod:
                    info[k, 0] = 'Brodmann area ' + str(brod)
                # Find the AAL :
                aal = vol[sub[0], sub[1], sub[2]]
                if aal:
                    info[k, 1] = aal_label[aal - 1]
        else:
            pass
            # print('BAD')

    # print(info)
