"""This script contains the main class for 1D plotting."""

import numpy as np

from vispy import scene, visuals
import vispy.visuals.transforms as vist

from ...vbrain.utils import color2vb

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
                 color='white', **kwargs):
        """Init."""
        self._data = np.array(data, dtype=float)
        self._sf = float(sf)
        self._axis = axis
        self._plot = plot
        self._index = index
        self._color = color2vb(color)
        self._xtype = xtype
        self._kwargs = kwargs
        self._bins = kwargs.get('bins', 10)
        self._xlab, self._ylab = '', ''

        # Check data :
        self._check_data()
        self.set_type(plot, color=color, **kwargs)

    # ========================================================================
    # SET FUNCTIONS
    # ========================================================================
    def set_type(self, plot='line', bins=10, color='white', **kwargs):
        """Set the plot type."""
        # LINE :
        if plot == 'line':
            self.mesh = Line((self._xvec, self._rowdata), color=color,
                             **self._kwargs)
            self._xlab, self._ylab = None, None

        # HISTOGRAM :
        elif plot == 'histogram':
            # Compute the mesh :
            self.mesh = scene.visuals.Histogram(self._rowdata, color=color,
                                                **self._kwargs)
            # Compute the histogram :
            self._rowdata, self._xvec = np.histogram(self._rowdata, self._bins)
            self._rowdata = np.array([0, self._rowdata.max()])

        # SPECTROGRAM :
        elif plot == 'spectrogram':
            # Define labels :
            self._xlab, self._ylab = 'Time (ms)', 'Frequency (Hz)'
            # Compute the mesh :
            self.mesh = scene.visuals.Spectrogram(self._rowdata, fs=self._sf,
                                                  cmap='viridis',
                                                  **self._kwargs)
            # Define the time / freq vector :
            time = np.arange(self.n) / self._sf
            freq = self.mesh.freqs
            # Re-scale the mesh for fitting in time / frequency :
            sc = (time.max()/self.mesh.size[0], freq.max()/len(freq), 1)
            self.mesh.transform = vist.STTransform(scale=sc)
            # Save the time and frequency vector :
            self._xvec = time
            self._rowdata = freq

    def set_data(self, data, axis=None, index=0):
        """Set some data."""
        self._data, self._axis, self._index = data, axis, index
        self._check_data()
        self.set_type(self._plot, color=self._color, **self._kwargs)

    # ========================================================================
    # CHECK FUNCTIONS
    # ========================================================================
    def _check_data(self):
        """Check the shape of the data acording to the axis parameter."""
        # Get the number of dimensions :
        ndim = self._data.ndim

        # Select the data :
        if ndim == 1:
            self._timeIdx, self._alongIdx = None, None
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
        self.n = len(self._data)

        # Build the x vector :
        self._xvec = np.arange(self.n)
        if self._xtype is 'time':
            self._xvec = np.divide(self._xvec, self._sf)

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
        self.mesh.parent = value

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
