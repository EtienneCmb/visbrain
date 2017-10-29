"""Base class for objects of type source."""
import logging
import numpy as np

from vispy import scene

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import array2colormap, color2vb, wrap_properties
from ..visuals import CbarArgs, Arrow
from ..visuals.arrow import ARROW_TYPES


logger = logging.getLogger('visbrain')


class VectorObj(VisbrainObject, CbarArgs):
    """Create a vector object.

    Parameters
    ----------
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Markers object parent.
    verbose : string
        Verbosity level.
    _z : float | 10.
        In case of (n_sources, 2) use _z to specify the elevation.
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, arrow_start, arrow_end=2., data=None, select=None,
                 color='black',
                 line_width=5.,
                 arrow_type='stealth', arrow_size=10.,
                 transform=None, antialias=False, cmap='viridis',
                 clim=None, vmin=None, under='gray', vmax=None, over='red',
                 parent=None, verbose=None, _z=-10., **kwargs):
        """Init."""
        # Init Visbrain object base class and SourceProjection :
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        # Initialize colorbar arguments :
        isvmin = isinstance(vmin, (int, float))
        isvmax = isinstance(vmax, (int, float))
        CbarArgs.__init__(self, cmap, clim, isvmin, vmin, isvmax, vmax, under,
                          over)
        # _______________________ CHECKING _______________________
        # arrow_start // arrow_end :
        assert isinstance(arrow_start, np.ndarray)
        if isinstance(arrow_end, (int, float)):
            arrow_end = arrow_start * arrow_end
        assert isinstance(arrow_end, np.ndarray)
        assert arrow_start.shape == arrow_end.shape
        n_arrows = arrow_start.shape[0]
        # Select :
        select = np.ones(n_arrows, dtype=bool) if select is None else select
        assert select.dtype == bool and len(select) == n_arrows
        arrow_start = arrow_start[select, ...]
        arrow_end = arrow_end[select, ...]
        self._n_arrows = arrow_start.shape[0]
        # Line width // arrow type / size :
        assert isinstance(line_width, (int, float))
        assert arrow_type in ARROW_TYPES and isinstance(arrow_size, float)
        self._line_width = line_width
        self._arrow_size = arrow_size
        self._arrow_type = arrow_type
        #
        if isinstance(data, np.ndarray):
            data = data[select]
            clim = (data.min(), data.max()) if clim is None else clim
            assert len(clim) == 2
            color = array2colormap(data, cmap=cmap, clim=clim, vmin=vmin,
                                   vmax=vmax, under=under, over=over)
        else:
            color = np.tile(color2vb(color).reshape(1, -1), (len(self), 1))

        # _______________________ ARROWS _______________________
        # Build arrows :
        arrows = np.c_[arrow_start, arrow_end]
        line = arrows.reshape(len(self) * 2, 3)
        line_color = np.repeat(color, 2, axis=0)
        self._arrows = Arrow(pos=line, color=line_color, arrows=arrows,
                             arrow_type=arrow_type, arrow_size=arrow_size,
                             antialias=antialias, arrow_color=color,
                             connect='segments', width=line_width,
                             parent=self._node)

    def __len__(self):
        """Get the number of arrows."""
        return self._n_arrows

    def _get_camera(self):
        """Get the most adapted camera."""
        # d_mean = self._xyz.mean(0)
        # dist = np.sqrt(np.sum(d_mean ** 2))
        return scene.cameras.TurntableCamera()

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
