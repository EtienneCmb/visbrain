"""VisPy canvas initialization."""
import numpy as np
from PyQt5 import QtWidgets
from warnings import warn

import vispy.scene.cameras as viscam
from vispy import app

from ..gui import Ui_MainWindow
from visbrain.objects import VisbrainCanvas


class GridShortcuts(object):
    """Add shortcuts to grid canvas.

    Parameters
    ----------
    canvas : vispy canvas
        Vispy canvas to add the shortcuts.
    """

    def __init__(self, canvas):
        """Init."""
        self._sh_grid = [('Double click (grid canvas)', "Enlarge signal "
                          "under the mouse cursor"),
                         ]

        @canvas.events.key_press.connect
        def on_key_press(event):
            """Executed function when a key is pressed."""
            pass

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over canvas."""
            n_rows, n_cols = self._grid.g_size
            rect = self._grid_canvas.camera.rect
            w_cols, w_rows = self._grid_canvas.canvas.size
            # Get camera limits :
            bottom, height = rect.bottom, rect.height
            left, width = rect.left, rect.width
            x, y = event.pos
            # Pass in the camera system [-1, 1]:
            x_cam = (width * (x / w_cols) + left) + 1.
            y_cam = (height * ((w_rows - y) / w_rows) + bottom) + 1.
            # Get signal location :
            x_loc = int(np.ceil((n_cols / 2.) * x_cam) - 1.)
            y_loc = int(n_rows - np.ceil((n_rows / 2.) * y_cam))
            y_loc, x_loc = self._grid._convert_row_cols(y_loc, x_loc)
            # String conversion :
            if self._data.ndim == 2:
                lst = [str(x_loc)]
            elif self._data.ndim == 3:
                lst = [str(y_loc), str(x_loc)]
            lst.insert(self._signal._axis, ':')
            st = '(' + ', '.join(lst) + ')'
            # Try to set the signal
            try:
                # Get signal index :
                index = self._signal._get_signal_index(st)
                self._safely_set_index(index, True, True)
                if not self.actionSignal.isChecked():
                    self.actionSignal.setChecked(True)
                    self._fcn_menu_disp_signal()
            except:
                warn("No signal found at this position.")


class SignalShortcuts(object):
    """Add shortcuts to grid canvas.

    Parameters
    ----------
    canvas : vispy canvas
        Vispy canvas to add the shortcuts.
    """

    def __init__(self, canvas):
        """Init."""
        self._sh_sig = [('n (signal canvas)', 'Go to the next signal'),
                        ('b (signal canvas)', 'Go to the previous signal'),
                        ('Double click (signal canvas)', 'Insert annotation'),
                        ('g', 'Display / hide grid'),
                        ('s', 'Display / hide signal'),
                        ('<delete>', 'Reset the camera'),
                        ('CTRL + t', 'Display shortcuts'),
                        ('CTRL + d', 'Display / hide setting panel'),
                        ('CTRL + n', 'Take a screenshot'),
                        ('CTRL + q', 'Close Sleep graphical interface'),
                        ]

        @canvas.events.key_press.connect
        def on_key_press(event):
            """Executed function when a key is pressed."""
            if event.text.lower() == 'n':
                self._fcn_next_index()
            elif event.text.lower() == 'b':
                self._fcn_prev_index()

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over canvas."""
            # Get event position and camera rectangle:
            x_pos, y_pos = event.pos
            rect = self._signal_canvas.camera.rect
            # Get right padding, canvas, title and wc size :
            cs = canvas.size
            ws = self._signal_canvas.wc.size
            rpad = self._signal_canvas._rpad.size[0]
            ts = self._signal_canvas._titleObj.size[1]
            # From x-pos, remove offset du to y-label and ticks :
            x_pos -= cs[0] - (ws[0] + rpad)
            # From y-pos, remove offset du to title :
            y_pos -= ts
            # Get position only if double-click inside the widget :
            if (x_pos >= 0) and (y_pos >= 0):
                # Get time :
                t_diff = rect.right - rect.left
                t = (t_diff * x_pos / ws[0]) + rect.left
                # Get amplitude :
                d_diff = rect.top - rect.bottom
                d = rect.top - (d_diff * y_pos / ws[1])
                # Take only two decimals :
                t, d = np.around((t, d), decimals=2)
            # Add annotation :
            self._annotate_event(str(self._signal), (t, d))


class UiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas):
    """docstring for UiInit."""

    def __init__(self, **kwargs):
        """Init."""
        # Create the main window :
        super(UiInit, self).__init__(None)
        self.setupUi(self)

        # Cameras :
        grid_rect = (0, 0, 1, 1)
        cb_rect = (-.05, -2, .8, 4.)
        cam_signal = viscam.PanZoomCamera()
        cam_grid = viscam.PanZoomCamera(rect=grid_rect)
        cam_cbar = viscam.PanZoomCamera(rect=cb_rect)

        # Canvas creation :
        cargs = {'size': (800, 600)}
        self._grid_canvas = VisbrainCanvas(axis=False, name='Grid',
                                           cargs=cargs, camera=cam_grid,
                                           **kwargs)
        self._signal_canvas = VisbrainCanvas(axis=True, name='Signal',
                                             cargs=cargs, add_cbar=True,
                                             camera=cam_signal, **kwargs)
        self._signal_canvas.wc_cbar.camera = cam_cbar

        # Add canvas to layout :
        self._GridLayout.addWidget(self._grid_canvas.canvas.native)
        self._SignalLayout.addWidget(self._signal_canvas.canvas.native)

        # Initialize shortcuts :
        GridShortcuts.__init__(self, self._grid_canvas.canvas)
        SignalShortcuts.__init__(self, self._signal_canvas.canvas)
