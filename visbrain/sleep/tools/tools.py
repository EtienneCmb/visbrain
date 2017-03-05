"""Set of tools for sleep data."""

import numpy as np

from vispy import scene

from ...utils import peakdetect, color2vb

__all__ = ["Tools"]


class Tools(object):
    """docstring for Tools."""

    def __init__(self):
        """Init."""
        # =========== PEAK DETECTION ===========
        self._peak = PeakDetection(color=self._indicol)


class PeakDetection(object):
    """docstring for Tools."""

    def __init__(self, color='red', size=7.):
        """Init."""
        self._color = color2vb(color)
        self._edgecol = 'white'
        self._edgewidth = 0
        self._size = size
        # Create a set of empty markers :
        self.mesh = scene.visuals.Markers(pos=np.zeros((2, 2)))
        self.mesh.set_gl_state('translucent')

    def set_data(self, data, time, display='max', lookahead=10, parent=None):
        """Find peaks according to data.

        Args:
            data: np.ndarray
                The data to find peaks. Must be a row vector

            time: np.ndarray
                The time vector.

        Kargs:
            display: string, optional, (def: 'max')
                Display either max peaks ('max'), min peaks ('min') or min and
                max 'minmax'.

            lookahead: float, optional, (def: 10.)
                Distance to look ahead from a peak candidate to determine if
                it is the actual peaks

            parent: vispy, optional, (def: None)
                The vispy scene for markers.
        """
        # Remove previous markers and re-create it :
        self.mesh.parent = None
        self.mesh = scene.visuals.Markers(pos=np.zeros((2, 2)))
        self.mesh.set_gl_state('translucent')
        # Find peaks (Max, Min) :
        M, m = peakdetect(data, time, int(lookahead))
        # Extract (x, y) coordinates for (Max, Min) peaks :
        xM, yM = zip(*M)
        xm, ym = zip(*m)
        # Array conversion :
        tM, yM, tm, ym = np.array(xM), np.array(yM), np.array(xm), np.array(ym)
        # Set data to markers :
        if display == 'max':
            pos = np.vstack((tM, yM)).T
        elif display == 'min':
            pos = np.vstack((tm, ym)).T
        elif display == 'minmax':
            pos = np.vstack((np.hstack((tm, tM)), np.hstack((ym, yM)))).T
        self.mesh.set_data(pos, size=self._size, edge_color=self._edgecol,
                           face_color=self._color, edge_width=self._edgewidth,
                           scaling=False)
        self.mesh.parent = parent
        self.mesh.update()
