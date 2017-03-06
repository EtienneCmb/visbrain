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
        yaxis = (self._hypcam.rect.bottom, self._hypcam.rect.top)
        self._hypedit = HypnoEdition(self._sf, self._hyp,
                                     self._hypCanvas.canvas, -self._hypno,
                                     self._time, yaxis,
                                     enable=True, color=self._indicol,
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

    def set_data(self, data, time, marker, display='max', lookahead=10):
        """Find peaks according to data.

        Args:
            data: np.ndarray
                The data to find peaks. Must be a row vector

            time: np.ndarray
                The time vector.

            marker: vispy.scene.visuals.Markers
                The marker object to set data.

        Kargs:
            display: string, optional, (def: 'max')
                Display either max peaks ('max'), min peaks ('min') or min and
                max 'minmax'.

            lookahead: float, optional, (def: 10.)
                Distance to look ahead from a peak candidate to determine if
                it is the actual peaks
        """
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
        marker.set_data(pos, size=self._size, edge_color=self._edgecol,
                        face_color=self._color, edge_width=self._edgewidth,
                        scaling=False)
        marker.update()


class HypnoEdition(object):
    """Hypnogram edition."""

    def __init__(self, sf, hypno_obj, canvas, hypno, time, yaxis, enable=False,
                 parent=None, color='red'):
        """Init."""
        # ============ MARKERS POSITION ============
        self.transient(hypno, time)

        # ============ COLOR ============
        self.color_cursor = color2vb('red')
        self.color_static = color2vb('blue')
        self.color_close = color2vb('green')
        self.color = color2vb('blue', length=self.pos.shape[0])

        self.keep = False
        self.keep_idx = -1
        tM = time.max()

        @canvas.events.mouse_release.connect
        def on_mouse_release(event):
            """Executed function when the mouse is pressed over canvas.

            :event: the trigger event
            """
            if self.keep:
                self.transient(hypno, time)
                self.color = color2vb('blue', length=self.pos.shape[0])
            # Stop keeping point :
            self.keep = False

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
            cpos = _get_cursor(event.pos, not self.keep)
            # Get closest marker :
            color, _ = _get_close_marker(event)
            # On marker moving :
            if self.keep:
                # Get distance between cursor and markers :
                xpos = self.pos[:, 0] - cpos[0, 0]
                xpos_sorted = np.sort(xpos)
                # Find current position :
                xpos_z = np.where(xpos_sorted == xpos[self.keep_idx])[0]
                # Find previous / next marker position :
                xprev = self.pos[xpos == xpos_sorted[xpos_z-1], 0]
                xnext = self.pos[xpos == xpos_sorted[xpos_z+1], 0]
                # Find their position in the time vector :
                # xtprev = np.abs(time - xprev).argmin()
                xtnext = np.abs(time - xnext).argmin()
                # Move cursor only if xprev <= x < xnext :
                if (cpos[0, 0] >= xprev) and (cpos[0, 0] <= xnext):
                    # Force to be on the grid :
                    cpos[0, 1] = float(round(cpos[0, 1]))
                    # Update position :
                    self.pos[self.keep_idx, 1] = cpos[0, 1]
                    self.pos[xpos == xpos_sorted[xpos_z+1], 1] = cpos[0, 1]
                    # Stream hypno data :
                    xtpos = np.abs(time-self.pos[self.keep_idx, 0]).argmin()
                    hypno[xtpos:xtnext+1] = cpos[0, 1]
                    # hypno_obj.mesh.update()
                    hypno_obj.set_data(100., -hypno, time)
                    # Send data marker :
                    hypno_obj.edit.set_data(pos=self.pos,
                                            face_color=self.color,
                                            edge_width=0., size=10.)
            else:
                # Stack all pos and color :
                pos = np.vstack((self.pos, cpos)) if self.pos.size else cpos
                color = np.vstack((color, self.color_cursor))
                # Set new data to marker :
                hypno_obj.edit.set_data(pos=pos, face_color=color,
                                        edge_width=0., size=10.)
                # Save current position :
                self._cpos = cpos

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            """Executed function when single click mouse over canvas.

            :event: the trigger event
            """
            # Get closest marker :
            _, idx = _get_close_marker(event)
            self.keep = idx is not None
            self.keep_idx = idx

        def _get_cursor(pos, force=True):
            # Get cursor position :
            cursor = tM * pos[0] / canvas.size[0]
            # Get y position :
            if force:
                # Force cursor to be on the hypnogram :
                val = hypno[np.abs(time - cursor).argmin()]
            else:
                # Return converted y axis :
                val = (yaxis[0]-yaxis[1]) * pos[1] / canvas.size[1] + yaxis[1]
            # Set to marker position :
            pos = np.array([cursor, val, -1.])[np.newaxis, ...]
            return pos

        def _get_close_marker(event, dist=10.):
            """Get closest marker from the cursor."""
            # Get cursor (x, y) converted :
            cursor = _get_cursor(event.pos, force=False)
            color = self.color.copy()
            # Get distance between all markers and cursor :
            l = np.abs(np.square(self.pos - cursor).mean(1))
            # Color points under dist :
            under = l <= dist
            if any(under):
                idx = l.argmin()
                if idx not in (0, 1):
                    color[idx, :] = self.color_close
                    return color, idx
                else:
                    return self.color, None
            else:
                return self.color, None

    def transient(self, hypno, time):
        # Transient detection :
        tr = np.nonzero(np.abs(hypno[:-1] - hypno[1:]))[0] +1
        # tr = np.append(tr, tr + 1)
        tr = np.array([0, len(hypno)-1] + list(tr))
        # Predefined positions :
        self.pos = np.array([time[tr], hypno[tr], np.full_like(tr, -1.)]).T
