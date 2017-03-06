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

        # =========== HYPNOGRAM EDITION ===========
        # self._hypedit = HypnoEdition(self._hypCanvas.canvas, -self._hypno,
        #                              self._time, enable=True,
        #                              color=self._indicol,
        #                              parent=self._hypCanvas.wc.scene)


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
        # Find peaks (Max, Min) :
        M, m = peakdetect(data, time, int(lookahead))
        # Extract (x, y) coordinates for (Max, Min) peaks :
        xM, yM = zip(*M)
        xm, ym = zip(*m)
        # Array conversion :
        tM, yM, tm, ym = np.array(xM), np.array(yM), np.array(xm), np.array(ym)
        # Set data to markers :
        z = np.full_like(tM, -0.5)
        if display == 'max':
            pos = np.vstack((tM, yM, z)).T
        elif display == 'min':
            pos = np.vstack((tm, ym)).T
        elif display == 'minmax':
            pos = np.vstack((np.hstack((tm, tM)), np.hstack((ym, yM)))).T
        self.mesh.set_data(pos, size=self._size, edge_color=self._edgecol,
                           face_color=self._color, edge_width=self._edgewidth,
                           scaling=False)
        self.mesh.parent = parent
        self.mesh.update()


class HypnoEdition(object):
    """Hypnogram edition."""

    def __init__(self, canvas, hypno, time, enable=False, parent=None,
                 color='red'):
        """Init."""
        # Create a marker :
        self.color = color2vb(color)
        marker = scene.visuals.Markers(parent=parent)
        self.pos = np.array([])
        tM = time.max()

        @canvas.events.mouse_release.connect
        def on_mouse_release(event):
            """Executed function when the mouse is pressed over canvas.

            :event: the trigger event
            """
            pass

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over canvas.

            :event: the trigger event
            """
            self.pos = _get_cursor(event.pos)
            self.color = np.vstack((color2vb('green'), self.color))

        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            """Executed function when the mouse move over canvas.

            :event: the trigger event
            """
            marker.set_data(pos=_get_cursor(event.pos), face_color=self.color)

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            """Executed function when single click mouse over canvas.

            :event: the trigger event
            """
            # Find the closest marker (if possible) :
            cursor = _get_cursor(event.pos)
            dist = np.mean(self.pos - cursor[-1, :].T, axis=0)
            temp = self.pos - cursor[-1, :]
            print(dist, temp.shape)

        def _get_cursor(pos):
            # Get cursor position :
            cursor = tM * pos[0] / canvas.size[0]
            # Find hypnogram value for this position :
            idx = np.abs(time - cursor).argmin()
            # Set to marker position :
            pos = np.array([cursor, hypno[idx], -1.])[np.newaxis, ...]
            return np.vstack((self.pos, pos)) if self.pos.size else pos
