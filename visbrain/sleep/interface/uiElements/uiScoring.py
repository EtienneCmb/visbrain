"""Main class for settings managment."""
import numpy as np

from ....utils import transient

__all__ = ['uiScoring']


class uiScoring(object):
    """"""

    def __init__(self):
        """Init."""
        pass

    def _fcn_scoreUpdate(self):
        """Update table with hypno data."""
        # Find transients :
        _, tr, stages = transient(self._hypno, self._time)