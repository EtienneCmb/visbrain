"""Signal module."""
import os
import sip
import sys
from PyQt5 import QtWidgets
import numpy as np

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .ui_elements import UiElements, UiInit
from .visuals import Visuals
from ..utils import (set_widget_size, toggle_enable_tab, safely_set_cbox,
                     color2tuple)

sip.setdestroyonexit(False)

__all__ = ('Signal')


class Signal(UiInit, UiElements, Visuals):
    """Signal inspection module (data mining).

    The Signal module can be used to relatively large datasets of
    time-series. Two layout are provided :

    * Grid layout : visualize all of the signals into a grid.
    * Signal layout : visualize only one signal.

    Parameters
    ----------
    data : array_like
        Array of data of shape (N,),
    axis : int | -1
        Specify where is located the time axis in data. By default, the last
        axis is considered as the time axis (-1).
    time : array_like | None
        Time vector to use. If None, the time vector is inferred using the axis
        input.
    sf : float | 1.
        Sampling frequency.
    enable_grid : bool | True
        Enable or disable the grid. If False, the grid is not computed and not
        accessible from the GUI. The grid requires more memory RAM. It could be
        turn to False for very large datasets.
    form : {'line', 'marker', 'histogram'}
        Plotting type.
    color : array_like/string/tuple | 'black'
        Color of the plot.
    lw : float | 2.
        Line width (form='line').
    symbol : string | 'o'
        Marker symbol (form='marker').
    size : float | 10.
        Marker size (form='marker').
    nbins : int | 10
        Number of bins for the histogram (form='histogram')
    parent : VisPy.parent | None
        Parent of the mesh.
    title : string | None
        Title of the axis (signal layout).
    xlabel : string | None
        Label for the x-axis (signal layout).
    ylabel : string | None
        Label for the y-axis (signal layout).
    title_font_size : float | 15.
        Size of the title (signal layout).
    axis_font_size : float | 12.
        Size of x and y labels (signal layout).
    axis_color : array_like/string/tuple | 'black'
        Label, title, axis and border color (signal layout).
    tick_font_size : float | 8.
        Size of ticks for the x and y-axis (signal layout).
    bgcolor : array_like/tuple/string | 'black'
        Background color.
    display_grid : bool | True
        Display the grid layout.
    display_signal : bool | True
        Display the signal layout.
    annotations : str | None
        Path to an annotation file.
    """

    def __init__(self, data, axis=-1, time=None, sf=1., enable_grid=True,
                 form='line', color='black', lw=2., symbol='disc', size=10.,
                 nbins=10, display_grid=True, display_signal=True,
                 annotations=None, **kwargs):
        """Init."""
        self._enable_grid = enable_grid
        display_grid = bool(display_grid * self._enable_grid)

        # ==================== APP CREATION ====================
        self._app = QtWidgets.QApplication(sys.argv)
        UiInit.__init__(self, **kwargs)

        # ==================== DATA CHECKING ====================
        if isinstance(data, (list, tuple)):
            data = np.asarray(data)
        if not isinstance(data, np.ndarray) or (data.ndim > 3):
            raise TypeError("data must be an NumPy array with less than three "
                            "dimensions.")
        if data.ndim == 1 or not self._enable_grid:  # disable grid
            display_grid = self._enable_grid = False
            toggle_enable_tab(self.QuickSettings, 'Grid', False)
            self.actionGrid.setEnabled(False)
        self._data = data.astype(np.float32, copy=False)

        # ==================== VISUALS ====================
        grid_parent = self._grid_canvas.wc.scene
        signal_parent = self._signal_canvas.wc.scene
        Visuals.__init__(self, data, time, sf, axis, form, color, lw, symbol,
                         size, nbins, grid_parent, signal_parent)

        # ==================== CAMERA ====================
        grid_rect = (0, 0, 1, 1)  # self._grid.rect
        sig_rect = self._signal.rect
        self._grid_canvas.camera = viscam.PanZoomCamera(rect=grid_rect)
        self._signal_canvas.camera = viscam.PanZoomCamera(rect=sig_rect)

        # ==================== UI INIT ====================
        # ------------- Signal -------------
        # Signal and axis color :
        self._sig_color.setText(str(color2tuple(color, astype=float)))
        self._axis_color.setText(str(kwargs.get('axis_color', 'black')))
        # Title, labels and ticks :
        self._sig_title.setText(kwargs.get('title', ''))
        self._sig_title_fz.setValue(kwargs.get('title_font_size', 15.))
        self._sig_xlab.setText(kwargs.get('xlabel', ''))
        self._sig_ylab.setText(kwargs.get('ylabel', ''))
        self._sig_lab_fz.setValue(kwargs.get('axis_font_size', 12.))
        self._sig_ticks_fz.setValue(kwargs.get('tick_font_size', 8.))
        # Signal properties :
        safely_set_cbox(self._sig_form, form)
        self._sig_lw.setValue(lw)  # line
        self._sig_nbins.setValue(nbins)  # histogram
        self._sig_size.setValue(size)  # marker
        safely_set_cbox(self._sig_symbol, symbol)  # marker

        # ------------- Settings -------------
        bgcolor = kwargs.get('bgcolor', 'white')
        self._set_bgcolor.setText(str(color2tuple(bgcolor, astype=float)))

        # ------------- Menu -------------
        self.actionGrid.setChecked(display_grid)
        self.actionSignal.setChecked(display_signal)

        self._fcn_on_creation()

        # ==================== USER <-> GUI ====================
        UiElements.__init__(self, **kwargs)

        # ==================== SHORTCUTS ====================
        self._shpopup.set_shortcuts(self._sh_grid + self._sh_sig)

        # ------------- Annotations -------------
        if annotations is not None:
            assert os.path.isfile(annotations)
            self._fcn_load_annotations(filename=annotations)

    def _fcn_on_creation(self):
        """Run on GUI creation."""
        # Settings :
        self.QuickSettings.setCurrentIndex(0)
        set_widget_size(self._app, self.q_widget, 23)
        # Fix index limits :
        self._sig_index.setMinimum(0)
        self._sig_index.setMaximum(len(self._signal._navidx) - 1)
        # Fix amplitude limits :
        d_min, d_max = self._data.min(), self._data.max()
        step = (d_max - d_min) / 100.
        self._sig_amp_min.setMinimum(d_min)
        self._sig_amp_min.setMaximum(d_max)
        self._sig_amp_min.setValue(d_min)
        self._sig_amp_min.setSingleStep(step)
        self._sig_amp_max.setMinimum(d_min)
        self._sig_amp_max.setMaximum(d_max)
        self._sig_amp_max.setValue(d_max)
        self._sig_amp_max.setSingleStep(step)
        # Fix amplitude limits :
        self._sig_th_min.setMinimum(d_min)
        self._sig_th_min.setMaximum(d_max)
        self._sig_th_min.setValue(d_min)
        self._sig_th_min.setSingleStep(step)
        self._sig_th_max.setMinimum(d_min)
        self._sig_th_max.setMaximum(d_max)
        self._sig_th_max.setValue(d_max)
        self._sig_th_max.setSingleStep(step)
        # Display / hide grid and signal :
        self._fcn_menu_disp_grid()
        self._fcn_menu_disp_signal()
        # Set signal data :
        self._fcn_set_signal(force=True)
        # Update cameras :
        self.update_cameras()

    def update_cameras(self, g_rect=None, s_rect=None, update='both'):
        """Update cameras."""
        if update == 'both':
            update_grid = update_signal = True
        elif update == 'signal':
            update_grid, update_signal = False, True
        elif update == 'grid':
            update_grid, update_signal = True, False
        if update_grid and hasattr(self, '_grid'):  # Grid
            g_rect = self._grid.rect if g_rect is None else g_rect
            self._grid_canvas.camera.rect = g_rect
            self._grid_canvas.update()
            self._grid_canvas.set_default_state()
        if update_signal:  # Signal
            s_rect = self._signal.rect if s_rect is None else s_rect
            self._signal_canvas.camera.rect = s_rect
            self._signal_canvas.set_default_state()
            self._signal_canvas.update()

    def screenshot(self):
        """Take a screenshot of the scene."""
        pass

    def show(self):
        """Display the graphical user interface."""
        self.showMaximized()
        visapp.run()
