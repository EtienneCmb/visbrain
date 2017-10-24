"""This script contains some other utility functions."""

import sys
import os
import logging

import numpy as np

from vispy.geometry import MeshData
from vispy.geometry.isosurface import isosurface

from .sigproc import smooth_3d

__all__ = ('set_log_level', 'get_dsf', 'vispy_array', 'convert_meshdata',
           'volume_to_mesh', 'add_brain_template', 'remove_brain_template',
           'set_if_not_none', 'get_data_path')


logger = logging.getLogger('visbrain')


def set_log_level(verbose=None):
    """Convenience function for setting the logging level.

    This function comes from the PySurfer package. See :
    https://github.com/nipy/PySurfer/blob/master/surfer/utils.py

    Parameters
    ----------
    verbose : bool, str, int, or None
        The verbosity of messages to print. If a str, it can be either DEBUG,
        INFO, WARNING, ERROR, or CRITICAL. Note that these are for
        convenience and are equivalent to passing in logging.DEBUG, etc.
        For bool, True is the same as 'INFO', False is the same as 'WARNING'.
        If None, the environment variable MNE_LOG_LEVEL is read, and if
        it doesn't exist, defaults to INFO.
    return_old_level : bool
        If True, return the old verbosity level.
    """
    # import vispy
    # log = logging.getLogger('vispy')
    # log.setLevel(logging.ERROR)
    if verbose is None:
        verbose = "INFO"
    elif isinstance(verbose, bool):
        if verbose is True:
            verbose = 'INFO'
        else:
            verbose = 'WARNING'
    if isinstance(verbose, str):
        verbose = verbose.upper()
        logging_types = dict(DEBUG=logging.DEBUG, INFO=logging.INFO,
                             WARNING=logging.WARNING, ERROR=logging.ERROR,
                             CRITICAL=logging.CRITICAL)
        if verbose not in logging_types:
            raise ValueError('verbose must be of a valid type')
        verbose = logging_types[verbose]
    format = "%(levelname)s : %(message)s"
    logging.basicConfig(format=format)
    logger.setLevel(verbose)


def get_dsf(downsample, sf):
    """Get the downsampling factor.

    Parameters
    ----------
    downsample : float
        The down-sampling frequency.
    sf : float
        The sampling frequency
    """
    if all([isinstance(k, (int, float)) for k in (downsample, sf)]):
        dsf = int(np.round(sf / downsample))
        downsample = float(sf / dsf)
        return dsf, downsample
    else:
        return 1, downsample


def vispy_array(data, dtype=np.float32):
    """Check and convert array to be compatible with buffers.

    Parameters
    ----------
    data : array_like
        Array of data.
    dtype : type | np.float32
        Futur type of the array.

    Returns
    -------
    data : array_like
        Contiguous array of type dtype.
    """
    if not data.flags['C_CONTIGUOUS']:
        data = np.ascontiguousarray(data, dtype=dtype)
    if data.dtype != dtype:
        data = data.astype(dtype, copy=False)
    return data


def convert_meshdata(vertices=None, faces=None, normals=None, meshdata=None,
                     invert_normals=False, transform=None):
    """Convert mesh data to be compatible with visbrain.

    Parameters
    ----------
    vertices : array_like | None
        Vertices of the template of shape (N, 3) or (N, 3, 3) if indexed by
        faces.
    faces : array_like | None
        Faces of the template of shape (M, 3)
    normals : array_like | None
        The normals to each vertex, with the same shape as vertices.
    meshdata : VisPy.MeshData | None
        VisPy MeshData object.
    invert_normals : bool | False
        If the brain appear to be black, use this parameter to invert normals.
    transform : visPy.transform | None
        VisPy transformation to apply to vertices ans normals.

    Returns
    -------
    vertices : array_like
        Vertices of shape (N, 3)
    faces : array_like
        Faces of the template of shape (M, 3)
    normals : array_like
        The normals of shape (M, 3, 3).
    """
    # Priority to meshdata :
    if meshdata is not None:
        vertices = meshdata.get_vertices()
        faces = meshdata.get_faces()
        normals = meshdata.get_vertex_normals(indexed='faces')
        logger.debug('Indexed faces normals converted // extracted')
    else:
        # Check if faces index start at zero (Matlab like):
        if faces.min() != 0:
            faces -= faces.min()
        # Get normals if None :
        if (normals is None) or (normals.ndim != 2):
            md = MeshData(vertices=vertices, faces=faces)
            normals = md.get_vertex_normals()
            logger.debug('Indexed faces normals converted // extracted')
    assert vertices.ndim == 2

    # Invert normals :
    norm_coef = -1. if invert_normals else 1.
    normals *= norm_coef

    # Apply transformation :
    if transform is not None:
        vertices = transform.map(vertices)[..., 0:-1]
        normals = transform.map(normals)[..., 0:-1]

    # Type checking :
    vertices = vispy_array(vertices)
    faces = vispy_array(faces, np.uint32)
    normals = vispy_array(normals)

    return vertices, faces, normals


def volume_to_mesh(vol, smooth_factor=3, level=None, **kwargs):
    """Convert a volume into a mesh with vertices, faces and normals.

    Parameters
    ----------
    vol : array_like
        The volume of shape (N, M, P)
    smooth_factor : int | 3
        The smoothing factor to apply to the volume.
    level : int | None
        Level to extract.
    kwargs : dict | {}
        Optional arguments to pass to convert_meshdata.

    Returns
    -------
    vertices : array_like
        Mesh vertices.
    faces : array_like
        Mesh faces.
    normals : array_like
        Mesh normals.
    """
    # Smooth the volume :
    vol_s = smooth_3d(vol, smooth_factor)
    # Extract vertices and faces :
    if level is None:
        level = .5
    elif isinstance(level, int):
        vol_s[vol_s != level] = 0
        level = .5
    vert_n, faces_n = isosurface(vol_s, level=level)
    # Convert to meshdata :
    vertices, faces, normals = convert_meshdata(vert_n, faces_n, **kwargs)
    return vertices, faces, normals


def add_brain_template(name, vertices, faces, normals=None, lr_index=None):
    """Add a brain template to the default list.

    Parameters
    ----------
    name : string
        Name of the template.
    vertices : array_like
        Vertices of the template of shape (N, 3) or (N, 3, 3) if indexed by
        faces.
    faces : array_like
        Faces of the template of shape (M, 3)
    normals : array_like
        The normals of the template, with the same shape as vertices.
    lr_index : int | None
        Specify where to cut vertices for left and right hemisphere so that
        x_left <= lr_index and right > lr_index
    """
    # Convert meshdata :
    vertices, faces, normals = convert_meshdata(vertices, faces, normals)
    # Get path to the templates/ folder :
    name = os.path.splitext(name)[0]
    path = get_data_path(folder='templates', file=name + '.npz')
    # Save the template :
    np.savez(path, vertices=vertices, faces=faces, normals=normals,
             lr_index=lr_index)


def remove_brain_template(name):
    """Remove brain template from the default list.

    Parameters
    ----------
    name : string
        Name of the template to remove.
    """
    assert name not in ['B1', 'B2', 'B3']
    # Get path to the templates/ folder :
    name = os.path.splitext(name)[0]
    path = get_data_path(folder='templates', file=name + '.npz')
    # Remove the file from templates/ folder :
    if os.path.isfile(path):
        os.remove(path)
    else:
        raise ValueError("No file " + path)


def set_if_not_none(to_set, value, cond=True):
    """Set a variable if the value is not None.

    Parameters
    ----------
    to_set : string
        The variable name.
    value : any
        The value to set.
    cond : bool | True
        Additional condition.

    Returns
    -------
    val : any
        The value if not None else to_set
    """
    return value if (value is not None) and cond else to_set


def get_data_path(folder=None, file=None):
    """Get the path to the visbrain data folder.

    This function can find a file in visbrain/data or visbrain/data/folder.

    Parameters
    ----------
    folder : string | None
        Sub-folder of visbrain/data.
    file : string | None
        File name.

    Returns
    -------
    path : string
        Path to the data folder or to the file if file is not None.
    """
    cur_path = sys.modules[__name__].__file__.split('utils')[0]
    folder = '' if not isinstance(folder, str) else folder
    file = '' if not isinstance(file, str) else file
    return os.path.join(*(cur_path, 'data', folder, file))
