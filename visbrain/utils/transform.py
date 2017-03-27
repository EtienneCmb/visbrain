"""This script contains some other utility functions."""
import numpy as np
from vispy.visuals.transforms import (STTransform, ChainTransform)


__all__ = ['vprescale', 'vprecenter', 'vpnormalize']


def vprescale(obj, tomax=1.):
    """Get the vispy transformation for rescaling objects.

    Args:
        obj: tuple
            The ndarray of the object to rescale. Must be a (..., 2) or
            (..., 3)

    Kargs:
        tomax: float, optional, (def: 1.)
            The final rescaling value.

    Returns:
        rescale: vispy.transformations
            The rescaling transformation.
    """
    # Get minimum / maximum trough last dimension :
    dim = tuple(np.arange(obj.ndim-1, dtype=int))
    ptp = np.max(obj, axis=dim) - np.min(obj, axis=dim)
    return STTransform(scale=[tomax / np.max(ptp)]*3)


def vprecenter(obj):
    """Get the vispy transformation to recenter objects.

    Args:
        obj: tuple
            The ndarray of the object to recenter. Must be a (..., 2) or
            (..., 3)

    Returns:
        recenter: vispy.transformations
            Vis py transformation to recenter object.
    """
    # Check object :
    if not isinstance(obj, np.ndarray) or obj.shape[-1] not in [2, 3]:
        raise ValueError("The object must be a ndarray of shape (..., 2) or "
                         "(..., 3)")
    # Get center :
    center = np.mean(obj, axis=tuple(np.arange(obj.ndim-1, dtype=int)))
    if center.shape[-1] == 2:
        center = np.hstack((center, 0.))
    # Build transformation :
    return STTransform(translate=-center)


def vpnormalize(obj, tomax=1.):
    """Get the vispy transformation for normalizing objects.

    Args:
        obj: tuple
            The ndarray of the object to rescale. Must be a (..., 2) or
            (..., 3)

    Kargs:
        tomax: float, optional, (def: 1.)
            The final rescaling value.

    Returns:
        normalize: vispy.transformations
            The normalize transformation.
    """
    # Prepare the transformatino chain :
    t = ChainTransform()
    # Recenter the object :
    t.prepend(vprecenter(obj))
    # Rescale :
    t.prepend(vprescale(obj, tomax))
    return t
