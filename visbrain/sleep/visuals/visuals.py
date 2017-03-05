"""Convert user inputs and create Nd, 1d and Image objects.
"""
import numpy as np
from scipy.signal import spectrogram

from vispy import scene
import vispy.visuals.transforms as vist

from ...utils import array2colormap, color2vb

__all__ = ["visuals"]


class visuals(object):
    """Create the visual objects to be added to the scene.

    This class create a Nd-plot, 1d-plot and Image-plot objects and set them
    parents on their own canvas.
    """

    def __init__(self, sf, data, time, channels, hypno, cameras=None,
                 method='agg', **kwargs):
        """Init."""
        # =================== CHANNELS ===================
        self._chan = ChannelPlot(channels, camera=cameras[0], method=method,
                                 color=self._chancolor)
        # self._chan.set_data(sf, data)
        self._chan.parent = self._chanCanvas

        # =================== SPECTROGRAM ===================
        # Create a spectrogram object :
        self._spec = Spectrogram(camera=cameras[1])
        self._spec.set_data(sf, data[0, ...], time)
        self._spec.mesh.parent = self._specCanvas.wc.scene
        # Create a visual indicator for spectrogram :
        self._specInd = Indicator(name='spectro_indic', width=2,
                                  color=self._indicol, visible=False)
        self._specInd.set_data(xlim=(0, 30), ylim=(0, 20))
        self._specInd.parent = self._specCanvas.wc.scene

        # =================== HYPNOGRAM ===================
        # Create a hypnogram object :
        self._hyp = Hypnogram(camera=cameras[2], color=self._hypcolor)
        self._hyp.set_data(sf, hypno, time)
        self._hyp.mesh.parent = self._hypCanvas.wc.scene
        # Create a visual indicator for hypnogram :
        self._hypInd = Indicator(name='hypno_indic', width=2,
                                 color=self._indicol, visible=False)
        self._hypInd.set_data(xlim=(0, 30), ylim=(-1, 6))
        self._hypInd.parent = self._hypCanvas.wc.scene
        self._hyp.grid.parent = self._hypCanvas.wc.scene


class ChannelPlot(object):
    """Plot each channel."""

    def __init__(self, channels, color=(.2, .2, .2), width=1., method='agg',
                 camera=None):
        self._camera = camera
        self.rect = []
        # Get color :
        col = color2vb(color)
        # Create one line pear channel :
        pos = np.array([[0, 0], [0, 100]])
        self.mesh, self.grid = [], []
        for i, k in enumerate(channels):
            # Create line :
            mesh = scene.visuals.Line(pos, name=k+'plot', color=col,
                                      method=method, width=width)
            self.mesh.append(mesh)
            # Create a grid :
            # grid = scene.visuals.GridLines(color=(.1, .1, .1, .5),
            #                                scale=(10, .1))
            # grid.set_gl_state('translucent')
            # self.grid.append(grid)

    def set_data(self, sf, data, time, sl=None):
        r = 1.1
        # Manage slice :
        sl = slice(0, data.shape[1]) if sl is None else sl
        # Time vector :
        time = time[sl]
        data = data[:, sl]
        # Set data to each plot :
        for i, k in enumerate(self.mesh):
            dat = np.vstack((time, data[i, :])).T
            dat = np.ascontiguousarray(dat)
            k.set_data(dat)
            # Get camera rectangle and set it:
            rect = (time.min(), r * data[i, :].min(), time.max()-time.min(),
                    r * (data[i, :].max() - data[i, :].min()))
            self._camera[i].rect = rect
            k.update()
            self.rect.append(rect)

    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get the parent value."""
        return self.mesh[0].parent

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        for i, k, in zip(value, self.mesh):
            k.parent = i.wc.scene
            # l.parent = i.wc.scene


class Spectrogram(object):
    """Create and manage a Spectrogram object.

    After object creation, use the set_data() method to pass new data, new
    color, new frequency / time range, new settings...
    """

    def __init__(self, camera):
        # Keep camera :
        self._camera = camera
        self._rect = (0., 0., 0., 0.)
        # Create a vispy image object :
        self.mesh = scene.visuals.Image(np.zeros((2, 2)), name='spectrogram')

    def set_data(self, sf, data, time, cmap='rainbow', nfft=30., overlap=0.,
                 fstart=0.5, fend=25., contraste=.7):
        """Set data to the spectrogram.

        Use this method to change data, colormap, spectrogram settings, the
        starting and ending frequencies.

        Args:
            sf: float
                The sampling frequency.

            data: np.ndarray
                The data to use for the spectrogram. Must be a row vector.

            time: np.ndarray
                The time vector.

        Kargs:
            cmap: string, optional, (def: 'viridis')
                The matplotlib colormap to use.

            nfft: float, optional, (def: 256)
                Number of fft points for the spectrogram (in seconds).

            overlap: float, optional, (def: 0)
                Time overlap for the spectrogram (in seconds).

            fstart: float, optional, (def: None)
                Frequency from which the spectrogram have to start.

            fend: float, optional, (def: None)
                Frequency from which the spectrogram have to finish.

            contraste: float, optional, (def: .7)
                Contraste of the colormap.
        """
        # =================== CONVERSION ===================
        nperseg = int(round(nfft * sf))
        overlap = int(round(overlap * sf))

        # =================== COMPUTE ===================
        # Compute the spectrogram :
        freq, t, mesh = spectrogram(data, fs=sf, nperseg=nperseg,
                                    noverlap=overlap, window='hamming')
        mesh = 20 * np.log10(mesh)

        # =================== FREQUENCY SELCTION ===================
        # Find where freq is [fstart, fend] :
        f = [0., 0.]
        f[0] = np.abs(freq - fstart).argmin() if fstart else 0
        f[1] = np.abs(freq - fend).argmin() if fend else len(freq)
        # Build slicing and select frequency vector :
        sls = slice(f[0], f[1]+1)
        freq = freq[sls]
        self._fstart, self._fend = freq[0], freq[-1]

        # =================== COLOR ===================
        # Get clim :
        clim = (contraste * mesh.min(), contraste * mesh.max())
        # Turn mesh into color array for selected frequencies:
        self.mesh.set_data(array2colormap(mesh[sls, :], cmap=cmap,
                                          clim=clim))

        # =================== TRANSFORM ===================
        # Re-scale the mesh for fitting in time / frequency :
        fact = (freq.max()-freq.min())/len(freq)
        sc = (time.max()/mesh.shape[1], fact, 1)
        tr = [0, freq.min(), 0]
        self.mesh.transform = vist.STTransform(scale=sc, translate=tr)
        # Update object :
        self.mesh.update()
        # Get camera rectangle :
        self.rect = (time.min(), freq.min(), time.max()-time.min(),
                     freq.max()-freq.min())

    # ----------- RECT -----------
    @property
    def rect(self):
        """Get the rect value."""
        return self._rect

    @rect.setter
    def rect(self, value):
        """Set rect value."""
        self._rect = value
        self._camera.rect = value


class Hypnogram(object):
    """Create a hypnogram object."""

    def __init__(self, camera, color='darkblue', width=2):
        # Keep camera :
        self._camera = camera
        self._rect = (0., 0., 0., 0.)
        # Get color :
        col = color2vb(color=color)
        # Create a default line :
        pos = np.array([[0, 0], [0, 100]])
        self.mesh = scene.visuals.Line(pos, name='hypnogram', color=col,
                                       method='agg', width=width)
        # Add grid :
        self.grid = scene.visuals.GridLines(color=(.1, .1, .1, .5),
                                            scale=(10, 1))
        self.grid.set_gl_state('translucent')

    def set_data(self, sf, data, time):
        """Set data to the hypnogram.

        Args:
            sf: float
                The sampling frequency.

            data: np.ndarray
                The data to send. Must be a row vector.

            time: np.ndarray
                The time vector
        """
        # Set data to the mesh :
        self.mesh.set_data(np.vstack((time, data)).T)
        # Re-scale hypnogram :
        # sc = ((time.max() - time.min()) / len(time), 1, 1)
        # self.mesh.transform = vist.STTransform(scale=sc)
        # Get camera rectangle :
        self.rect = (time.min(), data.min() - 1, time.max() - time.min(),
                     data.max() - data.min() + 2)
        self.mesh.update()

    # ----------- RECT -----------
    @property
    def rect(self):
        """Get the rect value."""
        return self._rect

    @rect.setter
    def rect(self, value):
        """Set rect value."""
        self._rect = value
        self._camera.rect = value


class Indicator(object):
    """Create a visual indicator (for spectrogram and hypnogram)."""

    def __init__(self, name='indicator', color='darkgreen', width=8,
                 visible=True):
        # Create a vispy image object :
        pos1 = np.array([[0, 0], [0, 100]])
        pos2 = np.array([[100, 0], [100, 100]])
        self.v1 = scene.visuals.Line(pos1, width=width, name=name, color=color,
                                     method='gl')
        self.v2 = scene.visuals.Line(pos2, width=width, name=name, color=color,
                                     method='gl')
        self.v1._width, self.v2._width = width, width
        self.v1.update(), self.v2.update()
        self.visible = visible

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
        self.update()

    def update(self):
        """Update both lines."""
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

    # ----------- VISIBLE -----------
    @property
    def visible(self):
        """Get the visible value."""
        return self._visible

    @visible.setter
    def visible(self, value):
        """Set visible value."""
        self.v1.visible = value
        self.v2.visible = value
        self.update()
