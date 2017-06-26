"""Utility functions if MNE is installed."""

__all__ = ['mne_is_installed', 'mne_read_sleep']


def mne_is_installed():
    """Test if MNE is installed."""
    try:
        import mne
        return True
    except:
        return False


def mne_read_sleep(file, ext, *args, **kwargs):
    """Read sleep datasets using mne.io.

    Args:
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
    from mne.io import (read_raw_egi, read_raw_cnt)
    raise ValueError("ASSURER COMPATIBILITE MNE")

    # Get full path :
    path = file + ext

    if ext == '.egi':  # EGI
        return read_raw_egi(path, *args, **kwargs)

    elif ext == '.cnt':  # EGI
        return read_raw_cnt(path, *args, **kwargs)
