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
        self._hypedit = HypnoEdition(self._hypCanvas.canvas, -self._hypno,
                                     self._time, enable=True,
                                     color=self._indicol,
                                     parent=self._hypCanvas.wc.scene)


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
        # Transient detection :
        tr = np.nonzero(np.abs(hypno[:-1] - hypno[1:]))[0] + 1
        # Predefined positions :
        self.pos = np.array([time[tr], hypno[tr], np.full_like(tr, -1.)]).T
        self.color_cursor = color2vb('red')
        self.color_static = color2vb('blue')
        self.color_close = color2vb('green')
        self.color = color2vb('blue', length=self.pos.shape[0])
        # Create a marker :
        marker = scene.visuals.Markers(parent=parent)
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
            self.pos = np.vstack((self.pos, self._cpos))
            self.color = np.vstack((self.color, self.color_static))

        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            """Executed function when the mouse move over canvas.

            :event: the trigger event
            """
            # Get cursor position :
            cpos = _get_cursor(event.pos)
            color, _ = _get_close_marker(cpos)
            # Stack all pos and color :
            pos = np.vstack((self.pos, cpos)) if self.pos.size else cpos
            color = np.vstack((color, self.color_cursor))
            # Set new data to marker :
            marker.set_data(pos=pos, face_color=color)
            # Save current position :
            self._cpos = cpos

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            """Executed function when single click mouse over canvas.

            :event: the trigger event
            """
            pass
            # # Find the closest marker (if possible) :
            # cpos = _get_cursor(event.pos)
            # dist = self.pos[:, 0] - cpos[:, 0]
            # temp = self.pos - cpos
            # print(dist, temp.shape)

        def _get_cursor(pos):
            # Get cursor position :
            cursor = tM * pos[0] / canvas.size[0]
            # Find hypnogram value for this position :
            idx = np.abs(time - cursor).argmin()
            # Set to marker position :
            pos = np.array([cursor, hypno[idx], -1.])[np.newaxis, ...]
            return pos

        def _get_close_marker(cursor, dist=10.):
            """Get close marker from the cursor."""
            color = self.color.copy()
            l = np.abs(self.pos[:, 0] - cursor[:, 0])
            under = l <= dist
            if any(under):
                idx = l.argmin()
                color[l.argmin(), :] = self.color_close
                return color, idx
            else:
                return self.color, None
