"""Base class for objects of type source."""
import logging
import numpy as np

from vispy import scene
from vispy.scene.visuals import Arrow
from vispy.visuals.line.arrow import ARROW_TYPES

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import array2colormap, color2vb, wrap_properties, normalize


logger = logging.getLogger('visbrain')
ARROW_DTYPES = [np.dtype([('start', float, 3), ('end', float, 3)]),
                np.dtype([('vertices', float, 3), ('normals', float, 3)])]


class VectorObj(VisbrainObject):
    """Create a vector object.

    Parameters
    ----------
    name : string
        Name of the vector object.
    arrows : array_like, tuple, list
        The position of arrows. Use either :

            * A list (or tuple) of two arrays with identical shapes (N, 3).
              The first array specify the (x, y, z) position where arrows start
              and the second the (x, y, z) position of the end of each arrow.
            * Alternatively to the point above, an array of type
              [('start', float, 3), ('end', float, 3)] can also be used.
            * An array of type [('vertices', float, 3), ('normals', float, 3)].
              This method use the normals to vertices to inferred the arrow
              locations. In addition, if `data` is not None, `data` is used to
              inferred the arrow length.
    data : array_like | None
        Attach some data to each vector. This data can be used to inferred the
        color.
    inferred_data : bool | False
        If the `arrows` input use the (start, end) method and if inferred_data
        is set to True, the magnitude of each vector is used as data.
    select : array_like | None
        An array of boolean values to select some specifics arrows.
    color : array_like/tuple/string | 'black'
        If no data are provided, use this parameter to set a unique color for
        all vectors.
    dynamic : tuple | None
        Use a dynamic transparency method. The dynamic input must be a tuple
        of two float between [0, 1]. Vectors with stronger associated data are
        going to be set more opaque.
    line_width : float | 5.
        Line width of each vector.
    arrow_size : float | 10.
        Size of the arrow-head.
    arrow_type : string | 'stealth'
        The arrow-head type. Use either 'stealth', 'curved', 'angle_30',
        'angle_60', 'angle_90', 'triangle_30', 'triangle_60', 'triangle_90'
        or 'inhibitor_round'.
    arrow_coef : float | 1.
        Use this coefficient to define longer arrows. Must be a float superior
        to 1.
    arrow_norm : tuple | (5., 20.)
        Control arrow length for arrows defined using vertices and normals.
    antialias : bool | False
        Use smoothed lines.
    cmap : string | 'viridis'
        The colormap to use (if data is not None).
    clim : tuple | None
        Colorbar limits. If None, the (max, min) of data is used (if data is
        not None).
    vmin : float | None
        Minimum threshold (if data is not None).
    under : string | 'gray'
        Color for values under vmin (if data is not None).
    vmax : float | None
        Maximum threshold (if data is not None).
    over : string | 'red'
        Color for values over vmax (if data is not None).
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Markers object parent.
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
    >>> from visbrain.objects import VectorObj
    >>> n_vector = 10
    >>> arrows = [np.random.rand(n_vector, 3), np.random.rand(n_vector, 3)]
    >>> data = np.random.uniform(-10, 10, (n_vector))
    >>> v = VectorObj('Vector', arrows, data=data, antialias=True)
    >>> v.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, arrows, data=None, inferred_data=False,
                 select=None, color='black', dynamic=None, line_width=5.,
                 arrow_size=10., arrow_type='stealth', arrow_coef=1.,
                 arrow_norm=(5., 20.), antialias=False, cmap='viridis',
                 clim=None, vmin=None, under='gray', vmax=None, over='red',
                 transform=None, parent=None, verbose=None, _z=-10., **kw):
        """Init."""
        # Init Visbrain object base class and SourceProjection :
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)

        # _______________________ START // END _______________________
        if isinstance(arrows, (list, tuple)) and len(arrows) == 2:
            arr = list(arrows).copy()
            arrows = np.zeros(arr[0].shape[0], dtype=ARROW_DTYPES[0])
            arrows['start'] = arr[0]
            arrows['end'] = arr[1]
        assert isinstance(arrows, np.ndarray)
        # Select :
        n_arrows = len(arrows)
        select = np.ones(n_arrows, dtype=bool) if select is None else select
        arrows = arrows[select]
        data = data[select] if isinstance(data, np.ndarray) else data
        self._n_arrows = len(arrows)
        # Build (arrow_start, arrow_end)
        assert select.dtype == bool and len(select) == n_arrows
        if arrows.dtype == ARROW_DTYPES[0]:    # (start, end)
            arrow_start, arrow_end = arrows['start'], arrows['end']
            if inferred_data:
                data = np.linalg.norm(arrow_end - arrow_start, axis=1)
        elif arrows.dtype == ARROW_DTYPES[1]:  # (vertices, normals)
            assert len(arrow_norm) == 2
            norm = np.ones(n_arrows) if not isinstance(
                data, np.ndarray) else data.copy()
            norm = normalize(norm, arrow_norm[0], arrow_norm[1]).reshape(-1, 1)
            arrow_start = arrows['vertices']
            arrow_end = arrow_start + norm * arrows['normals']
        else:
            raise ValueError("Undefined type for the `arrows` input.")
        assert arrow_coef >= 1.
        arrow_end *= arrow_coef

        # _______________________ CHECKING _______________________
        # Line width // arrow type / size :
        assert isinstance(line_width, (int, float))
        assert arrow_type in ARROW_TYPES and isinstance(arrow_size, float)
        self._line_width = line_width
        self._arrow_size = arrow_size
        self._arrow_type = arrow_type
        # Get color :
        if isinstance(data, np.ndarray):
            # Clim :
            clim = (data.min(), data.max()) if clim is None else clim
            assert len(clim) == 2
            # Color :
            color = array2colormap(data, cmap=cmap, clim=clim, vmin=vmin,
                                   vmax=vmax, under=under, over=over)
            # Dynamic transparency :
            if isinstance(dynamic, (tuple, list)) and len(dynamic) == 2:
                assert all(x >= 0. and x <= 1. for x in dynamic)
                color[..., -1] = normalize(data.copy(), dynamic[0], dynamic[1])
        else:
            color = np.tile(color2vb(color).reshape(1, -1), (len(self), 1))

        # _______________________ ARROWS _______________________
        # Build arrows :
        pos = np.c_[arrow_start, arrow_end]
        line = pos.reshape(len(self) * 2, 3)
        line_color = np.repeat(color, 2, axis=0)
        self._arrows = Arrow(pos=line, color=line_color, arrows=pos,
                             arrow_type=arrow_type, arrow_size=arrow_size,
                             antialias=antialias, arrow_color=color,
                             connect='segments', width=line_width,
                             parent=self._node)

    def __len__(self):
        """Get the number of arrows."""
        return self._n_arrows

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._arrows._pos.mean(0)
        dist = 1.1 * np.linalg.norm(self._arrows._pos, axis=1).max()
        return scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)

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
        value = max(1., value)
        self._arrows._width = value
        self._line_width = value
        self._arrows.update()

    # ----------- ARROW_TYPE -----------
    @property
    def arrow_type(self):
        """Get the arrow_type value."""
        return self._arrow_type

    @arrow_type.setter
    @wrap_properties
    def arrow_type(self, value):
        """Set arrow_type value."""
        self._arrows.arrow_type = value
        self._arrow_type = value
        self._arrows.update()

    # ----------- ARROW_SIZE -----------
    @property
    def arrow_size(self):
        """Get the arrow_size value."""
        return self._arrow_size

    @arrow_size.setter
    @wrap_properties
    def arrow_size(self, value):
        """Set arrow_size value."""
        self._arrows.arrow_size = value
        self._arrow_size = value
        self._arrows.update()


class CombineVectors(CombineObjects):
    """Combine vectors objects.

    Parameters
    ----------
    vobjs : VectorObj/list | None
        List of vector objects.
    select : string | None
        The name of the vector object to select.
    parent : VisPy.parent | None
        Images object parent.
    """

    def __init__(self, vobjs=None, select=None, parent=None):
        """Init."""
        CombineObjects.__init__(self, VectorObj, vobjs, select, parent)
