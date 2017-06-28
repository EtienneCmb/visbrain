"""Base class for colormap managment.

- create a colorbar
- Update it with new color / settings
"""
from vispy.scene import Node

from ...utils import _colormap, color2vb, CbarVisual


class CbarBase(_colormap):
    """Colormap / colorbar main class.

    This class can be used to create a colorbar. The purpose of this colorbar
    is to visualize and control elements that need colors (like cortical
    projection / repartition, connectivity...).
    """

    def __init__(self, parent, cmap='viridis', clim=None, vmin=None, vmax=None,
                 under=None, over=None, cb_export=False, cb_fontsize=18,
                 cb_fontcolor='white', cb_label=''):
        """Init."""
        # Initialize colorbar elements :
        _colormap.__init__(self, cmap, clim, vmin, vmax, under, over)

        # Colorbar elements :
        self.cbwc = parent
        self._cb['export'] = cb_export
        self._cb['label'] = cb_label
        self._cb['fontsize'] = cb_fontsize
        self._cb['fontcolor'] = tuple(color2vb(cb_fontcolor).ravel()[0:-1])
        self._cb['length'] = 10
        # Create a colorbar node :
        self._cbNode = Node(name='cbNode')
        self._cbNode.parent = parent

        # Create the colorbar :
        self.cbcreate()

    def cbcreate(self):
        """Create a default colorbar between 0 and 1."""
        # ==================================================================
        # COLORBAR OBJECT
        # ==================================================================
        sz = self['fontsize']-2
        self.colorbarW = CbarVisual(parent=self._cbNode, cbtxtsz=sz, txtsz=sz,
                                    txtcolor=self._cb['fontcolor'])

    def cbupdate(self, data, cmap, clim=None, vmin=None, under=None, vmax=None,
                 over=None, label='', fontsize=20, fontcolor='white',
                 export=True, length=10):
        """Update the colorbar with data or color properties.

        Args:
            data: array
                Array of data. This array is used to automatically set the
                minimum and maximum of the colorbar.

            cmap: string, optional, (def: inferno)
                Matplotlib colormap.

        Kargs:
            clim: tuple/list, optional, (def: None)
                Limit of the colormap. The clim parameter must be a tuple /
                list of two float number each one describing respectively the
                (min, max) of the colormap. Every values under clim[0] or over
                clim[1] will peaked.

            vmin: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the under parameter bellow.

            under: tuple/string, optional, (def: None)
                Matplotlib color for values under vmin.

            vmax: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the over parameter bellow.

            over: tuple/string, optional, (def: None)
                Matplotlib color for values over vmax.

            label: string, optional, (def: '')
                Colorbar label / title.

            fontsize: int, optional, (def: 10)
                Font-size of the colorbar text (min / max / title).

            fontcolor: string, optional, (def: 'white')
                Font-color of the colorbar text (min / max / title).

            length: int, optional, (def: 10)
                Number of lines in the colorbar.

            export: bool, optional, (def: True)
                Export the colorbar during a screenshot.
        """
        # Set all values :
        self['cmap'] = cmap
        self['clim'] = clim
        self['vmin'], self['vmax'] = vmin, vmax
        self['under'], self['over'] = under, over

        self.colorbarW.cmap = cmap
        self.colorbarW.clim = clim
        self.colorbarW.cblabel = label
        self.colorbarW.cbtxtsz = fontsize
        self.colorbarW.txtsz = fontsize
        self.colorbarW.txtcolor = fontcolor
        self.colorbarW.vmin = vmin
        self.colorbarW.under = under
        self.colorbarW.vmax = vmax
        self.colorbarW.over = over
