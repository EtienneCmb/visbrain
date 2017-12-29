"""Save templates (brain, roi, volume...) to the tmp folder."""
import logging
import os
import numpy as np

from .path import path_to_visbrain_data, path_to_tmp
from ..utils.mesh import convert_meshdata

logger = logging.getLogger('visbrain')

__all__ = ['add_brain_template', 'remove_brain_template',
           'save_volume_template', 'remove_volume_template']


def add_brain_template(name, vertices, faces, normals=None, lr_index=None,
                       tmpfile=False):
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
    tmpfile : bool | False
        Specify if the saved brain template is a temporary file (in that case,
        saved in visbrain/data/tmp/templates).
    """
    # Convert meshdata :
    vertices, faces, normals = convert_meshdata(vertices, faces, normals)
    # Create templates folder if doesn't exist :
    vb_path = path_to_visbrain_data(folder='templates')
    if not os.path.exists(vb_path):
        os.mkdir(vb_path)
    # Get path to the templates/ folder :
    name = os.path.splitext(name)[0]
    if tmpfile:
        path = path_to_tmp(folder='templates', file=name + '.npz')
    else:
        path = path_to_visbrain_data(folder='templates', file=name + '.npz')
    # Save the template :
    np.savez_compressed(path, vertices=vertices, faces=faces, normals=normals,
                        lr_index=lr_index)
    logger.info("Brain template saved (%s)." % path)


def remove_brain_template(name):
    """Remove brain template from the default list.

    Parameters
    ----------
    name : string
        Name of the template to remove.
    """
    # Get path to the templates/ folder :
    name = os.path.splitext(name)[0]
    path = path_to_visbrain_data(folder='templates', file=name + '.npz')
    # Remove the file from templates/ folder :
    if os.path.isfile(path):
        os.remove(path)
        logger.info("Brain template removed (%s)." % path)
    else:
        raise ValueError("No file " + path)


def save_volume_template(name, vol, labels, index, hdr, tmpfile=False):
    """Save as a predefined ROI atlas.

    Parameters
    ----------
    name : string
        Name of the ROI atlas.
    vol : array_like
        The volume of shape (nx, ny, nz).
    labels : array_like
        Array of labels of type object and of length n_labels.
    index : array_like
        Array of index corresponding to the labels of type np.int and of length
        n_labels.
    hdr : array_like
        The matrix of transformation of shape (4, 4).
    """
    path_to_save = path_to_visbrain_data(folder='roi')
    if not os.path.exists(path_to_save):
        os.mkdir(path_to_save)
    if tmpfile:
        path_to_save = path_to_tmp(folder='roi', file=name + '.npz')
    else:
        path_to_save = path_to_visbrain_data(folder='roi', file=name + '.npz')
    np.savez_compressed(path_to_save, vol=vol, hdr=hdr, index=index,
                        labels=labels)
    logger.info("%s is now a default ROI object. Use `r_obj = RoiObj('%s')` to"
                " call it." % (name, name))


def remove_volume_template(name):
    """Remove a predefined ROI object.

    Parameters
    ----------
    name : string
        Name of the ROI atlas.
    """
    path_to_file = path_to_visbrain_data(folder='roi', file=name + '.npz')
    if os.path.isfile(path_to_file):
        os.remove(path_to_file)
        logger.info("%s ROI object removed." % name)
