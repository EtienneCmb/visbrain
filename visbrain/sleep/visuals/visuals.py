"""Convert user inputs and create Nd, 1d and Image objects.
"""
import numpy as np

from vispy import scene
import vispy.visuals.transforms as vist

from ...utils import array2colormap, color2vb

__all__ = ["visuals"]


class visuals(object):
    """Create the visual objects to be added to the scene.

    This class create a Nd-plot, 1d-plot and Image-plot objects and set them
    parents on their own canvas.
    """

    def __init__(self, sf, data, channels, hypno, **kwargs):
        """Init."""
        # =================== CHANNELS ===================
        self._chan = ChannelPlot(channels)
        # self._chan.set_data(sf, data)
        self._chan.parent = self._chanCanvas

        # =================== SPECTROGRAM ===================
        # Create a spectrogram object :
        self._spec = Spectrogram()
        self._spec.set_data(sf, data[0, ...])
        self._spec.mesh.parent = self._specCanvas.wc.scene
        # Create a visual indicator for spectrogram :
        self._specInd = Indicator(name='spectro_indic', width=self._lw)
        self._specInd.set_data(xlim=(0, 30), ylim=(0, 20))
        self._specInd.parent = self._specCanvas.wc.scene

        # =================== HYPNOGRAM ===================
        # Create a hypnogram object :
        self._hyp = Hypnogram()
        self._hyp.set_data(sf, hypno)
        self._hyp.mesh.parent = self._hypCanvas.wc.scene
        # Create a visual indicator for hypnogram :
        self._hypInd = Indicator(name='hypno_indic', width=self._lw)
        self._hypInd.set_data(xlim=(0, 30), ylim=(0, 5))
        self._hypInd.parent = self._hypCanvas.wc.scene


class ChannelPlot(object):
    """Plot each channel."""

    def __init__(self, channels, color='black', width=4):
        # Get color :
        col = color2vb(color)
        # Create one line pear channel :
        pos = np.array([[0, 0], [0, 100]])
        self.mesh = []
        for i, k in enumerate(channels):
            mesh = scene.visuals.Line(pos, name=k+'plot', color=col,
                                      method='gl')
            self.mesh.append(mesh)

    def set_data(self, sf, data, sl=None):
        # Manage slice :
        sl = slice(0, data.shape[1]) if sl is None else sl
        # Time vector :
        time = np.arange(data.shape[1]) / sf
        time = time[sl].astype(np.float32)
        data = data[:, sl]
        # Set data to each plot :
        for i, k in enumerate(self.mesh):
            dat = np.vstack((time, data[i, :])).T
            dat = np.ascontiguousarray(dat)
            k.set_data(dat)
        # Get camera rectangle :
        self.rect = (time.min(), data.min(), time.max()-time.min(),
                     data.max()-data.min())

    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get the parent value."""
        return self.mesh[0].parent

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        for i, k in zip(value, self.mesh):
            k.parent = i.wc.scene


class Spectrogram(object):
    """Create and manage a Spectrogram object.

    After object creation, use the set_data() method to pass new data, new
    color, new frequency / time range, new settings...
    """

    def __init__(self):
        # Create a vispy image object :
        self.mesh = scene.visuals.Image(np.zeros((2, 2)), name='spectrogram')

    def set_data(self, sf, data, cmap='viridis', nfft=256, step=128,
                 fstart=0., fend=20.):
        """Set data to the spectrogram.

        Use this method to change data, colormap, spectrogram settings, the
        starting and ending frequencies.

        Args:
            sf: float
                The sampling frequency.

            data: np.ndarray
                The data to use for the spectrogram. Must be a row vector.

        Kargs:
            cmap: string, optional, (def: 'viridis')
                The matplotlib colormap to use.

            nfft: int, optional, (def: 256)
                Number of fft points for the spectrogram.

            step: int, optional, (def: 128)
                Time step for the spectrogram.

            fstart: float, optional, (def: None)
                Frequency from which the spectrogram have to start.

            fend: float, optional, (def: None)
                Frequency from which the spectrogram have to finish.
        """
        # =================== COMPUTE ===================
        # Compute the spectrogram :
        mesh = scene.visuals.Spectrogram(data, fs=sf, n_fft=nfft, step=step)
        # Get time vector :
        xvec = np.arange(len(data)) / sf

        # =================== FREQUENCY SELCTION ===================
        # Get frequency vector :
        freq = mesh.freqs
        # find where freq is [fstart, fend] :
        f = [0., 0.]
        f[0] = np.abs(freq - fstart).argmin() if fstart else 0
        f[1] = np.abs(freq - fend).argmin() if fend else len(freq)
        # Build slicing and select frequency vector :
        sls = slice(f[0], f[1]+1)
        freq = freq[sls]
        self._fstart, self._fend = freq[0], freq[-1]

        # =================== COLOR ===================
        # Turn mesh into color array for selected frequencies:
        self.mesh.set_data(array2colormap(mesh._data[sls, :], cmap=cmap))

        # =================== TRANSFORM ===================
        # Re-scale the mesh for fitting in xvec / frequency :
        fact = (freq.max()-freq.min())/len(freq)
        sc = (xvec.max()/mesh.size[0], fact, 1)
        tr = [0, freq.min(), 0]
        self.mesh.transform = vist.STTransform(scale=sc, translate=tr)
        # Update object :
        self.mesh.update()
        # Get camera rectangle :
        self.rect = (xvec.min(), freq.min(), xvec.max()-xvec.min(),
                     freq.max()-freq.min())


class Hypnogram(object):
    """Create a hypnogram object."""

    def __init__(self, color='slateblue'):
        # Get color :
        col = color2vb(color=color)
        # Create a default line :
        pos = np.array([[0, 0], [0, 100]])
        self.mesh = scene.visuals.Line(pos, name='hypnogram', color=col)

    def set_data(self, sf, data):
        """Set data to the hypnogram.

        Args:
            sf: float
                The sampling frequency.

            data: np.ndarray
                The data to send. Must be a row vector.
        """
        # Time vector :
        time = np.arange(len(data)) / sf
        self.mesh.set_data(np.vstack((time, data)).T)
        # Get camera rectangle :
        self.rect = (time.min(), data.min(), time.max()-time.min(),
                     data.max()-data.min())


class Indicator(object):
    """Create a visual indicator (for spectrogram and hypnogram)."""

    def __init__(self, name='indicator', color='red', width=8):
        # Create a vispy image object :
        pos1 = np.array([[0, 0], [0, 100]])
        pos2 = np.array([[100, 0], [100, 100]])
        self.v1 = scene.visuals.Line(pos1, width=width, name=name, color=color,
                                     method='agg')
        self.v2 = scene.visuals.Line(pos2, width=width, name=name, color=color,
                                     method='agg')
        self.v1._width, self.v2._width = width, width
        self.v1.update(), self.v2.update()

    def set_data(self, xlim, ylim, offset=5):
        """Move the visual indicator.

        Args:
            xlim: tuple
                A tuple of two float indicating where xlim start and xlim end.

            ylim: tuple
                A tuple of two floats indicating where ylim start and ylim end.

        Kargs:
            offset: float, optional, (def: 5.)
                Offset to apply to the ylim (hide line imperfections).
        """
        # Define new position :
        pos1 = np.array([[xlim[0], ylim[0]-offset], [xlim[0], ylim[1]+offset]])
        pos2 = np.array([[xlim[1], ylim[0]-offset], [xlim[1], ylim[1]+offset]])
        # Set data :
        self.v1.set_data(pos1)
        self.v2.set_data(pos2)
        # Update :
        self.v1.update(), self.v2.update()

    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get the parent value."""
        return self.v1.parent

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        self.v1.parent = value
        self.v2.parent = value
