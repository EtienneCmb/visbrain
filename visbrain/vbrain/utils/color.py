"""Group functions for color managment.

This file contains a bundle of functions that can be used to have a more
flexible control of diffrent problem involving colors (like turn an array /
string / faces into RBGA colors, defining the basic colormap object...)
"""

import numpy as np

from matplotlib.cm import ScalarMappable
import matplotlib.colors as mplcol
from warnings import warn

from .math import normalize


__all__ = ['color2vb', 'array2colormap', 'dynamic_color', 'color2faces',
           '_colormap'
           ]


def color2vb(color=None, default=(1, 1, 1), length=1, alpha=1.0):
    """Turn into a RGBA compatible color format.

    This function can tranform a tuple of RGB, a matplotlib color or an
    hexadecimal color into an array of RGBA colors.

    Kargs:
        color: None/tuple/string, optional, (def: None)
            The color to use. Can either be None, or a tuple (R, G, B),
            a matplotlib color or an hexadecimal color '#...'.

        default: tuple, optional, (def: (1,1,1))
            The default color to use instead.

        length: int, optional, (def: 1)
            The length of the output array.

        alpha: float, optional, (def: 1)
            The opacity (Last digit of the RGBA tuple).

    Return:
        vcolor: array
            Array of RGBA colors of shape (length, 4).
    """
    # Default or static color :
    if (color is None) or isinstance(color, (str, tuple)):
        # Default color :
        if color is None:
            coltuple = default
        # Static color :
        elif isinstance(color, (tuple, list)):
            if len(color) == 4:
                alpha = color[-1]
                color = color[0:-1]
            coltuple = color
        # Matplotlib color :
        elif isinstance(color, str) and (color[0] is not '#'):
            # Check if the name is in the Matplotlib database :
            if color in mplcol.cnames.keys():
                coltuple = mplcol.hex2color(mplcol.cnames[color])
            else:
                warn("The color name "+color+" is not in the matplotlib "
                     "database. Default color will be used instead.")
                coltuple = default
        # Hexadecimal colors :
        elif isinstance(color, str) and (color[0] is '#'):
            try:
                coltuple = mplcol.hex2color(color)
            except:
                warn("The hexadecimal color "+color+" is not valid. "
                     "Default color will be used instead.")
                coltuple = default
        # Set the color :
        vcolor = np.concatenate((np.array([list(coltuple)]*length),
                                 alpha*np.ones((length, 1),
                                               dtype=float)), axis=1)

        return vcolor
    else:
        raise ValueError(str(type(color)) + " is not a recognized type of "
                         "color. Use None, tuple or string")


def array2colormap(x, cmap='inferno', clim=None, alpha=1.0, vmin=None,
                   vmax=None, under='dimgray', over='darkred',
                   faces_render=False):
    """Transform an array of data into colormap (array of RGBA).

    Args:
        x: array
            Array of data

    Kargs:
        cmap: string, optional, (def: inferno)
            Matplotlib colormap

        clim: tuple/list, optional, (def: None)
            Limit of the colormap. The clim parameter must be a tuple / list
            of two float number each one describing respectively the (min, max)
            of the colormap. Every values under clim[0] or over clim[1] will
            peaked.

        alpha: float, optional, (def: 1.0)
            The opacity to use. The alpha parameter must be between 0 and 1.

        vmin: float, optional, (def: None)
            Threshold from which every color will have the color defined using
            the under parameter bellow.

        under: tuple/string, optional, (def: 'dimgray')
            Matplotlib color for values under vmin.

        vmax: float, optional, (def: None)
            Threshold from which every color will have the color defined using
            the over parameter bellow.

        over: tuple/string, optional, (def: 'darkred')
            Matplotlib color for values over vmax.

        faces_render: boll, optional, (def: False)
            Precise if the render should be applied to faces

    Return:
        color: array
            Array of RGBA colors
    """
    # ================== Check input argument types ==================
    # Force data to be an array :
    x = np.array(x)
    # Check clim :
    if (clim is None) or (clim is (None, None)):
        clim = (x.min(), x.max())
    else:
        clim = list(clim)
        if len(clim) is not 2:
            raise ValueError("The length of the clim must be 2: (min, max)")
        else:
            if clim[0] is None:
                clim[0] = x.min()
            if clim[1] is None:
                clim[1] = x.max()
    # Check (vmin, under) / (vmax, over) :
    if vmin is None:
        under = None
    elif (vmin is not None) and (vmin < clim[0]):
        if (vmin < clim[0]) or (vmin > clim[1]):
            vmin, under = None, None
            warn("vmin must be between clim[0] and clim[1]. vmin will be "
                 "ignored")
    else:
        if not isinstance(under, (str, tuple)):
            raise ValueError("The under parameter must be a string referring "
                             "to a matplotlib color or a (R, G, B) tuple.")
    if vmax is None:
        over = None
    elif (vmax is not None) and (vmax > clim[1]):
        if (vmax < clim[0]) or (vmax > clim[1]):
            vmax, over = None, None
            warn("vmax must be between clim[0] and clim[1]. vmax will be "
                 "ignored")
    else:
        if not isinstance(over, (str, tuple)):
            raise ValueError("The over parameter must be a string referring "
                             "to a matplotlib color or a (R, G, B) tuple.")
    if (vmin is not None) and (vmax is not None) and (vmin >= vmax):
        vmin, vmax, under, over = None, None, None, None
        warn("vmin > vmax : both arguments have been ignored.")
        # vmin, vmax = vmax, vmin
    # Check alpha :
    if (alpha < 0) or (alpha > 1):
        warn("The alpha parameter must be >= 0 and <= 1.")

    # ================== Define colormap ==================
    cm = ScalarMappable(cmap=cmap)

    # ================== Clip / Peak ==================
    # Force array to clip if x is under / over clim :
    if clim[0] > x.min():
        x = colorclip(x, clim[0], kind='under')
    if clim[1] < x.max():
        x = colorclip(x, clim[1], kind='over')

    # ================== Colormap (under, over) ==================
    # Set colormap (vmin, under) :
    if vmin is None:
        cm.set_clim(vmin=None)
    else:
        cm.set_clim(vmin=vmin)
        cm.cmap.set_under(color=under)
    # Set colormap (vmax, over) :
    if vmax is None:
        cm.set_clim(vmax=None)
    else:
        cm.set_clim(vmax=vmax)
        cm.cmap.set_over(color=over)

    # ================== Apply colormap ==================
    # Apply colormap to x :
    x_cmap = np.array(cm.to_rgba(x, alpha=alpha))
    # Faces render (repeat the color to other dimensions):
    if faces_render:
        x_cmap = np.transpose(np.tile(x_cmap[..., np.newaxis],
                                      (1, 1, 3)), (0, 2, 1))

    return x_cmap


def dynamic_color(color, x, dynamic=(0.0, 1.0)):
    """Dynamic color changing.

    Args:
        color: np.ndarray
            The color to dynamic change. color must have a shape
            of (N, 4) RGBA colors

        x: np.ndarray
            Dynamic values for color. x must have a shape of (N,)
    Kargs:
        dynamic: tuple, optional, (def: (0.0, 1.0))
            Control the dynamic of color.

    Return
        colordyn: np.ndarray
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

    Args:
        color: RGBA tuple
            Tuple of RGBA colors

        length: tuple
            Length of faces

    Return
        colorFace: the color adapted for faces
    """
    color = color.ravel()
    colorL = np.tile(np.array(color)[..., np.newaxis, np.newaxis],
                     (1, length, 3))
    return np.transpose(colorL, (1, 2, 0))


class _colormap(object):
    """Manage the diffrent inputs for the colormap creation.

    Kargs:
        cmap: string, optional, (def: None)
            Matplotlib colormap (like 'viridis', 'inferno'...).

        clim: tuple/list, optional, (def: None)
            Colorbar limit. Every values under / over clim will
            clip.

        vmin: float, optional, (def: None)
            Every values under vmin will have the color defined
            using the under parameter.

        vmax: float, optional, (def: None)
            Every values over vmin will have the color defined
            using the over parameter.

        under: tuple/string, optional, (def: None)
            Matplotlib color under vmin.

        over: tuple/string, optional, (def: None)
            Matplotlib color over vmax.

        data: ndarray, optional, (def: None)
            The data to use. This is only usefull to define automatically
            the clim parameter.
    """

    def __init__(self, cmap=None, clim=None, vmin=None, vmax=None, under=None,
                 over=None, data=None):
        """Init."""
        if data is None:
            clim = (None, None)
            vmin, vmax, under, over = None, None, None, None
            self._MinMax = (None, None)
        else:
            if clim is None:
                clim = [data.min(), data.max()]
            self._MinMax = (data.min(), data.max())
        self._cb = {'cmap': cmap, 'clim': clim, 'vmin': vmin, 'vmax': vmax,
                    'under': under, 'over': over}

    def __getitem__(self, key):
        """Get the item value, specified using the key parameter.

        Arg:
            key: string
                Name of the parameter

        Return:
            The item value
        """
        return self._cb[key]

    def __setitem__(self, key, item):
        """Set a value to an item.

        Arg:
            key: string
                Name of the parameter

            item: any
                The value of the item
        """
        self._cb[key] = item

    def cbUpdateFrom(self, obj):
        """Update a _colormap object using based on an other _colormap object.

        Arg:
            obj: _colormap object
                The _colormap object to use to take it values.
        """
        objkeys = obj._cb.keys()
        for k in self._cb.keys():
            if k in objkeys:
                self[k] = obj[k]
        self._MinMax = obj._MinMax


def colorclip(x, th, kind='under'):
    """Force an array to have clipping values.

    :x: array of data
    :th: the threshold to use
    :kind: string, can be either 'under' or 'over'
    """
    if kind is 'under':
        idx = x < th
    elif kind is 'over':
        idx = x > th
    x[idx] = th
    return x
