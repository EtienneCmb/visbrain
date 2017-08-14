"""Load sleep files.

This file contain functions to load :
- European Data Format (*.edf)
- Micromed (*.trc)
- BrainVision (*.eeg)
- ELAN (*.eeg)
- Hypnogram (*.hyp)
"""
import os

from .rw_utils import get_file_ext
from .mneio import mne_read_sleep
from .dependencies import is_mne_installed

__all__ = ['switch_sleep', 'read_edf', 'read_trc', 'read_eeg', 'read_elan',
           'read_hyp']


def switch_sleep(path, *args, **kwargs):
    """Switch between sleep data files.

    Args:
        path: string
            Full path to the filename.

        arg: tuple
            Further arguments.

    Kargs:
        kargs: dict, optional, (def: {})
            Further optional arguments.
    """
    # Find file extension :
    file, ext = get_file_ext(path)

    if ext == '.eeg':  # BrainVision // ELAN
        if os.path.isfile(file + '.ent'):  # ELAN
            return read_elan(path, *args, **kwargs)

        elif os.path.isfile(file + '.vhdr'):  # BrainVision
            return read_eeg(path, *args, **kwargs)

        else:  # None :
            raise ValueError("No header file found in this directory. You "
                             "should have a *.ent (ELAN) or *.vhdr "
                             "(BrainVision)")

    elif ext == '.edf':  # European Data Format
        return read_edf(path, *args, **kwargs)

    elif ext == '.trc':  # Micromed
        return read_trc(path, *args, **kwargs)

    elif is_mne_installed() and (ext in ['.egi', '.cnt']):  # Present in MNE
        return mne_read_sleep(file, ext, *args, **kwargs)

    else:  # None
        raise ValueError("*" + ext + " files are currently not supported.")


def read_edf():
    """Read data from a European Data Format (edf) file."""
    pass


def read_trc():
    """Read data from a Micromed (trc) file."""
    pass


def read_eeg():
    """Read data from a BrainVision (eeg) file."""
    pass


def read_elan():
    """Read data from a ELAN (eeg) file."""
    pass


def read_hyp():
    """Read data from a hypnogram (hyp) file."""
    pass
