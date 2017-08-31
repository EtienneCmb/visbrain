"""This script contains some other utility functions."""

import sys
import os
from warnings import warn
import numpy as np

from vispy.geometry import MeshData

__all__ = ('vis_args', 'check_downsampling', 'vispy_array', 'convert_meshdata',
           'add_brain_template', 'remove_brain_template', 'set_if_not_none')


def vis_args(kw, prefix, ignore=[]):
    """Extract arguments that contain a prefix from a dictionary.

    Parameters
    ----------
    kw : dict
        The dictionary of arguments
    prefix : string
        The prefix to use (something like 'nd_', 'cb_'...)
    ignors : list | []
        List of patterns to ignore.

    Returns
    -------
    args : dict
        The dictionary which contain aguments starting with prefix.
    others : dict
        A dictionary with all other arguments.
    """
    # Create two dictionaries (for usefull args and others) :
    args, others = {}, {}
    l = len(prefix)
    #
    for k, v in zip(kw.keys(), kw.values()):
        entry = k[:l]
        if (entry == prefix) and (k not in ignore):
            args[k.replace(prefix, '')] = v
        else:
            others[k] = v
    return args, others


def check_downsampling(sf, ds):
    """Check the down-sampling frequency and return the most appropriate one.

    Parameters
    ----------
    sf : float
        The sampling frequency
    ds : float
        The desired down-sampling frequency.

    Returns
    -------
    dsout : float
        The most appropriate down-sampling frequency.
    """
    if sf % ds != 0:
        dsbck = ds
        ds = int(sf / round(sf / (ds)))
        while sf % ds != 0:
            ds -= 1
        # ds = sf / round(sf / ds)
        warn("Using a down-sampling frequency (" + str(dsbck) + "hz) that is "
             "not a multiple of the sampling frequency (" + str(sf) + "hz) is"
             " not recommanded. A " + str(ds) + "hz will be used instead.")
    return ds


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
        Vertices of shape (N, 3, 3)
    faces : array_like
        Faces of the template of shape (M, 3)
    normals : array_like
        The normals of the template, with the same shape as vertices.
    """
    # Priority to meshdata :
    if meshdata is not None:
        vertices = meshdata.get_vertices(indexed='faces')
        faces = meshdata.get_faces()
        normals = meshdata.get_vertex_normals(indexed='faces')
    else:
        # Check if faces index start at zero (Matlab like):
        if faces.min() != 0:
            faces -= faces.min()
        # Get normals if None :
        if (normals is None) or (vertices.ndim == 2):
            md = MeshData(vertices=vertices, faces=faces)
            vertices = md.get_vertices(indexed='faces')
            normals = md.get_vertex_normals(indexed='faces')

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


def add_brain_template(name, vertices, faces, normals, lr_index=None):
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
    # Get path to the templates/ folder :
    name = os.path.splitext(name)[0]
    dirfile = sys.modules[__name__].__file__.split('utils')[0]
    to_temp = (dirfile, 'brain', 'base', 'templates', name + '.npz')
    path = os.path.join(*to_temp)
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
    # Get path to the templates/ folder :
    name = os.path.splitext(name)[0]
    dirfile = sys.modules[__name__].__file__.split('utils')[0]
    to_temp = (dirfile, 'brain', 'base', 'templates', name + '.npz')
    path = os.path.join(*to_temp)
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
