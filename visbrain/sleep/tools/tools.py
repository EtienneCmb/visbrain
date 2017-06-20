"""Set of tools for sleep data."""

import numpy as np

from ...utils import color2vb, transient

__all__ = ["Tools"]


class Tools(object):
    """docstring for Tools."""

    def __init__(self):
        """Init."""
        # =========== HYPNOGRAM EDITION ===========
        yaxis = (self._hypcam.rect.bottom, self._hypcam.rect.top)
        if self._enabhypedit:
            self._hypedit = HypnoEdition(self._sf, self._hyp, -self._hypno,
                                         self._time, self._hypCanvas.canvas,
                                         yaxis, enable=True,
                                         fcn=[self._fcn_infoUpdate,
                                              self._fcn_Hypno2Score])


class MouseEmulation(object):

    def __init__(self):
        """Init."""
        self.pos = (0, 0)


class HypnoEdition(object):
    """Hypnogram edition.

    Args:
        sf: float
            The sampling frequency.

        hypno_obj: Hypnogram
            The hypnogram object.

        data: np.ndarray
            Hypnogram data.

        canvas: AxisCanvas.canvas
            The canvas on which mouse will be active.

        yaxis: tuple
            Tuple describing where y-axis of the hypnogram start and finish.

    Kargs:
        enable: bool, optional, (def: False)
            Enable editing.

        color_cursor: string/tuple, optional, (def: 'red')
            Color of the traveling cursor.

        color_static: string/tuple, optional, (def: 'gray')
            Color of defined markers.

        color_active: string/tuple, optional, (def: 'green')
            Color of active marker.

        color_dragge: string/tuple, optional, (def: 'blue')
            Color of dragged marker.

        size: float, optional, (def: 9.)
            Marker size.

        fcn: list, optional, (def: None)
            List of executed function on mouse released. This is usefull to
            update stats info or editing table.
    """

    def __init__(self, sf, hypno_obj, data, time, canvas, yaxis, enable=False,
                 parent=None, color_cursor='red', color_static='gray',
                 color_active='green', color_dragge='blue', size=6.,
                 fcn=None):
        """Init."""
        # =================== MOUSE FUNCTIONS ===================
        @canvas.events.mouse_release.connect
        def on_mouse_release(event):
            """Executed function when mouse button is released.

            When the user release the mouse button, the current selected marker
            have to be deselect.
            """
            # Stop dragging point :
            self.keep = False
            _ = [k() for k in fcn]

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over canvas.

            Double clicking on the hypnogram canvas add a marker inplace.
            """
            self.pos = np.vstack((self.pos, self._cpos))
            self.color = np.vstack((self.color, self.color_static))

        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            """Executed function when the mouse move over canvas.

            When the mouse is moved, here's the accomplished steps :
                - Get cursor position
                - Get if a marker is under dist (and turn it color_active)
                - If user is curently pressing left mouse button, drag the
                point (only along y-axis). Then, drag point point and hypno too
                - Set data to marker object.
            """
            # Get latest data version :
            data = -hypno_obj.GUI2hyp()
            # Get cursor position :
            cpos = _get_cursor(event.pos, not self.keep)
            # Get closest marker :
            color, idx = _get_close_marker(event)
            # On marker moving :
            if self.keep:
                # Get a color backup :
                cbackup = self.color.copy()
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
                # Move cursor only if xprev <= x < xnext and if -4 <= y <= 1:
                if all([cpos[0, 0] >= xprev,  cpos[0, 0] <= xnext,
                       cpos[0, 1] <= 1, cpos[0, 1] >= -4]):
                    # Force to be on the grid :
                    cpos[0, 1] = float(round(cpos[0, 1]))
                    # Update position :
                    self.pos[self.keep_idx, 1] = cpos[0, 1]
                    # Send data non-converted marker :
                    hypno_obj.edit.set_data(pos=self.pos, edge_width=1.,
                                            face_color=cbackup, size=size,
                                            edge_color='white')
                    # Stream inv-converted hypno data :
                    posh = self.pos.copy()
                    posh[self.keep_idx, 1] = hypno_obj.pos2GUIinv(cpos)[0, 1]
                    xtpos = np.abs(time-posh[self.keep_idx, 0]).argmin()
                    data[xtpos:xtnext+1] = cpos[0, 1]
                    hypno_obj.set_data(sf, -data, time)
                    # Temporaly turn dragged point to color_dragge :
                    cbackup[self.keep_idx, :] = self.color_dragge
                    self.pos[self.keep_idx, 1] = hypno_obj.pos2GUI(cpos)[0, 1]
            else:
                cpos = self.convert(cpos)
                # Display moving point :
                if idx is None:
                    # Stack all pos and color :
                    pos = np.vstack((self.pos, cpos))
                    color = np.vstack((color, self.color_cursor))
                # If cursor close to marker, hide it and set to color_active :
                else:
                    pos = self.pos
                    # pos = hypno_obj.pos2GUI(self.pos)
                # Convert position :
                # Set new data to marker :
                hypno_obj.edit.set_data(pos=pos, face_color=color, size=size,
                                        edge_width=1., edge_color='white')
                # Save current position :
                self._cpos = cpos

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            """Executed function when single click mouse over canvas.

            When the user click on the canvas, a point will be selected but
            only if the distance is <= 10.
            """
            # Get closest marker :
            _, idx = _get_close_marker(event)
            self.keep = idx is not None
            self.keep_idx = idx

        def _get_cursor(pos, force=True):
            """Get the cursor position.

            Arg:
                pos: tuple
                    The position of the mouse (in pixel coordinates)

            Kargs:
                force: bool, optional, (def: True)
                    Force the returned mouse cursor position to fit to the
                    hypnogram values.

            Return:
                pos: np.ndarray
                    The mouse position converted in canvas unit
                    (i.e. time, hypno -1.).
            """
            # Get latest time :
            tm, tM = time_update()
            # Get cursor position :
            cursor = tm + ((tM - tm) * pos[0] / canvas.size[0])
            # Get y position :
            if force:
                # Force cursor to be on the hypnogram :
                val = -hypno_obj.GUI2hyp()[np.abs(time - cursor).argmin()]
            else:
                # Return converted y axis :
                val = (yaxis[0]-yaxis[1]) * pos[1] / canvas.size[1] + yaxis[1]
            # Set to marker position :
            pos = np.array([cursor, val, -1.])[np.newaxis, ...]

            return pos

        def _get_close_marker(event, perc=1.):
            """Get closest marker from the cursor.

            Arg:
                event: mouse.event
                    Mouse event.

            Kargs:
                perc: float, optional, (def: .1)
                    The distance under which the point is selected (in time
                    length percentage).

            Returns:
                color: np.ndarray
                    The array of new color (with color_active in case of
                    selected point).

                idx: int/None
                    The index of the closest marker (or None if no marker
                    position is under dist).
            """
            # Get latest time :
            tm, tM = time_update()
            dist = perc * (tM - tm) / 100
            # Get cursor (x, y) converted :
            cursor = _get_cursor(event.pos, force=False)
            color = self.color.copy()
            # Get distance between all markers and cursor :
            l = np.abs(np.square(self.pos - cursor).mean(1))
            # Select points under dist :
            under = l <= dist
            if any(under):
                idx = l.argmin()
                # Ignore first and last points of hypnogram :
                if idx not in (0, 1):
                    color[idx, :] = self.color_active
                    return color, idx
                else:
                    return self.color, None
            else:
                return self.color, None

        self._call = on_mouse_move

        # =================== UTILS FUNCTIONS ===================
        def data_update(hypno_obj):
            """Get latest data version."""
            data = -hypno_obj.GUI2hyp()
            time = hypno_obj.mesh.pos[hypno_obj.sl, 0]
            return data, time

        def time_update():
            """Get time extreme."""
            tm = hypno_obj._camera.rect.left
            tM = hypno_obj._camera.rect.right
            return tm, tM

        # =================== VARIABLES ===================
        self.event = MouseEmulation()

        # ============ MARKERS POSITION ============
        self.convert = hypno_obj.pos2GUI
        self._transient(data, time)

        # ============ COLOR ============
        self.color_cursor = color2vb(color_cursor)
        self.color_static = color2vb(color_static)
        self.color_active = color2vb(color_active)
        self.color_dragge = color2vb(color_dragge)
        self.color = color2vb(color_static, length=self.pos.shape[0])

        # ============ VARIABLES ============
        if fcn is None:
            def fcnt(): pass
            fcn = [fcnt]
        self.keep = False
        self.keep_idx = -1
        self.stidx = 0
        self.size = size

        # Update :
        self.update()

    # =================== TRANSIENT DETECTION ===================
    def _transient(self, data, time):
        """Perform a transient detection on hypnogram.

        This function is runned only on start to find if there's already
        predifined markers.

        Args:
            data: np.ndarray
                The hypnogram data.

            time: np.ndarray
                The time vector.
        """
        # Transient detection :
        tr = transient(data, time)[0] + 1
        # tr = np.append(tr, tr + 1)
        tr = np.array([0, len(data)-1] + list(tr))
        # Predefined positions :
        self.pos = np.array([time[tr], data[tr], np.full_like(tr, -1.)]).T
        self.pos = self.convert(self.pos)

    def update(self):
        """Update markers."""
        # Simulate a mouse movement :
        self._call(self.event)
