"""Signal module."""
import os
import numpy as np

import vispy.scene.cameras as viscam

from .ui_elements import UiElements, UiInit
from .visuals import Visuals
from ..utils import (safely_set_cbox, color2tuple, color2vb, mpl_cmap,
                     toggle_enable_tab)
from ..io import write_fig_canvas
from ..pyqt_module import PyQtModule
# get_screen_size


__all__ = ('Signal')


class Signal(PyQtModule, UiInit, UiElements, Visuals):
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
    form : {'line', 'marker', 'histogram', 'tf', 'psd', 'butterfly'}
        Plotting type.
    color : array_like/string/tuple | 'black'
        Color of the plot.
    line_lw : float | 1.
        Line width (form in ['line', 'psd', 'butterfly']).
    line_smooth : bool | False
        Specify if grid lines have to be smoothed. might be unstable on some
        platform.
    marker_symbol : string | 'o'
        Marker symbol.
    marker_size : float | 10.
        Marker size.
    hist_nbins : int | 10
        Number of bins for the histogram.
    tf_norm : int | 0
        Time-frequency normalization. If tf_baseline is not defined, the mean
        and deviation are deduced using the entire trial. Use :

            * 0 : No normalization
            * 1 : Subtract the mean
            * 2 : Divide by the mean
            * 3 : Subtract then divide by the mean
            * 4 : Z-score
    tf_baseline : tuple | None
        Baseline to used for the normalization. Must be a tuple of two integers
        (starting, ending) time index.
    tf_interp : string | 'gaussian'
        Time-frequency interpolation method.
    tf_cmap : string | 'viridis'
        Time-frequency colormap.
    tf_av_window : int | None
        Length of the window to apply a time averaging.
    tf_av_overlap : float | 0.
        Overlap between successive time window. Default 0. means no overlap.
    tf_clim : tuple | None
        Colorbar limits to use for the tim-frequency map.
    psd_nperseg : int | 256
        Length of each segment (scipy.signal.welch).
    psd_noverlap : int | 128
        Number of points to overlap between segments (scipy.signal.welch).
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
    grid_lw : float | 1.
        Grid line width.
    grid_titles : list | None
        Titles do add to each plot in the grid. Sould be a list of length
        (n_rows * n_cols).
    grid_font_size : float | 10.
        Font size of grid titles.
    grid_color : string | 'random'
        Grid plot color. Use 'random' to have one random color per plot or
        use a string (e.g. 'gray') for a uniform color.
    grid_titles_color : array_like/string/tuple | 'black'
        Grid titles color.
    bgcolor : array_like/tuple/string | 'black'
        Background color.
    display_grid : bool | True
        Display the grid layout.
    display_signal : bool | True
        Display the signal layout.
    annotations : str | None
        Path to an annotation file.
    smooth_lines : bool | True
        Specify if grid lines have to be smoothed. might be unstable on some
        platform.
    """

    def __init__(self, data, axis=-1, time=None, sf=1., enable_grid=True,
                 form='line', color='black', line_lw=1., line_smooth=False,
                 marker_symbol='disc', marker_size=10., hist_nbins=10,
                 tf_norm=0, tf_baseline=None, tf_interp='gaussian',
                 tf_cmap='viridis', tf_av_window=None, tf_av_overlap=0.,
                 tf_clim=None, psd_nperseg=256, psd_noverlap=128,
                 display_grid=True, display_signal=True, annotations=None,
                 annot_txtsz=18., annot_marksz=16., annot_color='#2ecc71',
                 grid_lw=1., grid_smooth=False, grid_titles=None,
                 grid_font_size=10., grid_color='random', grid_shape=None,
                 grid_titles_color='black', verbose=None, **kwargs):
        """Init."""
        dscb = ['_grid_canvas.canvas.scene', '_signal_canvas.canvas.scene']
        PyQtModule.__init__(self, verbose=verbose, to_describe=dscb)
        self._enable_grid = enable_grid
        self._previous_form = form
        display_grid = bool(display_grid * self._enable_grid)

        # ==================== APP CREATION ====================
        UiInit.__init__(self, **kwargs)

        # ==================== DATA CHECKING ====================
        if isinstance(data, (list, tuple)):
            data = np.asarray(data)
        if not isinstance(data, np.ndarray) or (data.ndim > 3):
            raise TypeError("data must be an NumPy array with less than three "
                            "dimensions.")
        if data.ndim == 1 or not self._enable_grid:  # disable grid
            display_grid = self._enable_grid = False
            self.actionGrid.setEnabled(False)
            toggle_enable_tab(self.QuickSettings, 'Grid', False)
        self._data = data.astype(np.float32, copy=False)
        self._axis = axis

        # ==================== VISUALS ====================
        grid_parent = self._grid_canvas.wc.scene
        signal_parent = self._signal_canvas.wc.scene
        Visuals.__init__(self, data, time, sf, axis, grid_titles, grid_color,
                         grid_shape, grid_parent, signal_parent)

        # ==================== CAMERA ====================
        grid_rect = (0, 0, 1, 1)
        sig_rect = self._signal.rect
        cb_rect = (-.05, -2, .8, 4.)
        self._grid_canvas.camera = viscam.PanZoomCamera(rect=grid_rect)
        self._signal_canvas.camera = viscam.PanZoomCamera(rect=sig_rect)
        self._signal_canvas.wc_cbar.camera = viscam.PanZoomCamera(rect=cb_rect)

        # ==================== UI INIT ====================
        self._fix_elements_limits()
        # ------------- Signal -------------
        # Signal and axis color :
        self._sig_color.setText(str(color2tuple(color, astype=float)))
        ax_color = kwargs.get('axis_color', color2vb('black'))
        self._axis_color.setText(str(ax_color))
        # Title, labels and ticks :
        self._sig_title.setText(kwargs.get('title', ''))
        self._sig_title_fz.setValue(kwargs.get('title_font_size', 15.))
        self._sig_xlab.setText(kwargs.get('xlabel', ''))
        self._sig_ylab.setText(kwargs.get('ylabel', ''))
        self._sig_lab_fz.setValue(kwargs.get('axis_font_size', 12.))
        self._sig_ticks_fz.setValue(kwargs.get('tick_font_size', 8.))
        # Signal properties :
        safely_set_cbox(self._sig_form, form)
        self._sig_lw.setValue(line_lw)  # line
        self._sig_smooth.setChecked(line_smooth)  # line
        self._sig_nbins.setValue(hist_nbins)  # histogram
        self._sig_size.setValue(marker_size)  # marker
        safely_set_cbox(self._sig_symbol, marker_symbol)  # marker
        self._sig_norm.setCurrentIndex(tf_norm)
        safely_set_cbox(self._sig_tf_interp, tf_interp)
        self._sig_tf_rev.setChecked(bool(tf_cmap.find('_r') + 1))
        self._sig_tf_cmap.addItems(mpl_cmap())
        safely_set_cbox(self._sig_tf_cmap, tf_cmap.replace('_r', ''))
        if (tf_baseline is not None) and (len(tf_baseline) == 2):
            self._sig_baseline.setChecked(True)
            self._sig_base_start.setValue(tf_baseline[0])
            self._sig_base_end.setValue(tf_baseline[1])
        if isinstance(tf_av_window, int):
            self._sig_averaging.setChecked(True)
            self._sig_av_win.setValue(tf_av_window)
            self._sig_av_overlap.setValue(tf_av_overlap)
        if (tf_clim is not None) and (len(tf_clim) == 2):
            self._sig_tf_clim.setChecked(True)
            self._sig_climin.setValue(tf_clim[0])
            self._sig_climax.setValue(tf_clim[1])
        self._sig_nperseg.setValue(psd_nperseg)
        self._sig_noverlap.setValue(psd_noverlap)

        # ------------- Grid -------------
        if hasattr(self, '_grid'):
            n_rows, n_cols = self._grid.g_size
            self._grid_nrows.setValue(n_rows)
            self._grid_nrows.setMaximum(np.prod(self._grid.g_size))
            self._grid_ncols.setValue(n_cols)
            self._grid_ncols.setMaximum(np.prod(self._grid.g_size))
        gt_st = str(color2tuple(grid_titles_color, astype=float))
        self._grid_titles_fz.setValue(grid_font_size)
        self._grid_titles_color.setText(gt_st)
        self._grid_lw.setValue(grid_lw)

        # ------------- Cbar -------------
        self._signal_canvas.cbar.txtcolor = ax_color
        self._signal_canvas.cbar.border = False
        self._signal_canvas.cbar.cbtxtsz = 15.
        self._signal_canvas.cbar.txtsz = 12.

        # ------------- Settings -------------
        bgcolor = kwargs.get('bgcolor', 'white')
        self._set_bgcolor.setText(str(color2tuple(bgcolor, astype=float)))
        self._grid_smooth.setChecked(grid_smooth)

        # ------------- Annotations -------------
        self._annot_txtsz.setValue(annot_txtsz)
        self._annot_marksz.setValue(annot_marksz)
        self._annot_color.setText(str(color2tuple(annot_color, astype=float)))

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

    def __iter__(self):
        """Iterate over signal dimension."""
        for k in range(len(self._signal._navidx) - 1):
            yield k

    def _fix_elements_limits(self):
        """Fiw the upper and lower limits of some elements."""
        # Fix index limits :
        self._sig_index.setMinimum(0)
        self._sig_index.setMaximum(len(self._signal._navidx) - 1)
        # Fix amplitude limits :
        d_min, d_max = self._data.min(), self._data.max()
        step = (d_max - d_min) / 100.
        n = self._data.shape[self._axis]
        self._sig_amp_min.setMinimum(d_min)
        self._sig_amp_min.setMaximum(d_max)
        self._sig_amp_min.setValue(d_min)
        self._sig_amp_min.setSingleStep(step)
        self._sig_amp_max.setMinimum(d_min)
        self._sig_amp_max.setMaximum(d_max)
        self._sig_amp_max.setValue(d_max)
        self._sig_amp_max.setSingleStep(step)
        self._sig_av_win.setMaximum(n)
        self._sig_base_start.setMaximum(n)
        self._sig_base_end.setMaximum(n)
        # Fix amplitude limits :
        self._sig_th_min.setMinimum(d_min)
        self._sig_th_min.setMaximum(d_max)
        self._sig_th_min.setValue(d_min)
        self._sig_th_min.setSingleStep(step)
        self._sig_th_max.setMinimum(d_min)
        self._sig_th_max.setMaximum(d_max)
        self._sig_th_max.setValue(d_max)
        self._sig_th_max.setSingleStep(step)

    def _fcn_on_creation(self):
        """Run on GUI creation."""
        # Fix proportion of canvas :
        # w, g = get_screen_size(self._app)
        # self._signal_canvas.wc.width_max = w / 2
        # self._grid_canvas.wc.width_max = w / 2
        # Display / hide grid and signal :
        self._fcn_menu_disp_grid()
        self._fcn_menu_disp_signal()
        # Grid properties :
        self._fcn_grid_tupdate()
        self._fcn_grid_lw()
        # Set signal data :
        self._fcn_set_signal(force=True)
        self._fcn_sig_smooth()
        # Annotations :
        self._fcn_annot_appear()
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

    def screenshot(self, filename='screenshot.png', canvas='signal',
                   autocrop=False, region=None, print_size=None,
                   unit='centimeter', dpi=300., factor=1., bgcolor=None,
                   transparent=False):
        """Take a screenshot of the scene.

        Parameters
        ----------
        filename : string | 'screenshot.png'
            Name and path of the screenshot file.
        canvas : {'signal', 'grid'}
            Canvas to capture.
        autocrop : bool | False
            Auto-cropping argument to remove useless space.
        region : tuple/list | None
            The region to export (x_start, y_start, width, height).
        print_size : tuple | None
            The desired print size. This argument should be used in association
            with the dpi and unit inputs. print_size describe should be a tuple
            of two floats describing (width, height) of the exported image for
            a specific dpi level. The final image might not have the exact
            desired size but will try instead to find a compromize
            regarding to the proportion of width/height of the original image.
        unit : {'centimeter', 'millimeter', 'pixel', 'inch'}
            Unit of the printed size.
        dpi : float | 300.
            Dots per inch for printing the image.
        factor : float | None
            If you don't want to use the print_size input, factor simply
            multiply the resolution of your screen.
        bgcolor : array_like/string | None
            Background color of the canvas.
        transparent : bool | False
            Use transparent background.
        """
        if canvas == 'signal':
            c, w = self._signal_canvas.canvas, self._SignalWidget
        elif canvas == 'grid':
            c, w = self._grid_canvas.canvas, self._GridWidget
        write_fig_canvas(filename, c, w, autocrop, region, print_size, unit,
                         dpi, factor, bgcolor, transparent)

    def set_xlim(self, xstart, xend):
        """Fix limits of the x-axis.

        Parameters
        ----------
        xstart : float
            Starting point of the x-axis.
        xend : float
            Ending point of the x-axis
        """
        self._signal_canvas.camera.rect.left = xstart
        self._signal_canvas.camera.rect.right = xend
        self._signal_canvas.update()

    def set_ylim(self, ystart, yend):
        """Fix limits of the y-axis.

        Parameters
        ----------
        ystart : float
            Starting point of the y-axis.
        yend : float
            Ending point of the y-axis
        """
        self._signal_canvas.camera.rect.bottom = ystart
        self._signal_canvas.camera.rect.top = yend
        self._signal_canvas.update()

    def set_signal_index(self, index):
        """Set the index of the signal."""
        self._safely_set_index(index, True, True)

    def set_signal_form(self, form='line'):
        """Set plotting method.

        Parameters
        ----------
        form : {'line', 'marker', 'histogram', 'tf', 'psd', 'butterfly'}
            Plotting form.
        """
        idx = ['line', 'marker', 'histogram', 'tf', 'psd',
               'butterfly'].index(form)
        self._sig_form.setCurrentIndex(idx)
