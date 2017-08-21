"""Load data files.

This file contain functions to load :
- Matlab (*.mat)
- Pickle (*.pickle)
- NumPy (*.npy and *.npz)
- Text (*.txt)
- CSV (*.csv)
- JSON (*.json)
- NIFTI
"""
import numpy as np
from scipy.io import loadmat
# import os

from ..utils.transform import array_to_stt
from .dependencies import is_nibabel_installed
from .rw_utils import get_file_ext

__all__ = ('switch_data', 'read_mat', 'read_pickle', 'read_npy', 'read_npz',
           'read_txt', 'read_csv', 'read_json', 'read_nifti')


def switch_data(path, *args, **kwargs):
    """Switch between data files.

    Args:
        path: string
            Filename.

        arg: tuple
            Further arguments.

    Kargs:
        kargs: dict, optional, (def: {})
            Further optional arguments.
    """
    # Find file extension :
    file, ext = get_file_ext(path)

    if ext == '.mat':  # Matlab
        return read_mat(path, *args, **kwargs)

    elif ext == '.pickle':  # Pickle
        return read_pickle(path, *args, **kwargs)

    elif ext == '.npy':  # NumPy (npy)
        return read_npy(path, *args, **kwargs)

    elif ext == '.npz':  # NumPy (npz)
        return read_npz(path, *args, **kwargs)

    elif ext == '.txt':  # Text file
        return read_txt(path, *args, **kwargs)

    elif ext == '.csv':  # CSV file
        return read_csv(path, *args, **kwargs)

    elif ext == '.json':  # JSON file
        return read_json(path, *args, **kwargs)


def read_mat(path, vars=None):
    """Read data from a Matlab (mat) file."""
    return loadmat(path, variable_names=vars)


def read_pickle(path, vars=None):
    """Read data from a Pickle (pickle) file."""
    # np.loads? ou depuis import pickle
    pass


def read_npy(path):
    """Read data from a NumPy (npy) file."""
    return np.load(path)


def read_npz(path, vars=None):
    """Read data from a Numpy (npz) file."""
    pass


def read_txt(path):
    """Read data from a text (txt) file."""
    pass


def read_csv(path):
    """Read data from a CSV (csv) file."""
    pass


def read_json(path):
    """Read data from a JSON (json) file."""
    pass


def read_nifti(path):
    """Read data from a NIFTI file using Nibabel.

    Parameters
    ----------
    path : string
        Path to the nifti file.

    Returns
    -------
    vol : array_like
        The 3-D volume data.
    header : Nifti1Header
        Nifti header.
    transform : VisPy.transform
        The transformation
    """
    if is_nibabel_installed():
        import nibabel as nib
        # Load the file :
        img = nib.load(path)
        # Get the data and affine transformation ::
        vol = img.get_data()
        affine = img.affine
        # Define the transformation :
        transform = array_to_stt(affine)

        return vol, img.header, transform
    else:
        raise IOError("The python package Nibabel must be installed to load "
                      "the Nifti file.")
