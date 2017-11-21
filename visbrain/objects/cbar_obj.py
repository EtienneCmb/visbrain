"""Colorbar object."""
from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals import CbarArgs, CbarVisual


class ColorbarObj(VisbrainObject, CbarArgs):
    """Create a colorbar object.

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
    vmax : float | None
        Every values over vmin will have the color defined
        using the over parameter.
    under : tuple/string | None
        Matplotlib color under vmin.
    over : tuple/string | None
        Matplotlib color over vmax.
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

    def __init__(self, name, transform=None,
                 parent=None, verbose=None, **kwargs):
        """Init."""
        # Init Visbrain object base class and SourceProjection :
        if not isinstance(name, str):
            kwargs = self._update_cbar_from_obj(name, update=False, **kwargs)
            name = name.name + 'Cbar'  # that's a lot of name
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        self._cbar = CbarVisual(parent=self._node, **kwargs)

    def _get_camera(self):
        """Get a panzoom camera."""
        return scene.cameras.PanZoomCamera(rect=(-.7, -2, 1.5, 4))

    def _update_cbar_from_obj(self, obj, update=True, **kwargs):
        """Update colorbar from an object."""
        is_meth = hasattr(obj, 'to_kwargs') and callable(obj.to_kwargs)
        if is_meth:
            kw = obj.to_kwargs(True)
            if update:
                for name, val in kw.items():
                    exec('self._cbar._%s = val' % name)
                self._cbar._build()
            else:
                for name, val in kw.items():
                    kwargs[name] = val
                return kwargs
        else:
            raise ValueError("Can not get the colorbar of a %s "
                             "object" % type(obj).__name__)
