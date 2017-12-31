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
# import os

from ..utils.transform import array_to_stt
from .dependencies import is_nibabel_installed

__all__ = ('read_mat', 'read_pickle', 'read_npy', 'read_npz',
           'read_txt', 'read_csv', 'read_json', 'read_nifti', 'read_stc')


def read_mat(path, vars=None):
    """Read data from a Matlab (mat) file."""
    from scipy.io import loadmat
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


def read_nifti(path, hdr_as_array=False):
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
    is_nibabel_installed(raise_error=True)
    import nibabel as nib
    # Load the file :
    img = nib.load(path)
    # Get the data and affine transformation ::
    vol = img.get_data()
    affine = img.affine
    # Define the transformation :
    if hdr_as_array:
        transform = affine
    else:
        transform = array_to_stt(affine)

    return vol, img.header, transform


def read_stc(path):
    """Read an STC file from the MNE package.

    STC files contain activations or source reconstructions
    obtained from EEG and MEG data.

    This function is a copy from the PySurfer package. See :
    https://github.com/nipy/PySurfer/blob/master/surfer/io.py

    Parameters
    ----------
    path : string
        Path to STC file

    Returns
    -------
    data : dict
        The STC structure. It has the following keys:
           tmin           The first time point of the data in seconds
           tstep          Time between frames in seconds
           vertices       vertex indices (0 based)
           data           The data matrix (nvert * ntime)
    """
    fid = open(path, 'rb')

    stc = dict()

    fid.seek(0, 2)  # go to end of file
    file_length = fid.tell()
    fid.seek(0, 0)  # go to beginning of file

    # read tmin in ms
    stc['tmin'] = float(np.fromfile(fid, dtype=">f4", count=1))
    stc['tmin'] /= 1000.0

    # read sampling rate in ms
    stc['tstep'] = float(np.fromfile(fid, dtype=">f4", count=1))
    stc['tstep'] /= 1000.0

    # read number of vertices/sources
    vertices_n = int(np.fromfile(fid, dtype=">u4", count=1))

    # read the source vector
    stc['vertices'] = np.fromfile(fid, dtype=">u4", count=vertices_n)

    # read the number of timepts
    data_n = int(np.fromfile(fid, dtype=">u4", count=1))

    if ((file_length / 4 - 4 - vertices_n) % (data_n * vertices_n)) != 0:
        raise ValueError('incorrect stc file size')

    # read the data matrix
    stc['data'] = np.fromfile(fid, dtype=">f4", count=vertices_n * data_n)
    stc['data'] = stc['data'].reshape([data_n, vertices_n]).T

    # close the file
    fid.close()
    return stc
