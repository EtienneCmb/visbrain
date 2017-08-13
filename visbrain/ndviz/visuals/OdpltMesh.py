"""This script contains the main class for 1D plotting."""

import numpy as np
from scipy.interpolate import interp1d

from vispy import scene
import vispy.visuals.transforms as vist

from ...utils import type_coloring, array2colormap

__all__ = ['OdpltMesh']


class OdpltMesh(object):
    """Create a 1D object.

    This class can be used to create a line, an image, a histogram, a
    spectrogram or a cloud of points with several graphical and computing
    options.
    """

    def __init__(self, *args, **kwargs):
        """Init."""
        # Create a minimalistic Line, Histogram and spectrogram objects :
        self._line = scene.visuals.Line([0, 1], width=2, name='line')
        self._hist = scene.visuals.Histogram([0], name='histogram')
        self._spec = scene.visuals.Image(np.random.rand(2, 2),
                                         name='spectrogram')
        self._mark = scene.visuals.Markers(pos=np.random.rand(2, 2),
                                           name='marker')
        self._imag = scene.visuals.Image(np.random.rand(20, 20),
                                         name='image')
        # Set objects in list :
        self._obj = [self._line, self._hist, self._spec, self._mark,
                     self._imag]
        self._name = [k.name for k in self._obj]
        self._minmax = (0., 1.)

    # ========================================================================
    # SET FUNCTIONS
    # ========================================================================

    def set_data(self, data, sf, axis=None, index=0, plot='line',
                 color='uniform', rnd_dyn=(.3, .9), cmap='viridis',
                 clim=None, vmin=None, under=None, vmax=None, over=None,
                 unicolor='white', bins=10, nfft=256, step=128, fstart=None,
                 fend=None, itp_type=None, itp_step=1., method='gl', msize=5.,
                 imz=None, **kwargs):
        """Set new values to the selected plot.

        Dynamic coloring are only available for line type plot but all of the
        static color type can be applied either on line or histogram. The
        spectrogram colormap is fixed to 'viridis'.

        Args:
            data: ndarray
                The array to use. Must be float32.

            sf: float
                The sampling frequency.

        Kargs:
            axis: tuple/list/array, optional, (def: None)
                The axis parameter must contains two integers. The first one
                refer to the location of the time axis. All the points over
                this axis are going to be selected. The second one refer to the
                axis along which selecting the data.

            index: int, optional, (def: 0)
                The index along axis[1] for selecting the data.

            plot: string, optional, (def: 'line')
                Specify how to plot the data. Use either 'line', 'histogram',
                'spectrogram' or 'marker'.

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

            bins: float, optional, (def: 10.)
                Number of bins for the histogram.

            nfft: int, optional, (def: 256)
                Number of fft points for the spectrogram.

            step: int, optional, (def: 128)
                Time step for the spectrogram.

            fstart: float, optional, (def: None)
                Frequency from which the spectrogram have to start

            fend: float, optional, (def: None)
                Frequency from which the spectrogram have to finish

            itp_type: string, optional, (def: None)
                Interpolation type. See scipy.interp1d for selecting an
                appropriate type.

            itp_step: float, optional, (def: 1.)
                Interpolation step.

            method: string, optional, (def: 'gl')
                Method for plotting the line. Use 'gl' or 'agg'

            msize: float, optional, (def: 5.)
                Marker size.

            imz: int, optional, (def: None)
                Z-axis for image plot type.
        """
        self._axis, self._index, self._sf = axis, index, sf
        self._itptype, self._itpstep = itp_type, itp_step
        self._plot, self._bins = plot, bins
        self._nfft, self._step, self._method = nfft, step, method
        self._color, self._rnd_dyn, self._unicolor = color, rnd_dyn, unicolor
        self._cmap, self._clim, self._vmin, self._vmax = cmap, clim, vmin, vmax
        self._fstart = fstart if fstart else 0
        self._fend = fend if fend else sf / 2
        self._under, self._over = under, over
        self._msize, self._imz = msize, imz

        # #############################################################
        # CHECK DATA
        # #############################################################
        # Get the number of dimensions :
        self.ndim, self.sh = data.ndim, data.shape

        # Select the data :
        if self.ndim == 1:
            self._timeIdx, self._alongIdx = 0, 0
            sl = slice(None)
        else:
            # Check axis :
            if axis is None:
                axis = [0, 1]
                self._axis = axis
            if len(axis) is not 2:
                raise ValueError("The length of the axis parameter must be 2.")
            else:
                self._timeIdx = axis[0]
                self._alongIdx = axis[1]
            # Z-axis for image :
            if (imz is None) and (self.ndim > 2):
                self._imz = list(set(range(self.ndim)).difference(
                                                        set(self._axis)))[0]
            elif (imz is None):
                self._imz = 0
            # -----------------------------------------
            # 1D Slice :
            # Select nothing in the data data :
            sl = [slice(1)] * self.ndim
            # Select everything over the time axis :
            sl[self._timeIdx] = slice(None)
            # Select data along the desire axis :
            sl[self._alongIdx] = self._index
            # -----------------------------------------
            # 2D Slice :
            sl2d = [slice(1)] * self.ndim
            sl2d[self._alongIdx] = slice(None)
            sl2d[self._timeIdx] = slice(None)
            # Get data of z-axis (for ndim >= 3) :
            if self.ndim >= 3:
                sl2d[self._imz] = self._index

        if plot != 'image':
            # Build the row vector and get the length :
            rowdata = np.squeeze(data[sl])
            self.n = data.shape[self._timeIdx]
            self.l = data.shape[self._alongIdx]

            # Build the x-vector :
            xvec = np.arange(self.n, dtype=np.float32)

            # Data interpolation :
            if (itp_type not in [None, 'None']):
                # Define the interpolation function :
                f = interp1d(xvec, rowdata, kind=itp_type, copy=False)
                # Define the new interpolation vector :
                xvec = np.arange(0, self.n-1, itp_step, dtype=np.float32)
                self.n = len(xvec)
                # Build the interpolate data :
                rowdata = f(xvec)

            # Time conversion of thex-axis :
            xvec /= self._sf

        # #############################################################
        # CHECK COLOR
        # #############################################################
        # If histogram and dynamic color, set to random :
        if (plot in ['image', 'histogram', 'spectrogram']) and (color in [
                                                    'dyn_minmax', 'dyn_time']):
            color = 'random'

        # ---------------------------------------------
        # Static color :
        if color in [None, 'random', 'rnd', 'uniform']:
            if color is None:
                color = 'random'
            # Get color :
            a_color = type_coloring(color=color, n=1, rnd_dyn=rnd_dyn,
                                    unicolor=unicolor)
            # Repeat across time in case of line :
            if plot == 'line':
                a_color = np.tile(a_color, (self.n, 1))

        # ---------------------------------------------
        # Dynamic color :
        elif color in ['dyn_minmax', 'dyn_time']:
            # Minmax -> rowdata :
            if color == 'dyn_minmax':
                data = rowdata
            # Time -> time vector :
            elif color == 'dyn_time':
                data = np.arange(self.n)
            a_color = type_coloring(color='dynamic', data=data, clim=clim,
                                    cmap=cmap, vmin=vmin, under=under,
                                    vmax=vmax, over=over)
            self.minmax = (data.min(), data.max())

        # #############################################################
        # PLOT TYPE
        # #############################################################
        # ---------------------------------------------
        # LINE :
        if plot == 'line':
            # Set the data :
            self._line.method = method
            self._line.set_data(np.vstack((xvec, rowdata)).T, color=a_color)
            # Update object :
            self._line.update()

        # ---------------------------------------------
        # IMAGE :
        if plot == 'image':
            # Rank axis :
            axrk = np.argsort(self._axis).argsort()
            # Get 2d data :
            data2d = np.squeeze(data[sl2d])
            # Transpose if needed :
            if np.array_equal(axrk, np.array([0, 1])):
                data2d = data2d.T
            # Set the data :
            cmap = array2colormap(np.flipud(data2d), cmap=cmap, vmin=vmin,
                                  under=under, vmax=vmax, over=over, clim=clim)
            self._imag.set_data(cmap)
            # Re-define xvec / rowdata :
            xvec = np.arange(data2d.shape[1]+1) / self._sf
            rowdata = np.arange(data2d.shape[0]+1)
            self.minmax = (data2d.min(), data2d.max())
            # Transform image according to time vector :
            sc = (xvec.max()/data2d.shape[1], 1, 1)
            self._imag.transform = vist.STTransform(scale=sc)
            # Update object :
            self._imag.update()

        # ---------------------------------------------
        # HISTOGRAM :
        elif plot == 'histogram':
            # Compute the mesh :
            mesh = scene.visuals.Histogram(rowdata, bins)
            # Get the vertices and faces of the mesh :
            vert = mesh.mesh_data.get_vertices()
            faces = mesh.mesh_data.get_faces()
            # Pass vertices and faces to the histogram :
            self._hist.set_data(vert, faces, color=a_color)
            # Compute the histogram :
            rowdata, xvec = np.histogram(rowdata, bins)
            rowdata = np.array([rowdata[np.nonzero(rowdata)].min(),
                               rowdata.max()])
            # Update object :
            self._hist.update()
            self.minmax = (rowdata.min(), rowdata.max())

        # ---------------------------------------------
        # SPECTROGRAM :
        elif plot == 'spectrogram':
            # Compute the mesh :
            mesh = scene.visuals.Spectrogram(rowdata, fs=self._sf, n_fft=nfft,
                                             step=step)
            # Select frequencies :
            freq = mesh.freqs
            f = [0., 0.]
            f[0] = np.abs(freq - fstart).argmin() if fstart else 0
            f[1] = np.abs(freq - fend).argmin() if fend else len(freq)
            sls = slice(f[0], f[1]+1)
            freq = freq[sls]
            self._fstart, self._fend = freq[0], freq[-1]
            # Set data to the image :
            self._spec.set_data(array2colormap(mesh._data[sls, :], cmap=cmap,
                                               vmin=vmin, under=under,
                                               vmax=vmax, over=over, clim=clim)
                                )
            # Re-scale the mesh for fitting in xvec / frequency :
            fact = (freq.max()-freq.min())/len(freq)
            sc = (xvec.max()/mesh.size[0], fact, 1)
            tr = [0, freq.min(), 0]
            self._spec.transform = vist.STTransform(scale=sc, translate=tr)
            # Save the xvec and frequency vector :
            rowdata = freq
            # Update object :
            self._spec.update()
            self.minmax = (mesh._data.min(), mesh._data.max())

        # ---------------------------------------------
        # MARKER :
        elif plot == 'marker':
            self._mark.set_data(np.vstack((xvec, rowdata)).T, size=msize,
                                face_color=a_color, edge_color='white')
            self._mark.scaling = True
            # Update object :
            self._mark.update()

        # Update (xvec, rowdata) limits (for the camera) :
        self.xlim = (xvec.min(), xvec.max())
        self.ylim = (rowdata.min(), rowdata.max())

        # Manage visible object :
        self._viz = [plot == k for k in self._name]
        self._obj_visible()

    def _obj_visible(self):
        """Display or hide objects."""
        for k, i in enumerate(self._obj):
            i.visible = self._viz[k]

    # ========================================================================
    # PROPERTIES
    # ========================================================================
    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get doc."""
        return [k.parent for k in self._obj]

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        for k, i in enumerate(self._obj):
            i.parent = value

    # ----------- XLIM -----------
    @property
    def xlim(self):
        """Get the limit of the x-axis."""
        return self._xlim

    @xlim.setter
    def xlim(self, value):
        """Set xlim value."""
        self._xlim = value

    # ----------- YLIM -----------
    @property
    def ylim(self):
        """Get the limit of the y-axis."""
        return self._ylim

    @ylim.setter
    def ylim(self, value):
        """Set ylim value."""
        self._ylim = value

    # ----------- RECT -----------
    @property
    def rect(self):
        """Get the optimal rectangle to fit to the data."""
        xlim, ylim = self.xlim, self.ylim
        return xlim[0], ylim[0], xlim[1]-xlim[0], ylim[1]-ylim[0]

    # ----------- N -----------
    @property
    def n(self):
        """Get the length of the data."""
        return self._n

    @n.setter
    def n(self, value):
        """Set the length of the data."""
        self._n = value

    # ----------- L -----------
    @property
    def l(self):
        """Get the length of the "along" axis."""
        return self._l

    @l.setter
    def l(self, value):
        """Set the length of the "along" axis."""
        self._l = value

    # ----------- MINMAX -----------
    @property
    def minmax(self):
        """Get the minmax value."""
        return self._minmax

    @minmax.setter
    def minmax(self, value):
        """Set minmax value."""
        self._minmax = value
