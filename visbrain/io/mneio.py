"""Utility functions for MNE."""
import datetime
import numpy as np
from ..utils import get_dsf

__all__ = ['mne_switch']


def mne_switch(file, ext, downsample, preload=True, **kwargs):
    """Read sleep datasets using mne.io.

    Parameters
    ----------
    file : string
        Filename (without extension).
    ext : string
        File extension (e.g. '.edf'').
    preload : bool | True
        Preload data in memory.
    kwargs : dict | {}
        Further arguments to pass to the mne.io.read function.

    Returns
    -------
    sf : float
        The original sampling-frequency.
    downsample : float
        The down-sampling frequency used.
    dsf : int
        The down-sampling factor.
    data : array_like
        The raw data of shape (n_channels, n_points)
    channels : list
        List of channel names.
    n : int
        Number of time points before down-sampling.
    start_time : datetime.time
        The time offset.
    """
    from mne import io

    # Get full path :
    path = file + ext

    # Preload :
    if preload is False:
        preload = 'temp.dat'
    kwargs['preload'] = preload

    if ext.lower() in ['.edf', '.bdf', '.gdf']:  # EDF / BDF / GDF
        raw = io.read_raw_edf(path, **kwargs)
    elif ext.lower == '.set':   # EEGLAB
        raw = io.read_raw_eeglab(path, **kwargs)
    elif ext.lower() in ['.egi', '.mff']:  # EGI / MFF
        raw = io.read_raw_egi(path, **kwargs)
    elif ext.lower() == '.cnt':  # CNT
        raw = io.read_raw_cnt(path, **kwargs)
    elif ext.lower() == '.vhdr':  # BrainVision
        raw = io.read_raw_brainvision(path, **kwargs)
    else:
        raise IOError("File not supported by mne-python.")

    raw.pick_types(meg=True, eeg=True, ecg=True, emg=True)  # Remove stim lines
    sf = raw.info['sfreq']
    dsf, downsample = get_dsf(downsample, sf)
    channels = raw.info['ch_names']
    data = raw._data

    # Conversion Volt (MNE) to microVolt (Visbrain):
    if raw._raw_extras[0] is not None and 'units' in raw._raw_extras[0]:
        units = raw._raw_extras[0]['units'][0:data.shape[0]]
        data /= np.array(units).reshape(-1, 1)

    n = data.shape[1]
    start_time = datetime.time(0, 0, 0)  # raw.info['meas_date']
    anot = raw.annotations

    return sf, downsample, dsf, data[:, ::dsf], channels, n, start_time, anot
