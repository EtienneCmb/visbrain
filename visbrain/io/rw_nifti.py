"""Read nifti (nii.gz) files."""
import os

import numpy as np

from .dependencies import is_nibabel_installed
from .path import path_to_visbrain_data
from ..utils.transform import array_to_stt

from vispy.visuals.transforms import (MatrixTransform, ChainTransform,
                                      STTransform)


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
    # Replace NaNs with 0. :
    vol[np.isnan(vol)] = 0.
    # Define the transformation :
    if hdr_as_array:
        transform = affine
    else:
        transform = array_to_stt(affine)

    return vol, img.header, transform


def read_mist(name):
    """Load MIST parcellation.

    See : MIST: A multi-resolution parcellation of functional networks
    Authors : Sebastian Urchs, Jonathan Armoza, Yassine Benhajali,
              Jolène St-Aubin, Pierre Orban, Pierre Bellec

    Parameters
    ----------
    name : string
        Name of the level. Use MIST_x with x 7, 12, 20, 36, 64, 122 or ROI.

    Returns
    -------
    vol : array_like | None
        ROI volume.
    labels : array_like | None
        Array of labels.
    index : array_like | None
        Array of index that make the correspondance between the volume values
        and labels.
    hdr : array_like | None
        Array of transform source's coordinates into the volume space.
    """
    name = name.upper()
    assert ('MIST' in name) and ('_' in name)
    level = name.split('_')[-1]
    assert level in ['7', '12', '20', '36', '64', '122', 'ROI']
    # Define path :
    parc, parc_info = '%s.nii.gz', '%s.csv'
    folder, folder_info = 'Parcellations', 'Parcel_Information'
    mist_path = path_to_visbrain_data('mist', 'roi')
    parc_path = os.path.join(*(mist_path, folder, parc % name))
    parc_info_path = os.path.join(*(mist_path, folder_info, parc_info % name))
    # Load info :
    m = np.genfromtxt(parc_info_path, delimiter=';', dtype=str, skip_header=1,
                      usecols=[0, 1, 2])
    n_roi = m.shape[0]
    index = m[:, 0].astype(int)
    lab_, name_ = 'label_%s' % level, 'name_%s' % level
    labels = np.zeros(n_roi, dtype=[(lab_, object), (name_, object)])
    labels[lab_] = m[:, 1]
    labels[name_] = np.char.replace(np.char.capitalize(m[:, 2]), '_', ' ')
    # Load parc :
    vol, _, hdr = read_nifti(parc_path, hdr_as_array=True)
    return vol, labels, index, hdr


def _niimg_var(vol, hdr):
    """Get transformation variables.

    Parameters
    ----------
    vol : array_like
        The 3D array of the volume.
    hdr : array_like
        The (4, 4) transformation array.

    Returns
    -------
    sh : array_like
        Shape of the volume
    diag : array_like
        Diagonale of the transformation
    tr : array_like
        Translation of the transformation
    """
    assert vol.ndim == 3, "Volume should be an (n_x, n_y, n_z) array"
    n_x, n_y, n_z = vol.shape
    assert isinstance(hdr, (MatrixTransform, np.ndarray))
    if isinstance(hdr, MatrixTransform):
        affine = np.array(hdr.matrix).copy()
    # Get diagonal and translation
    d_x, d_y, d_z = np.diag(affine)[0:-1]
    t_x, t_y, t_z = affine[-1, 0:-1]
    return np.array(vol.shape), np.diag(affine)[0:-1], affine[-1, 0:-1]


def _niimg_norm(sh, diag, translate):
    """Normalize the volume between (0., 1.)."""
    # Compute normalization ratio
    ratio = np.abs(diag) * sh
    sgn = np.sign(diag)
    # Get scale and translate
    sc = 1. / ratio
    tr = -(translate + np.array([0., 0, 0])) / ratio
    # Define transformations of each slice
    sg_norm = STTransform(scale=(sc[1], sc[2], 1.),
                          translate=(tr[1], tr[2], 1.))
    cr_norm = STTransform(scale=(sc[0], sc[2], 1.),
                          translate=(sgn[0] * tr[0], tr[2], 1.))
    ax_norm = STTransform(scale=(sc[1], sc[0], 1.),
                          translate=(tr[1], sgn[0] * tr[0], 1.))
    return sg_norm, cr_norm, ax_norm


def _niimg_rot():
    """Get rotation trnasformations of each slice."""
    # Sagittal
    sg_rot = MatrixTransform()
    sg_rot.rotate(90., (0, 0, 1))
    sg_rot.rotate(180., (0, 1, 0))
    # Coronal
    cr_rot = MatrixTransform()
    cr_rot.rotate(90., (0, 0, 1))
    cr_rot.rotate(180., (0, 1, 0))
    # Axial
    ax_rot = MatrixTransform()
    ax_rot.rotate(180., (1, 0, 0))
    return sg_rot, cr_rot, ax_rot


def _niimg_mat(hdr, idx):
    """Get the transformation of a single slice.

    Parameters
    ----------
    hdr : array_like
        The (4, 4) transformation array.
    idx : tuple
        Slices indicies.

    Returns
    -------
    tf : MatrixTransform
        Image transformation.
    """
    hdr_mat = np.array(hdr.matrix).copy().T
    mat = np.identity(4, dtype=np.float32)

    to_idx = [[idx[0]], [idx[1]]], [idx[0], idx[1]]
    mat[[[0], [1]], [0, 1]] = hdr_mat[to_idx]
    mat[[0, 1], -1] = hdr_mat[[idx[0], idx[1]], -1]
    return MatrixTransform(mat.T)


def _niimg_mni(hdr):
    """Transformation for MNI conversions of each slice."""
    sg_mni = _niimg_mat(hdr, (2, 1))
    cr_mni = _niimg_mat(hdr, (2, 0))
    ax_mni = _niimg_mat(hdr, (1, 0))
    return sg_mni, cr_mni, ax_mni


def niimg_to_transform(vol, hdr, as_bgd=True, vol_bgd=None, hdr_bgd=None):
    """Get transformations of nii.gz files for cross-sections.

    Parameters
    ----------
    vol : array_like
        3D volume data.
    hdr : array_like
        Array of transformation of shape (4, 4).
    as_bgd : bool | True
        Specify if the volume is a background image or have to be considered as
        an activation image.
    vol_bgd : array_like | None
        Volume data if `as_bgd` is True.
    hdr_bgd : array_like | None
        Transformation array if `as_bgd` is True.

    Returns
    -------
    sg_tf : ChainTransform
        Transformation of sagittal view
    cr_tf : ChainTransform
        Transformation of coronal view
    ax_tf : ChainTransform
        Transformation of axial view
    """
    # Get transformation variables
    sh_img, diag_img, tr_img = _niimg_var(vol, hdr)
    # Get the normalization transformation depending if the volume is an image
    # background or an activation image
    if as_bgd:  # Background image
        sg_norm, cr_norm, ax_norm = _niimg_norm(sh_img - 1, diag_img, tr_img)
    else:       # Activation image
        sh_bgd, diag_bgd, tr_bgd = _niimg_var(vol_bgd, hdr_bgd)
        sg_norm, cr_norm, ax_norm = _niimg_norm(sh_bgd - 1, diag_bgd, tr_bgd)
    # Get MNI and rotation transformations
    sg_mni, cr_mni, ax_mni = _niimg_mni(hdr)
    sg_rot, cr_rot, ax_rot = _niimg_rot()
    # Build the chain of transformation
    sg_tf = ChainTransform([sg_norm, sg_rot, sg_mni])
    cr_tf = ChainTransform([cr_norm, cr_rot, cr_mni])
    ax_tf = ChainTransform([ax_norm, ax_rot, ax_mni])
    return sg_tf, cr_tf, ax_tf
