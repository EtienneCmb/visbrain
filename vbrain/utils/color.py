import numpy as np

from matplotlib.cm import ScalarMappable
import matplotlib.colors as mplcol
from warnings import warn


__all__ = ['color2vb', 'array2colormap']


def color2vb(color=None, default=(1,1,1), length=1, alpha=1.0):
    """Tranform a tuple of RGB, matplotlib color or an
    hexadecimal color to an array of RGBA colors

    Kargs:
        color: None, tuple, string (def: None)
            The color to use. Can either be None, or a tuple (R, G, B),
            a matplotlib color or an hexadecimal color '#...'

        default: tuple, (def: (1,1,1))
            The default color to use instead.

        length: int (def: 10)
            The length of the output

        alpha: float, (def: 1)
            The opacity

    Return:
        vcolor: array
            Array of RGBA colors of shape (length, 4)
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
                                 alpha*np.ones((length, 1), dtype=float)), axis=1)

        return vcolor
    else:
        raise ValueError(str(type(color))+" is not a recognized type of color. "
                         "Use None, tuple or string")



def array2colormap(x, cmap='inferno', alpha=1.0, vmin=None, vmax=None,
                   under='dimgray', over='darkred'):
    """Transform an array of data to colormap (array of RGBA)

    Args:
        x: array
            Array of data

    Kargs:
        cmap: string (def: inferno)
            Matplotlib colormap

        alpha: float, (def: 1.0)
            The opcaity

        vmin: float (def: None)
            Minimum of the colormap

        vmax: float (def: None)
            Maximum of the colormap

        under: tuple/string (def: 'dimgray')
            Matplotlib color under vmin

        over: tuple/string (def: 'darkred')
            Matplotlib color over vmax

    Return:
        color: array
            Array of RGBA colors
    """
    # Check vmin/vmax :
    if (vmin is not None) and (vmax is not None) and (vmax < vmin):
        v = vmin
        vmax = vmin
        vmin = v
    # Normalize x :
    xM = np.abs(x).max()
    x = x/xM
    # Define the colormap :
    cm = ScalarMappable(cmap=cmap)
    # Set clim :
    if vmin is not None:
        if vmin > xM:
            vmin = x.min()
        vmin /= xM
    else:
        under = None
    if vmax is not None:
        if vmax < x.min():
            vmax = xm
        vmax /= xM
    else:
        over = None
    cm.set_clim(vmin=vmin, vmax=vmax)
    # Under/over the colorbar :
    if under is not None:
        cm.cmap.set_under(color=under)
    if over is not None:
        cm.cmap.set_over(color=over)
    return np.array(cm.to_rgba(x, alpha=alpha))

