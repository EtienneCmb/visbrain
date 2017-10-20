"""Base class for the time-series object."""
import numpy as np

from vispy import scene
from vispy.scene import visuals
import vispy.visuals.transforms as vist

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import normalize, color2vb, wrap_properties


class TimeSeriesObj(VisbrainObject):
    """Create a  3-D time-series object.

    Parameters
    ----------
    name : string
        Name of the time-series object.
    data : array_like
        Array of time-series of shape (n_sources, n_time_points)
    xyz : array_like
        The 3-D center location  of each time-series of shape (n_sources, 3).
    select : array_like | None
        Select the time-series to display. Should be a vector of bolean values
        of shape (n_sources,).
    line_width : float | 1.5
        Time-series' line width.
    color : array_like/tuple/string | 'white'
        Time-series' color.
    amplitude : float | 6.
        Graphical amplitude of the time-series.
    width : float | 20.
        Graphical width of the time-series.
    alpha : float | 1.
        Time-series transparency.
    translate : tuple | (0., 0., 1.)
        Translate the time-series over the (x, y, z) axes.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Line object parent.
    _z : float | 10.
        In case of (n_sources, 2) use _z to specify the elevation.
    """

    def __init__(self, name, data, xyz, select=None, line_width=1.5,
                 color='white', amplitude=6., width=20., alpha=1.,
                 translate=(0., 0., 1.), transform=None, parent=None, _z=-10.):
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
        select = np.arange(len(self)) if select is None else select
        assert isinstance(select, (list, np.ndarray))
        self._select = select
        # Amplitude / width :
        assert isinstance(amplitude, float) and isinstance(width, float)
        self._amplitude, self._width = amplitude, width
        # Translate :
        assert len(translate) == 3
        tr = vist.STTransform(translate=translate)
        self._translate = translate
        # Line width :
        self._line_width = line_width
        # Color :
        self._color = color2vb(color, alpha=alpha)
        self._alpha = alpha

        # _______________________ LINE _______________________
        self._ts = visuals.Line(name='TimeSeriesObjLine', parent=self._node,
                                width=line_width, color=self._color)
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
        connect = np.zeros((n_nodes, self._n_pts), dtype=bool)
        connect[self._select, 0:-1] = True  # don't connect last point
        self._ts.set_data(pos=pos, connect=connect.ravel())

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._xyz.mean(0)
        dist = np.sqrt(np.sum(d_mean ** 2))
        return scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)

    ###########################################################################
    ###########################################################################
    #                             PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- WIDTH -----------
    @property
    def width(self):
        """Get the width value."""
        return self._width

    @width.setter
    @wrap_properties
    def width(self, value):
        """Set width value."""
        assert isinstance(value, (int, float))
        self._width = value
        self._build_line()

    # ----------- AMPLITUDE -----------
    @property
    def amplitude(self):
        """Get the amplitude value."""
        return self._amplitude

    @amplitude.setter
    @wrap_properties
    def amplitude(self, value):
        """Set amplitude value."""
        assert isinstance(value, (int, float))
        self._amplitude = value
        self._build_line()

    # ----------- COLOR -----------
    @property
    def color(self):
        """Get the color value."""
        return self._color

    @color.setter
    @wrap_properties
    def color(self, value):
        """Set color value."""
        color = color2vb(value)
        self._ts.set_data(color=color)
        self._color = color
        self.update()

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self._alpha

    @alpha.setter
    @wrap_properties
    def alpha(self, value):
        """Set alpha value."""
        assert isinstance(value, (int, float)) and (0. <= value <= 1.)
        self._ts.color[..., -1] = value
        self._alpha = value
        self.update()

    # ----------- TRANSLATE -----------
    @property
    def translate(self):
        """Get the translate value."""
        return self._translate

    @translate.setter
    @wrap_properties
    def translate(self, value):
        """Set translate value."""
        assert len(value) == 3
        self._ts.transform.translate = value
        self._translate = value
        self.update()

    # ----------- LINE_WIDTH -----------
    @property
    def line_width(self):
        """Get the line_width value."""
        return self._line_width

    @line_width.setter
    @wrap_properties
    def line_width(self, value):
        """Set line_width value."""
        assert isinstance(value, (int, float))
        self._ts._width = value
        self._line_width = value
        self._ts.update()


class CombineTimeSeries(CombineObjects):
    """Combine time-series objects.

    Parameters
    ----------
    tsobjs : TimeSeriesObj/list | None
        List of time-series objects.
    select : string | None
        The name of the time-series object to select.
    parent : VisPy.parent | None
        Line object parent.
    """

    def __init__(self, tsobjs=None, select=None, parent=None):
        """Init."""
        CombineObjects.__init__(self, TimeSeriesObj, tsobjs, select, parent)
