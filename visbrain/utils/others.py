"""This script contains some other utility functions."""

import sys
import os
from warnings import warn
import numpy as np

from vispy.geometry import MeshData

__all__ = ('vis_args', 'check_downsampling', 'vispy_array', 'convert_meshdata',
           'add_brain_template', 'remove_brain_template')


def vis_args(kw, prefix, ignore=[]):
    """Extract arguments that contain a prefix from a dictionary.

    Parameters
    ----------
    kw : dict
        The dictionary of arguments
    prefix : string
        The prefix to use (something like 'nd_', 'cb_'...)

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
        warn("Using a down-sampling frequency ("+str(dsbck)+"hz) that is not a"
             " multiple of the sampling frequency ("+str(sf)+"hz) is not "
             "recommanded."
             " A "+str(ds)+"hz will be used instead.")
    return ds
