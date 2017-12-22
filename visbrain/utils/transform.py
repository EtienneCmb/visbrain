"""This script contains some other utility functions."""
import numpy as np
from vispy.visuals.transforms import (STTransform, ChainTransform,
                                      MatrixTransform)


__all__ = ('vprescale', 'vprecenter', 'vpnormalize', 'array_to_stt',
           'stt_to_array')


def vprescale(obj, dist=1.):
    """Get the vispy transformation for rescaling objects.

    Parameters
    ----------
    obj : tuple
        The ndarray of the object to rescale. Must be a (..., 2) or (..., 3).
    dist : float | 1.
        The final rescaling value.

    Returns
    -------
    rescale : vispy.transformations
        VisPy transformation to rescale.
    """
    # Get minimum / maximum trough last dimension :
    dim = tuple(np.arange(obj.ndim - 1, dtype=int))
    ptp = np.max(obj, axis=dim) - np.min(obj, axis=dim)
    return STTransform(scale=[dist / np.max(ptp)] * 3)


def vprecenter(obj):
    """Get the vispy transformation to recenter objects.

    Parameters
    ----------
    obj : tuple
        The ndarray of the object to recenter. Must be a (..., 2) or (..., 3).

    Returns
    -------
    recenter : vispy.transformations
        VisPy transformation to recenter.
    """
    # Check object :
    if not isinstance(obj, np.ndarray) or obj.shape[-1] not in [2, 3]:
        raise ValueError("The object must be a ndarray of shape (..., 2) or "
                         "(..., 3)")
    # Get center :
    center = np.mean(obj, axis=tuple(np.arange(obj.ndim - 1, dtype=int)))
    if center.shape[-1] == 2:
        center = np.hstack((center, 0.))
    # Build transformation :
    return STTransform(translate=-center)


def vpnormalize(obj, dist=1.):
    """Get the vispy transformation for normalizing objects.

    Parameters
    ----------
    obj : tuple
        The ndarray of the object to rescale. Must be a (..., 2) or (..., 3).
    dist : float | 1.
        The final rescaling value.

    Returns
    -------
    normalize : vispy.transformations
        VisPy transformation to normalize.
    """
    # Prepare the transformation chain :
    t = ChainTransform()
    # Recenter the object :
    t.prepend(vprecenter(obj))
    # Rescale :
    t.prepend(vprescale(obj, dist))
    return t


def array_to_stt(arr):
    """Turn a (4, 4) array into a scale and translate matrix transformation.

    Parameters
    ----------
    arr : array_like
        A (4, 4) array.

    Returns
    -------
    transform : VisPy.transform
        The VisPy transformation.
    """
    assert isinstance(arr, np.ndarray) and arr.shape == (4, 4)
    _arr = arr.copy()
    _arr[-1, 0:-1] = _arr[0:-1, -1]
    _arr[0:-1, -1] = 0.
    transform = MatrixTransform(_arr)
    # transform.scale(np.diag(_arr)[0:-1])
    # transform.translate(_arr[0:-1, -1])
    return transform


def stt_to_array(stt):
    """Convert a MatrixTransform into a (4, 4) array.

    Parameters
    ----------
    stt : MatrixTransform
        The transformation.

    Returns
    -------
    mat : array_like
        The (4, 4) array.
    """
    assert isinstance(stt, MatrixTransform)
    mat = stt.matrix.copy()
    mat[0:-1, -1] = mat[-1, 0:-1]
    mat[-1, 0:-1] = 0.
    return mat
