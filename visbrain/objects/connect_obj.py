"""Base class for objects of type connectivity."""
import numpy as np
from collections import Counter

from vispy import scene
from vispy.scene import visuals

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import array2colormap, normalize, color2vb, wrap_properties


class ConnectObj(VisbrainObject):
    """Create a connectivity object.

    Parameters
    ----------
    name : string
        The name of the connectivity object.
    nodes : array_like
        Array of nodes coordinates of shape (n_nodes, 3).
    edges : array_like | None
        Array of ponderations for edges of shape (n_nodes, n_nodes).
    select : array_like | None
        Array to select edges to display. This should be an array of boolean
        values of shape (n_nodes, n_nodes).
    line_width : float | 3.
        Connectivity line width.
    color_by : {'strength', 'count'}
        Coloring method. Use 'strength' to color edges according to their
        connection strength define by the edges input. Use 'count' to color
        edges according to the number of connections per node.
    custom_colors : dict | None
        Use a dictionary to colorize edges. For example, {1.2: 'red',
        2.8: 'green', None: 'black'} turn connections that have a 1.2 and 2.8
        strength into red and green. All others connections are set to black.
    alpha : float | 1.
        Transparency level (if dynamic is None).
    antialias : bool | False
        Use smoothed lines.
    dynamic : tuple | None
        Control the dynamic opacity. For example, if dynamic=(0, 1),
        strong connections will be more opaque than weaker connections.
    cmap : string | 'viridis'
        Colormap to use if custom_colors is None.
    vmin : float | None
        Lower threshold of the colormap if custom_colors is None.
    under : string | None
        Color to use for values under vmin if custom_colors is None.
    vmin : float | None
        Higher threshold of the colormap if custom_colors is None.
    over : string | None
        Color to use for values over vmax if custom_colors is None.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Line object parent.
    verbose : string
        Verbosity level.
    _z : float | 10.
        In case of (n_sources, 2) use _z to specify the elevation.
    kw : dict | {}
        Optional arguments are used to control the colorbar
        (See :class:`ColorbarObj`).

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import ConnectObj
    >>> n_nodes = 100
    >>> nodes = np.random.rand(n_nodes, 3)
    >>> edges = np.random.uniform(low=-10., high=10., size=(n_nodes, n_nodes))
    >>> select = np.logical_and(edges >= 0, edges <= 1.)
    >>> c = ConnectObj('Connect', nodes, edges, select=select, cmap='inferno',
    >>>                antialias=True)
    >>> c.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, nodes, edges, select=None, line_width=3.,
                 color_by='strength', custom_colors=None, alpha=1.,
                 antialias=False, dynamic=None, cmap='viridis', clim=None,
                 vmin=None, vmax=None, under='gray', over='red',
                 transform=None, parent=None, verbose=None, _z=-10., **kw):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)

        # _______________________ CHECKING _______________________
        # Nodes :
        assert isinstance(nodes, np.ndarray) and nodes.ndim == 2
        sh = nodes.shape
        self._n_nodes = sh[0]
        assert sh[1] >= 2
        pos = nodes if sh[1] == 3 else np.c_[nodes, np.full((len(self),), _z)]
        self._pos = pos.astype(np.float32)
        # Edges :
        assert edges.shape == (len(self), len(self))
        if not np.ma.isMA(edges):
            mask = np.zeros(edges.shape, dtype=bool)
            edges = np.ma.masked_array(edges, mask=mask)
        # Select :
        if isinstance(select, np.ndarray):
            assert select.shape == edges.shape and select.dtype == bool
            edges.mask = np.invert(select)
        edges.mask[np.tril_indices(len(self), 0)] = True
        self._edges = edges
        # Colorby :
        assert color_by in ['strength', 'count']
        self._color_by = color_by
        # Dynamic :
        if dynamic is not None:
            assert len(dynamic) == 2
        self._dynamic = dynamic
        # Custom color :
        if custom_colors is not None:
            assert isinstance(custom_colors, dict)
        self._custom_colors = custom_colors
        # Alpha :
        assert 0. <= alpha <= 1.
        self._alpha = alpha

        # _______________________ LINE _______________________
        self._connect = visuals.Line(name='ConnectObjLine', width=line_width,
                                     antialias=antialias, parent=self._node,
                                     connect='segments')
        self._connect.set_gl_state('translucent')
        self._build_line()

    def __len__(self):
        """Get the number of nodes."""
        return self._n_nodes

    def update(self):
        """Update the line."""
        self._connect.update()

    def _build_line(self):
        """Build the connectivity line."""
        # Build the line position (consecutive segments):
        nnz_x, nnz_y = np.where(~self._edges.mask)
        indices = np.c_[nnz_x, nnz_y].flatten()
        line_pos = self._pos[indices, :]

        # Color either edges or nodes :
        if self._color_by == 'strength':
            nnz_values = self._edges.compressed()
            values = np.c_[nnz_values, nnz_values].flatten()
        elif self._color_by == 'count':
            node_count = Counter(np.ravel([nnz_x, nnz_y]))
            values = np.array([node_count[k] for k in indices])
        self._minmax = (values.min(), values.max())
        if self._clim is None:
            self._clim = self._minmax

        # Get the color according to values :
        if isinstance(self._custom_colors, dict):  # custom color
            if None in list(self._custom_colors.keys()):  # {None : 'color'}
                color = color2vb(self._custom_colors[None], length=len(values))
            else:  # black by default
                color = np.zeros((len(values), 4), dtype=np.float32)
            for val, col in self._custom_colors.items():
                color[values == val, :] = color2vb(col)
        else:
            color = array2colormap(values, **self.to_kwargs())
        color[:, -1] = self._alpha

        # Dynamic color :
        if self._dynamic is not None:
            color[:, 3] = normalize(values.copy(), tomin=self._dynamic[0],
                                    tomax=self._dynamic[1])

        # Send data to the connectivity object :
        self._connect.set_data(pos=line_pos, color=color)

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._pos.mean(0)
        dist = np.sqrt(np.sum(d_mean ** 2))
        return scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)

    ###########################################################################
    ###########################################################################
    #                             PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- LINE_WIDTH -----------
    @property
    def line_width(self):
        """Get the line_width value."""
        return self._connect.width

    @line_width.setter
    @wrap_properties
    def line_width(self, value):
        """Set line_width value."""
        assert isinstance(value, (int, float))
        self._connect._width = value
        self.update()

    # ----------- COLOR_BY -----------
    @property
    def color_by(self):
        """Get the color_by value."""
        return self._color_by

    @color_by.setter
    @wrap_properties
    def color_by(self, value):
        """Set color_by value."""
        assert value in ['strength', 'count']
        self._color_by = value
        self._build_line()

    # ----------- DYNAMIC -----------
    @property
    def dynamic(self):
        """Get the dynamic value."""
        return self._dynamic

    @dynamic.setter
    @wrap_properties
    def dynamic(self, value):
        """Set dynamic value."""
        assert value is None or len(value) == 2
        self._dynamic = value
        self._build_line()

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self._alpha

    @alpha.setter
    @wrap_properties
    def alpha(self, value):
        """Set alpha value."""
        assert 0. <= value <= 1.
        self._connect.color[:, -1] = value
        self._alpha = value
        self.update()


class CombineConnect(CombineObjects):
    """Combine connectivity objects.

    Parameters
    ----------
    cobjs : ConnectObj/list | None
        List of source objects.
    select : string | None
        The name of the connectivity object to select.
    parent : VisPy.parent | None
        Markers object parent.
    """

    def __init__(self, cobjs=None, select=None, parent=None):
        """Init."""
        CombineObjects.__init__(self, ConnectObj, cobjs, select, parent)
