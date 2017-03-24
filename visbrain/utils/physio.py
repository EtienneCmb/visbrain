"""Group of functions for physiological processing."""
import numpy as np
from re import findall

__all__ = ['rereferencing', 'bipolarization']


def _chaninspect(strlst, tofind):
    """In a list, find "tofind" which can be a srting or integer."""
    # Check tofind parameter :
    if not isinstance(tofind, list):
        if isinstance(tofind, (int, str)):
            tofind = [tofind]
        else:
            tofind = list(tofind)
    # Find channels :
    idx = []
    for name in tofind:
        if isinstance(name, str):
            idx.append(strlst.index(name))
        elif isinstance(name, int):
            idx.append(name)

    return idx


def rereferencing(data, chans, reference, to_ignore=None):
    """Re-reference data.

    Args:
        data: np.ndarray
            The array of data of shape (nchan, npts).

        chans: list
            List of channel names of length nchan.

        reference: int
            The index of the channel to consider as a reference.

    Kargs:
        to_ignore: list, optional, (def: None)
            List of channels to ignore in the re-referencing.

    Returns:
        datar: np.ndarray
            The re-referenced data.

        channelsr: list
            List of re-referenced channel names.

        consider: list
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
        sl = np.setdiff1d(np.arange(nchan), to_ignore)
        consider[to_ignore] = False
    # Re-reference data :
    data[sl, :] -= ref
    # Build channel names :
    chan = [k+'-'+name if consider[num] else k for num, k in enumerate(chans)]

    return data, chan, consider


def bipolarization(data, channel, dim=0, xyz=None, sep='.', unbip=None,
                   rmchan=None, keepchan='all', rmspace=True, rmalone=True):
    """Bipolarize data.

    Args:
        data: array
            Data to bipolarize

        channel: list
            List of channels name

    Kwargs:
        dim: integer, optional, [def: 0]
            Specify where is the channel dimension of data

        xyz: array, optional, [def: None]
            Electrode coordinates. Must be a n_channel x 3

        sep: string, optional, [def: '.']
            Separator to simplify electrode names by removing undesired name
            after the sep. For example, if channel = ['h1.025', 'h2.578']
            and sep='.', the final name will be 'h2-h1'.

        unbip: list, optional, [def: None]
            Channel that don't need a bipolarization but to keep.
            This list can either be the index or the name of the channel.

        rmchan: list, optional, [def: None]
            Channel to remove. This list can either be the index or the
            name of the channel.

        keepchan: list, optional, [def: 'all']
            Channel to keep. This list can either be the index or the
            name of the channel.

        rmspace: bool, optional, [def: True]
            Remove undesired space in channel names.

        rmalone: bool, optional, [def: True]
            Remove electrodes that cannot be bipolarized.

    Returns:
        data_b: array
            Bipolarized data.

        channel_b: list
            List of the bipolrized channels name.

        xyz_b: array
            Array of the new xyz coordinates.

    Example :
        >>> x = 47
        >>> f = np.array(47, 54, 85)
    """
    # Check data size :
    if data.shape[dim] != len(channel):
        raise ValueError("Dimension {dim} of data must be "
                         "{val}".format(dim=dim, val=len(channel)))
    if dim is not 0:
        data = np.swapaxes(data, 0, dim)

    # Check if the user is not trying to keep and remove the same elec :
    if (rmchan is not None) and (keepchan is not None):
        # Check if there is no intersection :
        inter = list(set(rmchan).intersection(set(keepchan)))
        if inter:
            raise ValueError("You are trying to keep and to remove the "
                             "same channel {inter}. You have to "
                             "choose !".format(inter=inter))

    # Remove channels :
    if rmchan is not None:
        # Find channels :
        chan2rm = _chaninspect(channel, rmchan)
        # Remove in data :
        data = np.delete(data, chan2rm, axis=0)
        # Update chhanel names :
        channel = [i for num, i in enumerate(channel) if num not in chan2rm]

    # Channels to keep :
    if keepchan is 'all':
        pass
    else:
        # Find channels :
        chan2keep = _chaninspect(channel, keepchan)
        # Keep data and channel :
        data = data[chan2keep, ...]
        channel = [channel[i] for i in chan2keep]

    # Get list of channel that don't need bipolarization :
    if unbip is not None:
        unbipidx = _chaninspect(channel, unbip)
    else:
        unbipidx = []

    # Use a separator for the channel name :
    chanShort = [i.strip().replace(' ', '').split(sep)[0] for i in channel]
    if sep is not None:
        channel = chanShort

    # Get num list :
    numlst = [[] if findall(
        r'\d+', i) == [] else int(findall(r'\d+', i)[0]) for i in chanShort]

    # Find channel association :
    channel_b, idx_b = [], []
    for num, chan in enumerate(chanShort):
        # Get current letter and num :
        cnum = numlst[num]
        cletter = chan.split(str(cnum))[0]
        # If chan is consider and there is a number in the elec name :
        if (num not in unbipidx) and cnum:
            # Try to find elec-1 :
            try:
                # Search if num-1 exist :
                id_1 = chanShort.index(cletter+str(cnum-1))
                # Append new name :
                channel_b.append(channel[num]+'-'+channel[id_1])
                # Append idx to substract :
                idx_b.append([num, id_1])
            except:
                if (cnum != 1) and not rmalone:
                    channel_b.append(chan)
                    idx_b.append(num)
        else:
            if not rmalone:
                channel_b.append(chan)
                idx_b.append(num)

    # Bipolarized data and mean of xyz :
    data_b, xyz_b = [], []
    if idx_b:
        for idx in idx_b:
            # ::::::::::::::: DATA ::::::::::::::::
            # Bipolarized :
            if isinstance(idx, list):
                data_b.append(data[idx[0], ...] - data[idx[1], ...])
            # Keep intact :
            elif isinstance(idx, int):
                data_b.append(data[idx, ...])

            # ::::::::::::::: XYZ ::::::::::::::::
            if xyz is not None:
                # Bipolarized :
                if isinstance(idx, list):
                    xyz_b.append((xyz[idx[0], :]+xyz[idx[1], :])/2)
                # Keep intact :
                elif isinstance(idx, int):
                    xyz_b.append(xyz[idx, :])

    # Remove undesired space :
    if rmspace:
        channel_b = [i.strip().replace(' ', '') for i in channel_b]

    # Finally swapaxis if not 0 :
    if dim is not 0:
        data_b = np.swapaxes(np.array(data_b), 0, dim)
    else:
        data_b = np.array(data_b)

    return data_b, channel_b, np.array(xyz_b)
