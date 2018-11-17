"""Group functions for color managment.

This file contains a bundle of functions that can be used to have a more
flexible control of diffrent problem involving colors (like turn an array /
string / faces into RBGA colors, defining the basic colormap object...)
"""
import logging

import numpy as np

from vispy.color.colormap import Colormap as VispyColormap

from matplotlib import cm
import matplotlib.colors as mplcol
from warnings import warn

from .sigproc import normalize
from .mesh import vispy_array


__all__ = ('Colormap', 'color2vb', 'array2colormap', 'cmap_to_glsl',
           'dynamic_color', 'color2faces', 'type_coloring', 'mpl_cmap',
           'color2tuple', 'mpl_cmap_index', 'vector_to_opacity')


logger = logging.getLogger('visbrain')


class Colormap(object):
    """Main colormap class.

    Parameters
    ----------
    cmap : string | inferno
        Matplotlib colormap
    clim : tuple/list | None
        Limit of the colormap. The clim parameter must be a tuple / list
        of two float number each one describing respectively the (min, max)
        of the colormap. Every values under clim[0] or over clim[1] will
        peaked.
    alpha : float | 1.0
        The opacity to use. The alpha parameter must be between 0 and 1.
    vmin : float | None
        Threshold from which every color will have the color defined using
        the under parameter bellow.
    under : tuple/string | 'dimgray'
        Matplotlib color for values under vmin.
    vmax : float | None
        Threshold from which every color will have the color defined using
        the over parameter bellow.
    over : tuple/string | 'darkred'
        Matplotlib color for values over vmax.
    translucent : tuple | None
        Set a specific range translucent. With f_1 and f_2 two floats, if
        translucent is :

            * (f_1, f_2) : values between f_1 and f_2 are set to translucent
            * (None, f_2) x <= f_2 are set to translucent
            * (f_1, None) f_1 <= x are set to translucent
    lut_len : int | 1024
        Number of levels for the colormap.
    interpolation : {None, 'linear', 'cubic'}
        Interpolation type. Default is None.

    Attributes
    ----------
    data : array_like
        Color data of shape (n_data, 4)
    shape : tuple
        Shape of the data.
    r : array_like
        Red levels.
    g : array_like
        Green levels.
    b : array_like
        Blue levels.
    rgb : array_like
        RGB levels.
    alpha : array_like
        Transparency level.
    glsl : vispy.colors.Colormap
        GL colormap version.
    """

    def __init__(self, cmap='viridis', clim=None, vmin=None, under=None,
                 vmax=None, over=None, translucent=None, alpha=1.,
                 lut_len=1024, interpolation=None):
        """Init."""
        # Keep color parameters into a dict :
        self._kw = dict(cmap=cmap, clim=clim, vmin=vmin, vmax=vmax,
                        under=under, over=over, translucent=translucent,
                        alpha=alpha)
        # Color conversion :
        if isinstance(cmap, np.ndarray):
            assert (cmap.ndim == 2) and (cmap.shape[-1] in (3, 4))
            # cmap = single color :
            if (cmap.shape[0] == 1) and isinstance(interpolation, str):
                logger.debug("Colormap : unique color repeated.")
                data = np.tile(cmap, (lut_len, 1))
            elif (cmap.shape[0] == lut_len) or (interpolation is None):
                logger.debug("Colormap : Unique repeated.")
                data = cmap
            else:
                from scipy.interpolate import interp2d
                n_ = cmap.shape[1]
                x, y = np.linspace(0, 1, n_), np.linspace(0, 1, cmap.shape[0])
                f = interp2d(x, y, cmap, kind=interpolation)
                # Interpolate colormap :
                data = f(x, np.linspace(0, 1, lut_len))
        elif isinstance(cmap, str):
            data = array2colormap(np.linspace(0., 1., lut_len), **self._kw)
        # Alpha correction :
        if data.shape[-1] == 3:
            data = np.c_[data, np.full((data.shape[0],), alpha)]
        # NumPy float32 conversion :
        self._data = vispy_array(data)

    def to_rgba(self, data):
        """Turn a data vector into colors using colormap properties.

        Parameters
        ----------
        data : array_like
            Vector of data of shape (n_data,).

        Returns
        -------
        color : array_like
            Array of colors of shape (n_data, 4)
        """
        if isinstance(self._kw['cmap'], np.ndarray):
            return self._data
        else:
            return array2colormap(data, **self._kw)

    def __len__(self):
        """Get the number of colors in the colormap."""
        return self._data.shape[0]

    def __getitem__(self, name):
        """Get a color item."""
        return self._kw[name]

    @property
    def data(self):
        """Get colormap data."""
        return self._data

    @property
    def shape(self):
        """Get the shape of the data."""
        return self._data.shape

    @property
    def glsl(self):
        """Get a glsl version of the colormap."""
        return cmap_to_glsl(lut_len=len(self), **self._kw)

    @property
    def r(self):
        """Get red levels."""
        return self._data[:, 0]

    @property
    def g(self):
        """Get green levels."""
        return self._data[:, 1]

    @property
    def b(self):
        """Get blue levels."""
        return self._data[:, 2]

    @property
    def rgb(self):
        """Get rgb levels."""
        return self._data[:, 0:3]

    @property
    def alpha(self):
        """Get transparency level."""
        return self._data[:, -1]


def color2vb(color=None, default=(1., 1., 1.), length=1, alpha=1.0,
             faces_index=False):
    """Turn into a RGBA compatible color format.

    This function can tranform a tuple of RGB, a matplotlib color or an
    hexadecimal color into an array of RGBA colors.

    Parameters
    ----------
    color : None/tuple/string | None
        The color to use. Can either be None, or a tuple (R, G, B),
        a matplotlib color or an hexadecimal color '#...'.
    default : tuple | (1,1,1)
        The default color to use instead.
    length : int | 1
        The length of the output array.
    alpha : float | 1
        The opacity (Last digit of the RGBA tuple).
    faces_index : bool | False
        Specify if the returned color have to be compatible with faces index
        (e.g a (n_color, 3, 4) array).

    Return
    ------
    vcolor : array_like
        Array of RGBA colors of shape (length, 4).
    """
    # Default or static color :
    if (color is None) or isinstance(color, (str, tuple, list, np.ndarray)):
        if color is None:  # Default
            coltuple = default
        elif isinstance(color, (tuple, list, np.ndarray)):  # Static
            color = np.squeeze(color).ravel()
            if len(color) == 4:
                alpha = color[-1]
                color = color[0:-1]
            coltuple = color
        elif isinstance(color, str) and (color[0] is not '#'):  # Matplotlib
            # Check if the name is in the Matplotlib database :
            if color in mplcol.cnames.keys():
                coltuple = mplcol.hex2color(mplcol.cnames[color])
            else:
                warn("The color name " + color + " is not in the matplotlib "
                     "database. Default color will be used instead.")
                coltuple = default
        elif isinstance(color, str) and (color[0] is '#'):  # Hexadecimal
            try:
                coltuple = mplcol.hex2color(color)
            except:
                warn("The hexadecimal color " + color + " is not valid. "
                     "Default color will be used instead.")
                coltuple = default
        # Set the color :
        vcolor = np.concatenate((np.array([list(coltuple)] * length),
                                 alpha * np.ones((length, 1),
                                                 dtype=np.float32)), axis=1)

        # Faces index :
        if faces_index:
            vcolor = np.tile(vcolor[:, np.newaxis, :], (1, 3, 1))

        return vcolor.astype(np.float32)
    else:
        raise ValueError(str(type(color)) + " is not a recognized type of "
                         "color. Use None, tuple or string")


def color2tuple(color, astype=np.float32, rmalpha=True, roundto=2):
    """Return a RGB tuple of the color.

    Parameters
    ----------
    color : None/tuple/string | None
        The color to use. Can either be None, or a tuple (R, G, B),
        a matplotlib color or an hexadecimal color '#...'.
    astype : type | np.float32
        The final color type.
    rmalpha : bool | True
        Specify if the alpha component have to be deleted.
    roundto : int | 2
        Number of digits per RGB.

    Returns
    -------
    coltuple: tuple
        Tuple of colors.
    """
    # Get the converted color :
    ccol = color2vb(color).ravel().astype(astype)
    # Round it :
    ccol = np.ndarray.tolist(np.around(ccol, roundto))
    if rmalpha:
        return tuple(ccol[0:-1])
    else:
        return tuple(ccol)


def array2colormap(x, cmap='inferno', clim=None, alpha=1.0, vmin=None,
                   vmax=None, under='dimgray', over='darkred',
                   translucent=None, faces_render=False):
    """Transform an array of data into colormap (array of RGBA).

    Parameters
    ----------
    x: array
        Array of data
    cmap : string | inferno
        Matplotlib colormap
    clim : tuple/list | None
        Limit of the colormap. The clim parameter must be a tuple / list
        of two float number each one describing respectively the (min, max)
        of the colormap. Every values under clim[0] or over clim[1] will
        peaked.
    alpha : float | 1.0
        The opacity to use. The alpha parameter must be between 0 and 1.
    vmin : float | None
        Threshold from which every color will have the color defined using
        the under parameter bellow.
    under : tuple/string | 'dimgray'
        Matplotlib color for values under vmin.
    vmax : float | None
        Threshold from which every color will have the color defined using
        the over parameter bellow.
    over : tuple/string | 'darkred'
        Matplotlib color for values over vmax.
    translucent : tuple | None
        Set a specific range translucent. With f_1 and f_2 two floats, if
        translucent is :

            * (f_1, f_2) : values between f_1 and f_2 are set to translucent
            * (None, f_2) x <= f_2 are set to translucent
            * (f_1, None) f_1 <= x are set to translucent
    faces_render : boll | False
        Precise if the render should be applied to faces

    Returns
    -------
    color : array_like
        Array of RGBA colors
    """
    # ================== Check input argument types ==================
    # Force data to be an array :
    x = np.asarray(x)

    # Check clim :
    clim = (None, None) if clim is None else list(clim)
    assert len(clim) == 2

    # ---------------------------
    # Check alpha :
    if (alpha < 0) or (alpha > 1):
        warn("The alpha parameter must be >= 0 and <= 1.")

    # ================== Define colormap ==================
    sc = cm.ScalarMappable(cmap=cmap)

    # Fix limits :
    norm = mplcol.Normalize(vmin=clim[0], vmax=clim[1])
    sc.set_norm(norm)

    # ================== Apply colormap ==================
    # Apply colormap to x :
    x_cmap = np.array(sc.to_rgba(x, alpha=alpha))

    # ================== Colormap (under, over) ==================
    if (vmin is not None) and (under is not None):
        under = color2vb(under)  # if isinstance(under, str) else under
        x_cmap[x < vmin, :] = under
    if (vmax is not None) and (over is not None):
        over = color2vb(over)  # if isinstance(over, str) else over
        x_cmap[x > vmax, :] = over

    # ================== Transparency ==================
    x_cmap = _transclucent_cmap(x, x_cmap, translucent)

    # Faces render (repeat the color to other dimensions):
    if faces_render:
        x_cmap = np.transpose(np.tile(x_cmap[..., np.newaxis],
                                      (1, 1, 3)), (0, 2, 1))

    return x_cmap.astype(np.float32)


def _transclucent_cmap(x, x_cmap, translucent, smooth=None):
    """Sub function to define transparency."""
    if translucent is not None:
        is_num = [isinstance(k, (int, float)) for k in translucent]
        assert len(translucent) == 2 and any(is_num)
        if all(is_num):                # (f_1, f_2)
            trans_x = np.logical_and(translucent[0] <= x, x <= translucent[1])
        elif is_num == [True, False]:  # (f_1, None)
            trans_x = translucent[0] <= x
        elif is_num == [False, True]:  # (None, f_2)
            trans_x = x <= translucent[1]
        x_cmap[..., -1] = np.invert(trans_x)
        if isinstance(smooth, int):
            alphas = x_cmap[:, -1]
            alphas = np.convolve(alphas, np.hanning(smooth), 'valid')
            alphas /= max(alphas.max(), 1.)
            x_cmap[smooth - 1::, -1] = alphas
    return x_cmap


def cmap_to_glsl(limits=None, lut_len=1024, color=None, **kwargs):
    """Get a glsl colormap.

    Parameters
    ----------
    limits : tuple | None
        Color limits for the object. Must be a tuple of two floats.
    lut_len : int | 1024
        Number of levels for the colormap.
    color : string | None
        Use a unique color for the colormap.
    kwarg : dict | None
        Additional inputs to pass to the array2colormap function.

    Returns
    -------
    cmap : vispy.color.Colormap
        VisPy colormap instance.
    """
    if limits is None:
        limits = (0., 1.)
    assert len(limits) == 2
    # Color transform :
    vec = np.linspace(limits[0], limits[1], lut_len)
    if color is None:  # colormap
        cmap = VispyColormap(array2colormap(vec, **kwargs))
    else:              # uniform color
        translucent = kwargs.get('translucent', None)
        rep_col = color2vb(color, length=lut_len)
        cmap_trans = _transclucent_cmap(vec, rep_col, translucent)
        cmap = VispyColormap(cmap_trans)

    return cmap


def dynamic_color(color, x, dynamic=(0., 1.)):
    """Dynamic color changing.

    Parameters
    ----------
    color : array_like
        The color to dynamic change. color must have a shape
        of (N, 4) RGBA colors
    x : array_like
        Dynamic values for color. x must have a shape of (N,)
    dynamic : tuple | (0.0, 1.0)
        Control the dynamic of color.

    Returns
    -------
    colordyn : array_like
        Dynamic color with a shape of (N, 4)
    """
    x = x.ravel()
    # Check inputs types :
    if color.shape[1] != 4:
        raise ValueError("Color must be RGBA")
    if color.shape[0] != len(x):
        raise ValueError("The length of color must be the same as"
                         " x: " + str(len(x)))
    # Normalise x :
    if dynamic[0] < dynamic[1]:
        x_norm = normalize(x, tomin=dynamic[0], tomax=dynamic[1])
    else:
        x_norm = np.full((len(x),), dynamic[0], dtype=np.float)
    # Update color :
    color[:, 3] = x_norm
    return color


def color2faces(color, length):
    """Pass a simple color to faces shape.

    Parameters
    ----------
    color : RGBA tuple
        Tuple of RGBA colors
    length : tuple
        Length of faces

    Returns
    -------
    color_face : array_like
        The color adapted for faces
    """
    color = np.asarray(color).ravel()
    colort = np.tile(np.array(color)[..., np.newaxis, np.newaxis],
                     (1, length, 3))
    return np.transpose(colort, (1, 2, 0))


def colorclip(x, th, kind='under'):
    """Force an array to have clipping values.

    Parameters
    ----------
    x : array_like
        Array of data.
    th : float
        The threshold to use.
    kind : string | 'under'
        Use eiher 'under' or 'over' for fore the array to clip for every
        values respectively under or over th.

    Returns
    -------
    x : array_like
        The clipping array.
    """
    if kind is 'under':
        idx = x < th
    elif kind is 'over':
        idx = x > th
    x[idx] = th
    return x


def type_coloring(color=None, n=1, data=None, rnd_dyn=(0.3, 0.9), clim=None,
                  cmap='viridis', vmin=None, under=None, vmax=None, over=None,
                  unicolor='gray'):
    """Switch between different coloring types.

    This function can be used to color a signal using random, uniform or
    dynamic colors.

    Parameters
    ----------
    color : string/tuple/array | None
        Choose how to color signals. Use None (or 'rnd', 'random') to
        generate random colors. Use 'uniform' (see the unicolor
        parameter) to define the same color for all signals. Use
        'dynamic' to have a dynamic color according to data values.
    n : int | 1
        The number of colors to generate in case of random or uniform
        colors.
    data : array_like | None
        The data to convert into color if the color type is dynamic.
        If this parameter is ignored, a default linear spaced vector of
        length n will be used instead.
    rnd_dyn : tuple | (.3, .9)
        Define the dynamic of random color. This parameter is active
        only if the color parameter is turned to None (or 'rnd' /
        'random').
    cmap : string | 'inferno'
        Matplotlib colormap (parameter active for 'dyn_minmax' and
        'dyn_time' color).
    clim : tuple/list | None
        Limit of the colormap. The clim parameter must be a tuple /
        list of two float number each one describing respectively the
        (min, max) of the colormap. Every values under clim[0] or over
        clim[1] will peaked (parameter active for 'dyn_minmax' and
        'dyn_time' color).
    alpha : float | 1.0
        The opacity to use. The alpha parameter must be between 0 and 1
        (parameter active for 'dyn_minmax' and 'dyn_time' color).
    vmin : float | None
        Threshold from which every color will have the color defined
        using the under parameter bellow (parameter active for
        'dyn_minmax' and 'dyn_time' color).
    under : tuple/string | 'gray'
        Matplotlib color for values under vmin (parameter active for
        'dyn_minmax' and 'dyn_time' color).
    vmax : float | None
        Threshold from which every color will have the color defined
        using the over parameter bellow (parameter active for
        'dyn_minmax' and 'dyn_time' color).
    over : tuple/string | 'red'
        Matplotlib color for values over vmax (parameter active for
        'dyn_minmax' and 'dyn_time' color).
    unicolor : tuple/string | 'gray'
        The color to use in case of uniform color.
    """
    # ---------------------------------------------------------------------
    # Random color :
    if color in [None, 'rnd', 'random']:
        # Create a (m, 3) color array :
        colout = np.random.uniform(size=(n, 3), low=rnd_dyn[0], high=rnd_dyn[1]
                                   )

    # ---------------------------------------------------------------------
    # Dynamic color :
    elif color == 'dynamic':
        # Generate a linearly spaced vector for None data :
        if data is None:
            data = np.arange(n)
        # Get colormap as (n, 3):
        colout = array2colormap(data.ravel(), cmap=cmap, clim=clim, vmin=vmin,
                                vmax=vmax, under=under, over=over)[:, 0:3]

    # ---------------------------------------------------------------------
    # Uniform color :
    elif color == 'uniform':
        # Create a (m, 3) color array :
        colout = color2vb(unicolor, length=n)[:, 0:3]

    # ---------------------------------------------------------------------
    # Not found color :
    else:
        raise ValueError("The color parameter is not recognized.")

    return colout.astype(np.float32)


def mpl_cmap(invert=False):
    """Get the list of matplotlib colormaps.

    Parameters
    ----------
    invert : bool | False
        Get the list of inverted colormaps.

    Returns
    -------
    cmap_lst: list
        list of available matplotlib colormaps.
    """
    # Full list of colormaps :
    fullmpl = list(cm.datad.keys()) + list(cm.cmaps_listed.keys())
    # Get the list of cmaps (inverted or not) :
    if invert:
        cmap_lst = [k for k in fullmpl if k.find('_r') + 1]
    else:
        cmap_lst = [k for k in fullmpl if not k.find('_r') + 1]

    # Sort the list :
    cmap_lst.sort()

    return cmap_lst


def mpl_cmap_index(cmap, cmaps=None):
    """Find the index of a colormap.

    Parameters
    ----------
    cmap : string
        Colormap name.
    cmaps : list | None
        List of colormaps.

    Returns
    -------
    idx : int
        Index of the colormap.
    invert : bool
        Boolean value indicating if it's a reversed colormap.
    """
    # Find if it's a reversed colormap :
    invert = bool(cmap.find('_r') + 1)
    # Get list of colormaps :
    if cmaps is None:
        cmap = cmap.replace('_r', '')
        cmaps = mpl_cmap()
        return np.where(np.char.find(cmaps, cmap) + 1)[0][0], invert
    else:
        return cmaps.index(cmap), invert


def vector_to_opacity(data, clim=None, dyn=(0., 1.), orientation='ascending',
                      order=1):
    """Convert a data vector into opacity.

    Parameters
    ----------
    data : array_like
        Vector of data of shape (n_data,).
    clim : tuple | None
        Limits to use. If None, clim is defined as the min and max of the data
    dyn : tuple | (0., 1.)
        Minimum and maximum of the transparency levels.
    orientation : {'ascending', 'center', 'descending'}
        Define the transparency behavior :

            * 'ascending' : from translucent to opaque
            * 'center' : from opaque to translucent and finish by opaque
            * 'descending' ; from opaque to translucent
    order : int | 1
        Get the alpha ** order.

    Returns
    -------
    alpha : array_like
        Array of transparency
    """
    data = np.asarray(data)
    assert data.ndim == 1
    clim = (data.min(), data.max()) if clim is None else clim
    assert len(clim) == 2
    assert (len(dyn) == 2) and (dyn[0] >= 0.) and (dyn[1] <= 1.)
    assert orientation in ['ascending', 'center', 'descending']

    _data, clim = data.copy(), np.asarray(clim)
    if orientation == 'center':
        _data = np.abs(_data - clim.mean())
        clim = clim - clim.mean()

    # Get limits :
    xtr_min = max(dyn[0] * _data.min() / clim[0], 0.) if clim[0] != 0. else 0.
    xtr_max = min(dyn[1] * _data.max() / clim[1], 1.) if clim[1] != 0. else 0.

    # Get alpha :
    alpha = np.zeros_like(_data)
    if orientation == 'descending':
        alpha = normalize(_data, xtr_max, xtr_min)
    elif orientation == 'center':
        alpha = normalize(_data, xtr_min, xtr_max)
    elif orientation == 'ascending':
        alpha = normalize(_data, xtr_min, xtr_max)
    return np.clip(alpha, 0., 1.) ** order
