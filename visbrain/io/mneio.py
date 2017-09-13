"""Utility functions for MNE."""

__all__ = ['mne_switch']


def mne_switch(file, ext, *args, **kwargs):
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

    if ext in ['.edf', '.bdf']:  # EDF / BDF
        raw = io.read_raw_edf(path, *args, **kwargs)
    elif ext == ['.egi', '.mff']:  # EGI / MFF
        raw = io.read_raw_egi(path, *args, **kwargs)
    elif ext == '.cnt':  # EGI
        raw = io.read_raw_cnt(path, *args, **kwargs)
