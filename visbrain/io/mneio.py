"""Utility functions for MNE."""
import numpy as np
import datetime
from ..utils import get_dsf

__all__ = ['mne_switch']


def mne_switch(file, ext, downsample, *args, preload=True, **kwargs):
    """Read sleep datasets using mne.io.

    Parameters
    ----------
        file: string
            Filename.

        ext: string
            File extension.

        arg: tuple
            Further arguments.

    Kargs:
        kargs: dict, optional, (def: {})
            Further optional arguments.
    """
    from mne import io

    # Get full path :
    path = file + ext

    # Preload :
    if preload is False:
        preload = 'temp.dat'
    kwargs['preload'] = preload

    if ext.lower() in ['.edf', '.bdf']:  # EDF / BDF
        raw = io.read_raw_edf(path, *args, **kwargs)
    elif ext.lower() == ['.egi', '.mff']:  # EGI / MFF
        raw = io.read_raw_egi(path, *args, **kwargs)
    elif ext.lower() == '.cnt':  # CNT
        raw = io.read_raw_cnt(path, *args, **kwargs)
    elif ext.lower() == '.eeg':  # BrainVision
        raw = io.read_raw_brainvision(path, *args, **kwargs)

    sf = np.round(raw.info['sfreq'])
    dsf, downsample = get_dsf(downsample, sf)
    channels = raw.info['ch_names']
    data = raw._data
    n = data.shape[1]
    start_time = datetime.time(0, 0, 0)  #raw.info['meas_date']

    return sf, downsample, dsf, data[:, ::dsf], channels, n, start_time
