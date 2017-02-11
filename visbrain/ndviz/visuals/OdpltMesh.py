"""This script contains the main class for 1D plotting."""

import numpy as np

from vispy import scene, visuals
import vispy.visuals.transforms as vist

from ...utils import type_coloring

# Create a visual node :
Line = scene.visuals.create_visual_node(visuals.LinePlotVisual)

__all__ = ['OdpltMesh']


class OdpltMesh(object):
    """Create a 1D object.

    Args:
        data: ndarray
            The array to use

        sf: float
            The sampling frequency

    Kargs:
        axis: tuple/list/array, optional, (def: None)
            The axis parameter must contains two integers. The first one refer
            to the location of the time axis. All the points over this axis
            are going to be selected. The second one refer to the axis along
            which selecting the data.

        index: int, optional, (def: 0)
            The index along axis[1] for selecting the data.

        xtype: string, optional, (def: None)
            How to consider the x-axis. Use None for the default, 'time' to get
            a time scale.
    """

    def __init__(self, data, sf, axis=None, index=0, plot='line', xtype=None,
                 color='uniform', rnd_dyn=(0.3, 0.9), cmap='viridis',
                 clim=None, vmin=None, under=None, vmax=None, over=None,
                 unicolor='white', bins=10, nfft=256, step=128, **kwargs):
        """Init."""
        # User inputs :
        self._data = np.array(data, dtype=float)
        self._sf = float(sf)
        self._axis = axis
        self._plot = plot
        self._index = index
        self._color = color
        self._xtype = xtype
        self._bins = bins
        self._xlab, self._ylab = '', ''
        self._color, self._rnd_dyn, self._unicolor = color, rnd_dyn, unicolor
        self._cmap, self._clim, self._vmin, self._vmax = cmap, clim, vmin, vmax
        self._under, self._over = under, over
        self._nfft, self._step = nfft, step
        self._kwargs = kwargs

        # Variables :
        self._l = 0
        self._col = 'white'
        self._viz = [True, False, False]

        # Create a default Line, Histogram and spectrogram :
        self._line = Line([0, 1])
        self._hist = scene.visuals.Histogram([0])
        self._imag = scene.visuals.Image(np.random.rand(2, 2))

        self._obj_visible()

        # Check data :
        self.update()

    # ========================================================================
    # SET FUNCTIONS
    # ========================================================================
    def set_data(self, data, axis=None, index=0):
        """Set some data.

        Args:
            data: ndarray
                The array to use

        Kargs:
            axis: tuple/list/array, optional, (def: None)
                The axis parameter must contains two integers. The first one
                refer to the location of the time axis. All the points over
                this axis are going to be selected. The second one refer to the
                axis along which selecting the data.

            index: int, optional, (def: 0)
                The index along axis[1] for selecting the data.
        """
        self._data, self._axis, self._index = data, axis, index
        self.update()

    def set_type(self, plot='line', bins=10, nfft=256, step=128, **kwargs):
        """Set the plot type."""
        self._plot = plot
        self._bins = bins
        self._nfft, self._step = nfft, step

        # Update data and color :
        self.update()

        # Manage visible object :
        self._viz = [plot is k for k in ['line', 'histogram', 'spectrogram']]
        self._obj_visible()

    def set_color(self, color='uniform', rnd_dyn=(0.3, 0.9), cmap='viridis',
                  clim=None, vmin=None, under=None, vmax=None, over=None,
                  unicolor='white'):
        """Set new color parameter to the data.

        Dynamic coloring are only avaible for line type plot but all of the
        static color type can be applied either on line or histogram. The
        spectrogram colormap is fixed to 'viridis'.

        Kargs:
            color: string/tuple/array, optional, (def: 'uniform')
                Choose how to color signals. Use None (or 'rnd', 'random') to
                generate random colors. Use 'uniform' (see the unicolor
                parameter) to define the same color for all signals. Use
                'dyn_time' to have a dynamic color according to the time index.
                This is particulary convenient to inspect real time signals
                (see play parameter). Use 'dyn_minmax' to a color code acording
                to the dynamic of the signal. This option can be used to detect
                extrema and can be futher controled using colormap parameters
                (cmap, clim, vmin, vmax, under and over).

            rnd_dyn: tuple, optional, (def: (.3, .9))
                Define the dynamic of random color. This parameter is active
                only if the color parameter is turned to None (or 'rnd' /
                'random').

            cmap: string, optional, (def: inferno)
                Matplotlib colormap (parameter active for 'dyn_minmax' and
                'dyn_time' color).

            clim: tuple/list, optional, (def: None)
                Limit of the colormap. The clim parameter must be a tuple /
                list of two float number each one describing respectively the
                (min, max) of the colormap. Every values under clim[0] or over
                clim[1] will peaked (parameter active for 'dyn_minmax' and
                'dyn_time' color).

            alpha: float, optional, (def: 1.0)
                The opacity to use. The alpha parameter must be between 0 and 1
                (parameter active for 'dyn_minmax' and 'dyn_time' color).

            vmin: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the under parameter bellow (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            under: tuple/string, optional, (def: 'gray')
                Matplotlib color for values under vmin (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            vmax: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the over parameter bellow (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            over: tuple/string, optional, (def: 'red')
                Matplotlib color for values over vmax (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            unicolor: tuple/string, optional, (def: 'white')
                The color to use in case of uniform color.
        """
        # Get inputs arguments :
        self._color, self._rnd_dyn, self._unicolor = color, rnd_dyn, unicolor
        self._cmap, self._clim, self._vmin, self._vmax = cmap, clim, vmin, vmax
        self._under, self._over = under, over
        # Check color :
        self.update()

    def update(self):
        """Update plotting."""
        # Check arguments :
        self._check_data()
        self._check_color()

        # Set data and color :
        self._set_data()

    # ========================================================================
    # SET SUB-FUNCTIONS
    # ========================================================================
    def _set_data(self):
        """Set data according to plot type."""
        # --------------------------------------------------------------------
        # LINE :
        if self._plot is 'line':
            # First visible object :
            self._viz = [True, False, False]
            # Set the data :
            self._line.set_data(np.vstack((self._xvec, self._rowdata)).T,
                                color=self._col, symbol=None, **self._kwargs)
            self._xlab, self._ylab = None, None
            # Update object :
            self._line.update()

        # --------------------------------------------------------------------
        # HISTOGRAM :
        elif self._plot is 'histogram':
            # First visible object :
            self._viz = [False, True, False]
            # Compute the mesh :
            mesh = scene.visuals.Histogram(self._rowdata, self._bins,
                                           **self._kwargs)
            # Get the vertices and faces of the mesh :
            vert = mesh.mesh_data.get_vertices()
            faces = mesh.mesh_data.get_faces()
            # Pass vertices and faces to the histogram :
            self._hist.set_data(vert, faces, color=self._col)
            # Compute the histogram :
            self._rowdata, self._xvec = np.histogram(self._rowdata, self._bins)
            self._rowdata = np.array([0, self._rowdata.max()])
            # Update object :
            self._hist.update()

        # --------------------------------------------------------------------
        # SPECTROGRAM :
        elif self._plot is 'spectrogram':
            # First visible object :
            self._viz = [False, False, True]
            # Define labels :
            self._xlab, self._ylab = 'Time (ms)', 'Frequency (Hz)'
            # Compute the mesh :
            mesh = scene.visuals.Spectrogram(self._rowdata, fs=self._sf,
                                             n_fft=self._nfft, step=self._step,
                                             cmap='viridis')
            # Set data to the image :
            self._imag.set_data(mesh._data)
            # Define the time / freq vector :
            time = np.arange(self.n) / self._sf
            freq = mesh.freqs
            # Re-scale the mesh for fitting in time / frequency :
            sc = (time.max()/mesh.size[0], freq.max()/len(freq), 1)
            self._imag.transform = vist.STTransform(scale=sc)
            # Save the time and frequency vector :
            self._xvec = time
            self._rowdata = freq
            # Update object :
            self._imag.update()

        # Set object visible :
        self._obj_visible()

    def _obj_visible(self):
        """Display or hide objects."""
        self._line.visible = self._viz[0]
        self._hist.visible = self._viz[1]
        self._imag.visible = self._viz[2]

    # ========================================================================
    # CHECK FUNCTIONS
    # ========================================================================
    def _check_data(self):
        """Check the shape of the data acording to the axis parameter."""
        # Get the number of dimensions :
        ndim = self._data.ndim

        # Select the data :
        if ndim == 1:
            self._timeIdx, self._alongIdx = 0, 0
            sl = slice(None)
        else:
            # Check axis :
            if self._axis is None:
                self._axis = [0, 1]
            if len(self._axis) is not 2:
                raise ValueError("The length of the axis parameter must be 2.")
            else:
                self._timeIdx = self._axis[0]
                self._alongIdx = self._axis[1]
            # Select nothing in the data data :
            sl = [slice(1)] * ndim
            # Select everything over the time axis :
            sl[self._timeIdx] = slice(None)
            # Select data along the desire axis :
            sl[self._alongIdx] = self._index

        # Build the row vector and get the length :
        self._rowdata = np.squeeze(self._data[sl])
        self.n = self._data.shape[self._timeIdx]
        self.l = self._data.shape[self._alongIdx]

        # Build the x vector :
        self._xvec = np.arange(self.n)
        if self._xtype == 'time':
            self._xvec = np.divide(self._xvec, self._sf)

    def _check_color(self):
        """Check color inputs."""
        # If histogram and dynamic color, set to random :
        if (self._plot in ['histogram', 'spectrogram']) and (
                                    self._color in ['dyn_minmax', 'dyn_time']):
            self._color = None

        # ---------------------------------------------------------------------
        # Static color :
        if self._color in [None, 'random', 'rnd', 'uniform']:
            if self._color is None:
                self._color = 'random'
            # Get color :
            a_color = type_coloring(color=self._color, n=1,
                                    rnd_dyn=self._rnd_dyn,
                                    unicolor=self._unicolor)
            # Repeat across time in case of line :
            if self._plot is 'line':
                a_color = np.tile(a_color, (self.n, 1))

        # ---------------------------------------------------------------------
        # Dynamic color :
        elif self._color in ['dyn_minmax', 'dyn_time']:
            # Minmax -> rowdata :
            if self._color == 'dyn_minmax':
                data = self._rowdata
            # Time -> time vector :
            elif self._color == 'dyn_time':
                data = np.arange(self.n)
            a_color = type_coloring(color='dynamic', data=data,
                                    clim=self._clim, cmap=self._cmap,
                                    vmin=self._vmin, under=self._under,
                                    vmax=self._vmax, over=self._over)

        # Save the color :
        self._col = a_color

    # ========================================================================
    # PROPERTIES
    # ========================================================================
    @property
    def parent(self):
        """Get doc."""
        return self._parent

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        self._obj.parent = value

    @property
    def n(self):
        """Get the length of the data."""
        return self._n

    @n.setter
    def n(self, value):
        """Set the length of the data."""
        self._n = value

    @property
    def xlim(self):
        """Get the limit of the x-axis."""
        return self._xvec.min(), self._xvec.max()

    @property
    def ylim(self):
        """Get the limit of the y-axis."""
        return self._rowdata.min(), self._rowdata.max()

    @property
    def rect(self):
        """Get the optimal rectangle to fit to the data."""
        xlim, ylim = self.xlim, self.ylim
        return xlim[0], ylim[0], xlim[1]-xlim[0], ylim[1]-ylim[0]

    @property
    def l(self):
        """Get the length of the "along" axis."""
        return self._l

    @l.setter
    def l(self, value):
        """Set the length of the "along" axis."""
        self._l = value
