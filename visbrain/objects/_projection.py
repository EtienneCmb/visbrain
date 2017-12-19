"""Projection of a source object onto a brain object."""
import numpy as np
from scipy.spatial.distance import cdist

from ..utils import (normalize, array2colormap, color2vb)

import logging
logger = logging.getLogger('visbrain')
PROJ_STR = "%i sources visibles and not masked used for the %s"


def _get_eucl_mask(v, xyz, radius, contribute, xsign):
    # Compute euclidian distance and get sources under radius :
    eucl = cdist(v, xyz)
    eucl = eucl.astype(np.float32, copy=False)
    mask = eucl <= radius
    # Contribute :
    if not contribute:
        # Get vertices sign :
        vsign = np.sign(v[:, 0]).reshape(-1, 1)
        # Find where vsign and xsign are equals :
        isign = np.logical_and(vsign != xsign, xsign != 0)
        mask[isign] = False
    return eucl, mask


def _check_projection(s_obj, v, radius, contribute, not_masked=True):
    # =============== CHECKING ===============
    assert isinstance(v, np.ndarray)
    assert isinstance(radius, (int, float))
    assert isinstance(contribute, bool)
    if v.ndim == 2:  # index faced vertices
        v = v[:, np.newaxis, :]

    # =============== PRE-ALLOCATION ===============
    if not_masked:  # get visible and not masked sources
        mask = s_obj.visible_and_not_masked
    else:           # get visible and masked sources
        mask = np.logical_and(s_obj.mask, s_obj.visible)
    xyz, data = s_obj._xyz[mask, :], s_obj._data[mask]
    # Get sign of the x coordinate :
    xsign = np.sign(xyz[:, 0]).reshape(1, -1)

    return xyz, data, v, xsign


def _project_modulation(s_obj, v, radius, contribute=False):
    """Project source's data onto vertices.

    Parameters
    ----------
    s_obj : SourceObj
        The source object to project.
    v : array_like
        The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
    radius : float
        The radius under which activity is projected on vertices.
    contribute: bool | False
        Specify if sources contribute on both hemisphere.

    Returns
    -------
    modulation : array_like
        The modulations of shape (nv, 3) or (nv, 3, 3) if index faced. This
        is a masked array where the mask refer to sources that are over the
        radius.
    """
    # Check inputs :
    xyz, data, v, xsign = _check_projection(s_obj, v, radius, contribute)
    logger.info(PROJ_STR % (len(data), 'projection'))
    index_faced = v.shape[1]
    # Modulation / proportion / (Min, Max) :
    modulation = np.ma.zeros((v.shape[0], index_faced), dtype=np.float32)
    prop = np.zeros_like(modulation.data)
    minmax = np.zeros((index_faced, 2), dtype=np.float32)
    if len(data) == 0:
        logger.warn("Projection ignored because no sources visibles and "
                    "not masked")
        return np.squeeze(np.ma.masked_array(modulation, True))

    # For each triangle :
    for k in range(index_faced):
        # =============== EUCLIDIAN DISTANCE ===============
        eucl, mask = _get_eucl_mask(v[:, k, :], xyz, radius, contribute, xsign)
        # Invert euclidian distance for modulation and mask it :
        np.multiply(eucl, -1. / eucl.max(), out=eucl)
        np.add(eucl, 1., out=eucl)
        eucl = np.ma.masked_array(eucl, mask=np.invert(mask),
                                  dtype=np.float32)

        # =============== MODULATION ===============
        # Modulate data by distance (only for sources under radius) :
        modulation[:, k] = np.ma.dot(eucl, data, strict=False)

        # =============== PROPORTIONS ===============
        np.sum(mask, axis=1, dtype=np.float32, out=prop[:, k])
        nnz = np.nonzero(mask.sum(0))
        minmax[k, :] = np.array([data[nnz].min(), data[nnz].max()])

    # Divide modulations by the number of contributing sources :
    prop[prop == 0.] = 1.
    np.divide(modulation, prop, out=modulation)
    # Normalize inplace modulations between under radius data :
    normalize(modulation, minmax.min(), minmax.max())
    s_obj._minmax = (modulation.min(), modulation.max())

    return np.squeeze(modulation)


def _project_repartition(s_obj, v, radius, contribute=False):
    """Project source's repartition onto vertices.

    Parameters
    ----------
    s_obj : SourceObj
        The source object to project.
    v : array_like
        The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
    radius : float
        The radius under which activity is projected on vertices.
    contribute: bool | False
        Specify if sources contribute on both hemisphere.

    Returns
    -------
    repartition: array_like
        The repartition of shape (nv, 3) or (nv, 3, 3) if index faced. This
        is a masked array where the mask refer to sources that are over the
        radius.
    """
    # Check inputs :
    xyz, _, v, xsign = _check_projection(s_obj, v, radius, contribute)
    logger.info(PROJ_STR % (xyz.shape[0], 'repartition'))
    index_faced = v.shape[1]
    # Corticale repartition :
    repartition = np.ma.zeros((v.shape[0], index_faced), dtype=np.int)
    if not xyz.size:
        logger.warn("Repartition ignored because no sources visibles and "
                    "not masked")
        return np.squeeze(np.ma.masked_array(repartition, True))

    # For each triangle :
    for k in range(index_faced):
        # =============== EUCLIDIAN DISTANCE ===============
        eucl, mask = _get_eucl_mask(v[:, k, :], xyz, radius, contribute, xsign)

        # =============== REPARTITION ===============
        # Sum over sources dimension :
        sm = np.sum(mask, 1, dtype=np.int)
        smmask = np.invert(sm.astype(bool))
        repartition[:, k] = np.ma.masked_array(sm, mask=smmask)
    s_obj._minmax = (repartition.min(), repartition.max())

    return np.squeeze(repartition)


def _get_masked_index(s_obj, v, radius, contribute=False):
    """Get the index of masked source's under radius.

    Parameters
    ----------
    s_obj : SourceObj
        The source object to project.
    v : array_like
        The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
    radius : float
        The radius under which activity is projected on vertices.
    contribute: bool | False
        Specify if sources contribute on both hemisphere.

    Returns
    -------
    idx: array_like
        The repartition of shape (nv, 3) or (nv, 3, 3) if index faced.
    """
    # Check inputs and get masked xyz / data :
    xyz, data, v, xsign = _check_projection(s_obj, v, radius, contribute,
                                            False)
    logger.info("%i sources visibles and masked found" % len(data))
    # Predefined masked euclidian distance :
    nv, index_faced = v.shape[0], v.shape[1]
    fmask = np.ones((v.shape[0], index_faced, len(data)), dtype=bool)

    # For each triangle :
    for k in range(index_faced):
        # =============== EUCLIDIAN DISTANCE ===============
        _, fmask[:, k, :] = _get_eucl_mask(v[:, k, :], xyz, radius, contribute,
                                           xsign)
    # Find where there's sources under radius and need to be masked :
    m = fmask.reshape(fmask.shape[0] * index_faced, fmask.shape[2])
    idx = np.dot(m, np.ones((len(data),), dtype=bool))

    return np.squeeze(idx.reshape(nv, index_faced))


def _project_sources_data(s_obj, b_obj, project='modulation', radius=10.,
                          contribute=False, cmap='viridis', clim=None,
                          vmin=None, under='black', vmax=None, over='red',
                          mask_color=None):
    """Project source's data."""
    # _____________________ CHECKING _____________________
    assert type(s_obj).__name__ in ['SourceObj', 'CombineSources']
    assert type(b_obj).__name__ in ['BrainObj', 'RoiObj']
    assert isinstance(radius, (int, float))
    if project == 'modulation':
        project_fcn = _project_modulation
    elif project == 'repartition':
        project_fcn = _project_repartition
    else:
        raise ValueError("`project` must either be 'modulation' or "
                         "'repartition'")
    if mask_color is None:
        logger.warning("mask_color use %s.mask_color variable" % s_obj.name)
        mask_color = s_obj.mask_color
    mask_color = color2vb(mask_color)
    logger.info("Project the source's %s (radius=%r, "
                "contribute=%r)" % (project, radius, contribute))
    # Get mesh and vertices :
    mesh = b_obj.mesh
    vertices = mesh._vertices
    mask = np.zeros((vertices.shape[0]), dtype=np.float32)

    # _____________________ GET MODULATION _____________________
    mod = project_fcn(s_obj, vertices, radius, contribute)
    # Update mesh color informations :
    b_obj._cbar_data = mod
    b_obj._minmax = (float(mod.min()), float(mod.max()))
    if clim is None:
        clim = b_obj._minmax
        b_obj._clim = b_obj._minmax
    # Get where there's masked sources :
    if s_obj.is_masked:
        mask_idx = _get_masked_index(s_obj, vertices, radius, contribute)
        mask[mask_idx] = 2.
        mesh.mask_color = mask_color
        logger.info("Set masked sources cortical activity to the "
                    "color %s" % str(list(mesh.mask_color.ravel())[0:-1]))
    # Enable to set color to active vertices :
    if mod.mask.sum():
        mask[~mod.mask] = 1.

    # _____________________ MODULATION TO COLOR _____________________
    mesh.mask = mask
    mod_color = array2colormap(mod, cmap=cmap, clim=clim, vmin=vmin, vmax=vmax,
                               under=under, over=over)
    mesh.color = mod_color
