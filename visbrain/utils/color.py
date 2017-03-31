"""Group functions for color managment.

This file contains a bundle of functions that can be used to have a more
flexible control of diffrent problem involving colors (like turn an array /
string / faces into RBGA colors, defining the basic colormap object...)
"""

import numpy as np

from matplotlib import cm
import matplotlib.colors as mplcol
from warnings import warn

from .sigproc import normalize


__all__ = ['color2vb', 'array2colormap', 'dynamic_color', 'color2faces',
           '_colormap', 'type_coloring', 'mpl_cmap'
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
    if (color is None) or isinstance(color, (str, tuple, np.ndarray)):
        # Default color :
        if color is None:
            coltuple = default
        # Static color :
        elif isinstance(color, (tuple, list, np.ndarray)):
            color = np.squeeze(color)
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
                                               dtype=np.float32)), axis=1)

        return vcolor.astype(np.float32)
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
    xm, xM = x.min(), x.max()

    # ---------------------------
    # Check clim :
    if (clim is None) or (clim is (None, None)):
        clim = (xm, xM)
    else:
        clim = list(clim)
        if len(clim) is not 2:
            raise ValueError("The length of the clim must be 2: (min, max)")
        else:
            if clim[0] is None:
                clim[0] = xm
            if clim[1] is None:
                clim[1] = xM

    # ---------------------------
    # Check (vmin, under) / (vmax, over) :
    if (vmin is None) or (under is None):
        vmin, under = None, None
    elif (vmin is not None) and (vmin < clim[0]):
        if (vmin < clim[0]) or (vmin > clim[1]):
            vmin, under = None, None
            warn("vmin must be between clim[0] and clim[1]. vmin will be "
                 "ignored")
    else:
        if not isinstance(under, (str, tuple)):
            raise ValueError("The under parameter must be a string referring "
                             "to a matplotlib color or a (R, G, B) tuple.")
    if (vmax is None) or (over is None):
        vmax, over = None, None
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

    # ---------------------------
    # Check alpha :
    if (alpha < 0) or (alpha > 1):
        warn("The alpha parameter must be >= 0 and <= 1.")

    # ================== Define colormap ==================
    sc = cm.ScalarMappable(cmap=cmap)

    # ================== Clip / Peak ==================
    # Force array to clip if x is under / over clim :
    if clim[0] > xm:
        x = colorclip(x, clim[0], kind='under')
    if clim[1] < xM:
        x = colorclip(x, clim[1], kind='over')

    # ================== Colormap (under, over) ==================
    # Set colormap (vmin, under) :
    if vmin is None:
        sc.set_clim(vmin=None)
    else:
        sc.set_clim(vmin=vmin)
        sc.cmap.set_under(color=under)
    # Set colormap (vmax, over) :
    if vmax is None:
        sc.set_clim(vmax=None)
    else:
        sc.set_clim(vmax=vmax)
        sc.cmap.set_over(color=over)
    # Fix limits :
    # norm = mplcol.Normalize(vmin=clim[0], vmax=clim[1])
    # sc.set_norm(norm)

    # ================== Apply colormap ==================
    # Apply colormap to x :
    x_cmap = np.array(sc.to_rgba(x, alpha=alpha))
    # Faces render (repeat the color to other dimensions):
    if faces_render:
        x_cmap = np.transpose(np.tile(x_cmap[..., np.newaxis],
                                      (1, 1, 3)), (0, 2, 1))

    return x_cmap.astype(np.float32)


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

    Args:
        x: np.ndarray
            Array of data.

        th: float
            The threshold to use.

    Kargs:
        kind: string, optional, (def: 'under')
            Use eiher 'under' or 'over' for fore the array to clip for every
            values respectively under or over th.

    Return:
        x: np.ndarray
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

    Arg:
        n: int
            The number of color to generate.
    Kargs:
        color: string/tuple/array, optional, (def: None)
            Choose how to color signals. Use None (or 'rnd', 'random') to
            generate random colors. Use 'uniform' (see the unicolor
            parameter) to define the same color for all signals. Use
            'dynamic' to have a dynamic color according to data values.

        n: int, optional, (def: 1)
            The number of colors to generate in case of random or uniform
            colors.

        data: np.ndarray, optional, (def: None)
            The data to convert into color if the color type is dynamic.
            If this parameter is ignored, a default linear spaced vector of
            length n will be used instead.

        rnd_dyn: tuple, optional, (def: (.3, .9))
            Define the dynamic of random color. This parameter is active
            only if the color parameter is turned to None (or 'rnd' /
            'random').

        cmap: string, optional, (def: inferno)
            Matplotlib colormap (parameter active for 'dyn_minmax' and
            'dyn_time' color).

        clim: tuple/list, optional, (def: None)
            Limit of the colormap. The clim parameter must be a tuple /
            list of two float number each one describing respectively the
            (min, max) of the colormap. Every values under clim[0] or over
            clim[1] will peaked (parameter active for 'dyn_minmax' and
            'dyn_time' color).

        alpha: float, optional, (def: 1.0)
            The opacity to use. The alpha parameter must be between 0 and 1
            (parameter active for 'dyn_minmax' and 'dyn_time' color).

        vmin: float, optional, (def: None)
            Threshold from which every color will have the color defined
            using the under parameter bellow (parameter active for
            'dyn_minmax' and 'dyn_time' color).

        under: tuple/string, optional, (def: 'gray')
            Matplotlib color for values under vmin (parameter active for
            'dyn_minmax' and 'dyn_time' color).

        vmax: float, optional, (def: None)
            Threshold from which every color will have the color defined
            using the over parameter bellow (parameter active for
            'dyn_minmax' and 'dyn_time' color).

        over: tuple/string, optional, (def: 'red')
            Matplotlib color for values over vmax (parameter active for
            'dyn_minmax' and 'dyn_time' color).

        unicolor: tuple/string, optional, (def: 'gray')
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
        # Generate a linearly spaced vecto for None data :
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

    Kargs:
        invert: bool, optional, (def: False)
            Get the list of inverted colormaps.

    Returns:
        cmap_lst: list
            list of avaible matplotlib colormaps.
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
