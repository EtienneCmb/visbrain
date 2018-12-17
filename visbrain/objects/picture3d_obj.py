"""Base class for objects of type connectivity."""
import numpy as np

from vispy import scene
import vispy.visuals.transforms as vist

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import wrap_properties
from ..visuals import PicMesh


class Picture3DObj(VisbrainObject):
    """Create a 3-D picture object.

    Parameters
    ----------
    name : string
        The name of the connectivity object.
    data : array_like
        Array of data pictures of shape (n_sources, n_rows, n_columns).
    xyz : array_like
        The 3-d position of each picture of shape (n_sources, 3).
    select : array_like | None
        Select the pictures to display. Should be a vector of bolean values
        of shape (n_sources,).
    pic_width : float | 7.
        Width of each picture.
    pic_height : float | 7.
        Height of each picture.
    alpha : float | 1.
        Image transparency.
    cmap : string | 'viridis'
        Colormap to use.
    vmin : float | None
        Lower threshold of the colormap.
    under : string | None
        Color to use for values under vmin.
    vmin : float | None
        Higher threshold of the colormap.
    over : string | None
        Color to use for values over vmax.
    translate : tuple | (0., 0., 1.)
        Translation over the (x, y, z) axis.
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

    Notes
    -----
    List of supported shortcuts :

        * **s** : save the figure
        * **<delete>** : reset camera

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import Picture3DObj
    >>> n_rows, n_cols, n_pic = 10, 20, 5
    >>> data = np.random.rand(n_pic, n_rows, n_cols)
    >>> xyz = np.random.uniform(-10, 10, (n_pic, 3))
    >>> pic = Picture3DObj('Pic', data, xyz, cmap='plasma')
    >>> pic.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, data, xyz, select=None, pic_width=7.,
                 pic_height=7., alpha=1., cmap='viridis', clim=None, vmin=None,
                 vmax=None, under='gray', over='red', translate=(0., 0., 1.),
                 transform=None, parent=None, verbose=None, _z=-10., **kw):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)

        # _______________________ CHECKING _______________________
        # Data :
        assert isinstance(data, np.ndarray) and data.ndim == 3.
        self._n_nodes = data.shape[0]
        self._minmax = (data.min(), data.max())
        # XYZ :
        sh = xyz.shape
        assert (sh[1] in [2, 3]) and (sh[0] == len(self))
        xyz = xyz if sh[1] == 3 else np.c_[xyz, np.full((len(self),), _z)]
        self._xyz = xyz.astype(np.float32)
        # Select :
        assert (select is None) or isinstance(select, (list, np.ndarray))
        # Width, height :
        assert all([isinstance(k, (int, float)) for k in (pic_height,
                                                          pic_width)])
        self._pic_width, self._pic_height = pic_width, pic_height
        # Translate :
        assert len(translate) == 3
        tr = vist.STTransform(translate=translate)
        self._translate = translate
        # Alpha :
        assert isinstance(alpha, (int, float)) and (0. <= alpha <= 1.)
        self._alpha = alpha

        # _______________________ IMAGE _______________________
        self._pic = PicMesh(data, xyz, pic_width, pic_height, translate,
                            select, **self.to_kwargs())
        self._pic.transform = tr
        self._pic.parent = self._node

    def __len__(self):
        """Get the number of pictures."""
        return self._n_nodes

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._xyz.mean(0)
        dist = np.linalg.norm(self._xyz, axis=1).max()
        cam = scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)
        self.camera = cam
        return cam

    def update(self):
        """Update image."""
        self._pic.update()

    ###########################################################################
    ###########################################################################
    #                             PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- PIC_WIDTH -----------
    @property
    def pic_width(self):
        """Get the pic_width value."""
        return self._pic_width

    @pic_width.setter
    @wrap_properties
    def pic_width(self, value):
        """Set pic_width value."""
        assert isinstance(value, (int, float))
        self._pic_width = value
        self._pic.set_data(width=value)

    # ----------- PIC_HEIGHT -----------
    @property
    def pic_height(self):
        """Get the height value."""
        return self._pic_height

    @pic_height.setter
    @wrap_properties
    def pic_height(self, value):
        """Set pic_height value."""
        assert isinstance(value, (int, float))
        self._pic_height = value
        self._pic.set_data(height=value)

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
        self._pic.transform.translate = value
        self._translate = value
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
        self._pic.alpha = value
        self._alpha = value


class CombinePictures(CombineObjects):
    """Combine pictures objects.

    Parameters
    ----------
    pobjs : Picture3DObj/list | None
        List of picture objects.
    select : string | None
        The name of the picture object to select.
    parent : VisPy.parent | None
        Images object parent.
    """

    def __init__(self, pobjs=None, select=None, parent=None):
        """Init."""
        CombineObjects.__init__(self, Picture3DObj, pobjs, select, parent)
