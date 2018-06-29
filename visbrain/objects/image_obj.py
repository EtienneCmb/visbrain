"""Base class for objects that need an iage (TF, Pacmap, spectro...)."""
import numpy as np
import logging

from vispy import scene

from .visbrain_obj import VisbrainObject
from ..utils import vispy_array, wrap_properties, color2vb

logger = logging.getLogger('visbrain')


class ImageObj(VisbrainObject):
    """Create a single image object.

    Parameters
    ----------
    data : array_like
        Array of data. If data.ndim in [1, 2] the color is inferred from
        the data. Otherwise, if data.ndim is 3, data is interpreted as
        color if the last dimension is either 3 (RGB) or 4 (RGBA).
    xaxis : array_like | None
        Vector to use for the x-axis (number of columns in the image).
        If None, `xaxis` is inferred from the second dimension of data.
    yaxis : array_like | None
        Vector to use for the y-axis (number of rows in the image).
        If None, `yaxis` is inferred from the first dimension of data.
    clim : tuple | None
        Colorbar limits. If None, `clim=(data.min(), data.max())`
    cmap : string | None
        Colormap name.
    vmin : float | None
        Minimum threshold of the colorbar.
    under : string/tuple/array_like | None
        Color for values under vmin.
    vmax : float | None
        Maximum threshold of the colorbar.
    under : string/tuple/array_like | None
        Color for values over vmax.
    interpolation : string | 'nearest'
        Interpolation method for the image. See vispy.scene.visuals.Image for
        availables interpolation methods.
    max_pts : int | -1
        Maximum number of points of the image along the x or y axis. This
        parameter is essentially used to solve OpenGL issues with very large
        images.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Markers object parent.
    verbose : string
        Verbosity level.
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
    >>> from visbrain.objects import ImageObj
    >>> n = 100
    >>> time = np.r_[np.arange(n - 1), np.arange(n)[::-1]]
    >>> time = time.reshape(-1, 1) + time.reshape(1, -1)
    >>> im = ImageObj('im', time, cmap='Spectral_r', interpolation='bicubic')
    >>> im.preview(axis=True)
    """

    def __init__(self, name, data=None, xaxis=None, yaxis=None, cmap='viridis',
                 clim=None, vmin=None, under='gray', vmax=None, over='red',
                 interpolation='nearest', max_pts=-1, parent=None,
                 transform=None, verbose=None, **kw):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)

        # _______________________ CHECKING _______________________
        assert isinstance(max_pts, int)
        self._n_limit = max_pts  # fix GL issues with large images

        # _______________________ VISUAL _______________________
        self._image = scene.visuals.Image(parent=self._node, name="_ImageObj",
                                          interpolation=interpolation)
        self._image.transform = scene.transforms.STTransform()

        # _______________________ SET DATA _______________________
        if isinstance(data, np.ndarray):
            self.set_data(data, xaxis, yaxis, clim, cmap, vmin, under, vmax,
                          over)

    def set_data(self, data, xaxis=None, yaxis=None, clim=None, cmap=None,
                 vmin=None, under=None, vmax=None, over=None):
        """Set data to the image."""
        assert isinstance(data, np.ndarray) and data.ndim <= 3
        data = np.atleast_2d(data)
        # Get the x-axis and y-axis :
        xaxis = np.arange(data.shape[1]) if xaxis is None else np.array(xaxis)
        yaxis = np.arange(data.shape[0]) if yaxis is None else np.array(yaxis)
        assert (len(xaxis) == data.shape[1]) and (len(yaxis) == data.shape[0])
        self._dim = (xaxis.min(), xaxis.max(), yaxis.min(), yaxis.max())
        # Convert data to color (if data.ndim == 2)
        if data.ndim == 2:  # infer color from data
            clim = (data.min(), data.max()) if clim is None else clim
            # Limit the number of points :
            if any([k > self._n_limit for k in data.shape]):
                dsf_x = max(1, int(np.round(data.shape[0] / self._n_limit)))
                dsf_y = max(1, int(np.round(data.shape[1] / self._n_limit)))
                logger.debug("Image size reduced along the x and y-axis with "
                             "a down-sampling factor of %s" % ([dsf_x, dsf_y]))
                data = data[::dsf_x, ::dsf_y]
                xaxis, yaxis = xaxis[::dsf_x], yaxis[::dsf_y]
            # Set properties :
            self._update_cbar_args(cmap, clim, vmin, vmax, under, over)
            # Get colormap :
            cmap = self._get_glsl_colormap(limits=(data.min(), data.max()))
            self._image.cmap = cmap
            self._image.clim = 'auto'
        else:  # data is already a compatible color
            assert data.shape[-1] in [3, 4]
        # Set color to the image :
        self._image.set_data(vispy_array(data))
        fact_x = (self._dim[1] - self._dim[0]) / len(xaxis)
        fact_y = (self._dim[3] - self._dim[2]) / len(yaxis)
        sc = (fact_x, fact_y, 1.)
        tr = (self._dim[0], self._dim[2], 0.)
        self._image.transform.scale = sc
        self._image.transform.translate = tr

    def _get_camera(self):
        """Get the most adapted camera."""
        rect = (self._dim[0], self._dim[2], self._dim[1] - self._dim[0],
                self._dim[3] - self._dim[2])
        flip = (False, type(self).__name__ == 'ImageObj', False)
        return scene.cameras.PanZoomCamera(rect=rect, flip=flip)

    ###########################################################################
    ###########################################################################
    #                             PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- INTERPOLATION -----------
    @property
    def interpolation(self):
        """Get the interpolation value."""
        return self._image.interpolation

    @interpolation.setter
    @wrap_properties
    def interpolation(self, value):
        """Set interpolation value."""
        assert isinstance(value, str)
        self._image.interpolation = value

    # ----------- CMAP -----------
    @property
    def cmap(self):
        """Get the cmap value."""
        return self._cmap

    @cmap.setter
    @wrap_properties
    def cmap(self, value):
        """Set cmap value."""
        self._cmap = value

    # ----------- CLIM -----------
    @property
    def clim(self):
        """Get the clim value."""
        return self._clim

    @clim.setter
    @wrap_properties
    def clim(self, value):
        """Set clim value."""
        assert len(value) == 2
        self._clim = value

    # ----------- VMIN -----------
    @property
    def vmin(self):
        """Get the vmin value."""
        return self._vmin

    @vmin.setter
    @wrap_properties
    def vmin(self, value):
        """Set vmin value."""
        assert isinstance(value, (int, float))
        self._vmin = value

    # ----------- VMAX -----------
    @property
    def vmax(self):
        """Get the vmax value."""
        return self._vmax

    @vmax.setter
    @wrap_properties
    def vmax(self, value):
        """Set vmax value."""
        assert isinstance(value, (int, float))
        self._vmax = value

    # ----------- UNDER -----------
    @property
    def under(self):
        """Get the under value."""
        return self._under

    @under.setter
    @wrap_properties
    def under(self, value):
        """Set under value."""
        color = color2vb(value)
        self._under = color

    # ----------- OVER -----------
    @property
    def over(self):
        """Get the over value."""
        return self._over

    @over.setter
    @wrap_properties
    def over(self, value):
        """Set over value."""
        color = color2vb(value)
        self._over = color
