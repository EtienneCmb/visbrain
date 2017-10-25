"""This script contains some other utility functions."""

import sys
import os
import logging

import numpy as np


__all__ = ('set_log_level', 'get_dsf', 'set_if_not_none', 'get_data_path')


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
    if verbose is None:
        verbose = "INFO"
    elif isinstance(verbose, bool):
        verbose = 'INFO' if verbose else 'WARNING'
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
