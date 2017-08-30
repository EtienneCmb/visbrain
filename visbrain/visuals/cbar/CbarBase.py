"""Most basic colorbar class."""
from ...utils import color2tuple

__all__ = ('CbarArgs', 'CbarBase')


class CbarArgs(object):
    """Manage the different inputs for the colormap creation.

    Parameters
    ----------
    cmap : string | None
        Matplotlib colormap (like 'viridis', 'inferno'...).
    clim : tuple/list | None
        Colorbar limit. Every values under / over clim will
        clip.
    isvmin : bool | False
        Activate/deactivate vmin.
    vmin : float | None
        Every values under vmin will have the color defined
        using the under parameter.
    isvmax : bool | False
        Activate/deactivate vmax.
    vmax : float | None
        Every values over vmin will have the color defined
        using the over parameter.
    under : tuple/string | None
        Matplotlib color under vmin.
    over : tuple/string | None
        Matplotlib color over vmax.
    """

    def __init__(self, cmap=None, clim=None, isvmin=False, vmin=None,
                 isvmax=False, vmax=None, under=None, over=None):
        """Init."""
        # Cmap/Clim/Vmin/Vmax/Under/Over :
        self._cmap, self._clim = cmap, clim
        self._vmin, self._vmax = vmin, vmax
        self._isvmin, self._isvmax = isvmin, isvmax
        self._under, self._over = under, over

    def to_kwargs(self, addisminmax=False):
        """Return a dictionary for input arguments.

        Parameters
        ----------
        addisminmax : bool | False
            Specify if the returned dictionary have to had the ismin and
            ismax variables.
        """
        kwargs = {}
        kwargs['cmap'] = self._cmap
        kwargs['clim'] = self._clim
        kwargs['vmin'] = self._vmin if self._isvmin else None
        kwargs['under'] = self._under
        kwargs['vmax'] = self._vmax if self._isvmax else None
        kwargs['over'] = self._over
        if addisminmax:
            kwargs['isvmin'], kwargs['isvmax'] = self._isvmin, self._isvmax
        return kwargs

    def update_from_dict(self, kwargs):
        """Update attributes from a dictionary."""
        for k, i in kwargs.items():
            if not isinstance(i, str):
                exec('self._' + k + '=' + str(i))
            else:
                exec("self._" + k + "='" + str(i) + "'")


class CbarBase(CbarArgs):
    """Base class for colorbar.

    Parameters
    ----------
    cblabel : string | ''
        Colorbar label.
    cbtxtsz : float | 5..
        Text size of the colorbar label.
    cbtxtsh : float | 2.3
        Shift for the colorbar label.
    txtcolor : string | 'white'
        Text color.
    txtsz : float | 3.
        Text size for clim/vmin/vmax text.
    txtsh : float | 1.2
        Shift for clim/vmin/vmax text.
    border : bool | True
        Display colorbar borders.
    bw : float | 2.
        Border width.
    limtxt : bool | True
        Display vmin/vmax text.
    bgcolor : tuple/string | (0., 0., 0.)
        Background color of the colorbar canvas.
    ndigits : int | 2
        Number of digits for the text.
    """

    def __init__(self, cmap='viridis', clim=(0, 1), vmin=None, isvmin=False,
                 vmax=None, isvmax=False, under='gray', over='red', cblabel='',
                 cbtxtsz=5., cbtxtsh=2.3, txtcolor='white', txtsz=3.,
                 txtsh=1.2, width=.17, border=True, bw=2., limtxt=True,
                 bgcolor=(0., 0., 0.), ndigits=2, minmax=None, fcn=None,
                 minmaxfcn=None):
        """Init."""
        CbarArgs.__init__(self, cmap, clim, isvmin, vmin, isvmax, vmax, under,
                          over)
        # Cb text :
        self._cblabel = cblabel
        self._cbtxtsz = cbtxtsz
        self._cbtxtsh = cbtxtsh
        # Text :
        self._txtcolor = txtcolor
        self._txtsz = txtsz
        self._txtsh = txtsh
        self._limtxt = limtxt
        # Settings :
        self._bgcolor = bgcolor
        self._border = border
        self._bw = bw
        self._ndigits = ndigits
        self._width = width
        if fcn is None:
            def fcn():
                pass
        self._fcn = fcn
        if minmaxfcn is None:
            def minmaxfcn():
                pass
        self._minmaxfcn = minmaxfcn

    def __getitem__(self, key):
        """Get item (usefull for CbarObjects)."""
        return eval('self._' + key)

    def __setitem__(self, key, value):
        """Set self items."""
        if not isinstance(value, str):
            exec("self._" + key + "=" + str(value))
        else:
            exec("self._" + key + "='" + value + "'")

    # -------------------------------------------------------------------------
    #                             USER METHODS
    # -------------------------------------------------------------------------
    def to_dict(self):
        """Return a dictionary of all colorbar args."""
        todict = {}
        # cmap/clim/vmin/vmax/under/over :
        todict['cmap'] = self._cmap
        todict['clim'] = [float(k) for k in self._clim]
        todict['isvmin'] = self._isvmin
        todict['vmin'] = self._vmin
        todict['under'] = list(color2tuple(self._under, float))
        todict['isvmax'] = self._isvmax
        todict['vmax'] = self._vmax
        todict['over'] = list(color2tuple(self._over, float))
        # Cblabel :
        todict['cblabel'] = self._cblabel
        todict['cbtxtsz'] = float(self._cbtxtsz)
        todict['cbtxtsh'] = float(self._cbtxtsh)
        # Text :
        todict['txtcolor'] = list(color2tuple(self._txtcolor, float))
        todict['txtsz'] = float(self._txtsz)
        todict['txtsh'] = float(self._txtsh)
        # Settings :
        todict['border'] = self._border
        todict['bw'] = float(self._bw)
        todict['limtxt'] = self._limtxt
        todict['bgcolor'] = list(color2tuple(self._bgcolor, float))
        todict['ndigits'] = int(self._ndigits)
        todict['width'] = float(self._width)

        return todict

    def update(self):
        """Fonction to run when an update is needed."""
        if self._fcn is not None:
            self._fcn()
        else:
            raise ValueError("No updating function found.")
