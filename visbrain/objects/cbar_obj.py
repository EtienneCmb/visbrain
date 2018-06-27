"""Colorbar object."""
import logging

from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals import CbarVisual

logger = logging.getLogger('visbrain')


class ColorbarObj(VisbrainObject):
    """Create a colorbar object.

    Parameters
    ----------
    name : str
        Name of the colorbar object. Alternatively, you can pass an other
        object (like BrainObj or SourceObj) to get their colorbar.
    rect : tuple | (-.7, -2, 1.5, 4)
        Camera rectangle. The `rect` input must be a tuple of four floats
        describing where the camera (start_x, start_y, length_x, length_y).
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
    width : float | 0.17
        Colorbar width.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Markers object parent.
    verbose : string
        Verbosity level.

    Notes
    -----
    List of supported shortcuts :

        * **s** : save the figure
        * **<delete>** : reset camera

    Examples
    --------
    >>> from visbrain.objects import ColorbarObj
    >>> cb = ColorbarObj('cbar', cmap='viridis', clim=(4., 78.2), vmin=10.,
    >>>                  vmax=72., cblabel='Colorbar title', under='gray',
    >>>                  over='red', txtcolor='black', cbtxtsz=40, cbtxtsh=2.,
    >>>                  txtsz=20., width=.04)
    >>> cb.preview()
    """

    def __init__(self, name, rect=(-.7, -2, 1.5, 4), transform=None,
                 parent=None, verbose=None, **kwargs):
        """Init."""
        # Init Visbrain object base class and SourceProjection :
        if not isinstance(name, str):
            kwargs = self._update_cbar_from_obj(name, update=False, **kwargs)
            if hasattr(name, '_default_cblabel') and (
                    'cblabel' not in kwargs.keys()):
                kwargs['cblabel'] = name._default_cblabel
            name = name.name + 'Cbar'  # that's a lot of name
        kwargs['isvmin'] = kwargs.get('vmin', None) is not None
        kwargs['isvmax'] = kwargs.get('vmax', None) is not None
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        self._cbar = CbarVisual(parent=self._node, **kwargs)
        assert len(rect) == 4
        self._rect = rect

    def _get_camera(self):
        """Get a panzoom camera."""
        return scene.cameras.PanZoomCamera(rect=self._rect)

    def _update_cbar_from_obj(self, obj, update=True, **kwargs):
        """Update colorbar from an object."""
        is_meth = hasattr(obj, 'to_dict') and callable(obj.to_dict)
        if is_meth:
            logger.info("Get colorbar properties from %s object" % repr(obj))
            # Get object cbar properties :
            kw = obj.to_dict()
            if update:  # Update the colorbar visual
                for name, val in kw.items():
                    exec('self._cbar._%s = val' % name)
                self._cbar._build()
            for name, val in kwargs.items():
                kw[name] = val
            return kw
        else:
            raise ValueError("Can not get the colorbar of a %s "
                             "object" % type(obj).__name__)
