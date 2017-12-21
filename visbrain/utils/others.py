"""This script contains some other utility functions."""
import logging

import numpy as np
from vispy.util import profiler


__all__ = ('Profiler', 'get_dsf', 'set_if_not_none')


class Profiler(object):
    """Visbrain profiler.

    The visbrain profiler add some basic functionalities to the vispy profiler.
    """

    def __init__(self, delayed=True):
        """Init."""
        self._delayed = delayed
        logger = logging.getLogger('visbrain')
        enable = logger.level == 1  # enable for PROFILER
        if enable and not hasattr(self, '_vp_profiler'):
            self._vp_profiler = profiler.Profiler(disabled=not enable,
                                                  delayed=self._delayed)

    def __bool__(self):
        """Return if the profiler is enable."""
        if hasattr(self, '_vp_profiler'):
            return not isinstance(self._vp_profiler,
                                  profiler.Profiler.DisabledProfiler)
        else:
            return False

    def __call__(self, msg=None, level=0, as_type='msg'):
        """Call the vispy profiler."""
        self.__init__(delayed=self._delayed)
        if self:
            if as_type == 'msg':
                if isinstance(msg, str) and isinstance(level, int):
                    msg = '    ' * level + '> ' + msg
                self._vp_profiler(self._new_msg(msg))
            elif as_type == 'title':
                depth = type(self._vp_profiler)._depth
                msg = "  " * depth + '-' * 6 + ' ' + msg + ' ' + '-' * 6
                self._vp_profiler._new_msg(self._new_msg(msg))

    def finish(self, msg=None):
        """Finish the profiler."""
        self._vp_profiler.finish(msg)

    @staticmethod
    def _new_msg(msg):
        msg += ' ' if msg[-1] != ' ' else ''
        return msg


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
