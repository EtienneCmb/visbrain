import numpy as np

from vispy import scene
from vispy.scene import visuals
import vispy.visuals.transforms as vist

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import normalize, color2vb


class TimeSeriesObj(VisbrainObject):
    """Create a  3-D time-series object.

    Parameters
    ----------
    """

    def __init__(self, name, data, xyz, select=None, line_width=1.5,
                 color='white', amplitude=6., width=20., translate=(0., 0., 1.),
                 transform=None, parent=None, _z=-10.):
        """Init."""
        # Init Visbrain object base class :
        VisbrainObject.__init__(self, name, parent, transform)
        # _______________________ CHECKING _______________________
        # Data :
        assert isinstance(data, np.ndarray) and data.ndim == 2
        self._n_nodes, self._n_pts = data.shape
        self._data = data
        # XYZ :
        sh = xyz.shape
        assert sh[1] in [2, 3]
        xyz = xyz if sh[1] == 3 else np.c_[xyz, np.full((len(self),), _z)]
        self._xyz = xyz.astype(np.float32)
        # Select :
        select = np.ones(len(self), dtype=bool) if select is None else select
        assert (select.dtype == bool) and (len(select) == len(self))
        self._select = select
        # Amplitude / width :
        assert isinstance(amplitude, float) and isinstance(width, float)
        self._amplitude, self._width = amplitude, width
        # DXYZ :
        tr = vist.STTransform(translate=translate)

        # _______________________ LINE _______________________
        self._ts = visuals.Line(name='TimeSeriesObjLine', parent=self._node,
                                width=line_width, color=color2vb(color))
        self._ts.transform = tr
        self._build_line()

    def __len__(self):
        """Get the number of nodes."""
        return self._n_nodes

    def update(self):
        """Update line."""
        self._ts.update()

    def _build_line(self):
        # Get the number of sources :
        n_nodes = len(self)
        # Build the position vector :
        pos = np.zeros((n_nodes, self._n_pts, 3), dtype=np.float32)
        time = np.linspace(-self._width / 2, self._width / 2, self._n_pts)
        data = normalize(self._data, -self._amplitude / 2, self._amplitude / 2)
        for k in range(n_nodes):
            pos[k, :, 0] = self._xyz[k, 0] + time
            pos[k, :, 1] = self._xyz[k, 1] + data[k, :]
            pos[k, :, 2] = self._xyz[k, 2]
        pos = pos.reshape(n_nodes * self._n_pts, 3)
        # Build the connection vector :
        connect = np.ones((n_nodes, self._n_pts), dtype=bool)
        connect[~self._select, :] = False
        connect[:, -1] = False  # don't connect last point
        self._ts.set_data(pos=pos, connect=connect.ravel())

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._xyz.mean(0)
        dist = np.sqrt(np.sum(d_mean ** 2))
        return scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)

    # ----------- COLOR -----------
    @property
    def color(self):
        """Get the color value."""
        return self._color

    @color.setter
    def color(self, value):
        """Set color value."""
        color = color2vb(value)
        self._ts.set_data(color=color)
        self._color = color
        self.update()

    # ----------- TRANSLATE -----------
    @property
    def translate(self):
        """Get the translate value."""
        return self._translate

    @translate.setter
    def translate(self, value):
        """Set translate value."""
        if len(value) == 3:
            self._ts.transform.translate = value
            self._translate = value
            self.update()

    # ----------- LINE_WIDTH -----------
    @property
    def line_width(self):
        """Get the line_width value."""
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        """Set line_width value."""
        if isinstance(value, (int, float)):
            self._ts.width = value
            self._line_width = value


class CombineTimeSeries(CombineObjects):
    """docstring for CombineTimeSeries"""

    def __init__(self):
        pass
