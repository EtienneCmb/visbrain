"""Base class for colormap managment.

- create a colorbar
- Update it with new color / settings
"""

import numpy as np

from vispy.scene.visuals import ColorBar, Text
from vispy.color import Colormap

from ...utils import array2colormap, _colormap, color2vb


class CbarBase(_colormap):
    """Colormap / colorbar main class.

    This class can be used to create a colorbar. The purpose of this colorbar
    is to visualize and control elements that need colors (like cortical
    projection / repartition, connectivity...).
    """

    def __init__(self, parent, cmap='viridis', clim=None, vmin=None, vmax=None,
                 under=None, over=None, cb_export=False, cb_fontsize=15,
                 cb_fontcolor='w', cb_label='', **kwargs):
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

        # Create the colorbar :
        self.cbcreate()

    def cbcreate(self):
        """Create a default colorbar between 0 and 1."""
        # Define colors :
        cmap = self.cbcolor(np.array([0, 1]), length=self['length'])

        # ==================================================================
        # COLORBAR OBJECT
        # ==================================================================
        self.colorbarW = ColorBar(cmap=cmap, orientation='right', size=(40, 5),
                                  label='', clim=('', ''), border_color="w",
                                  padding=-10, margin=-10, border_width=1)
        self.cbwc.add(self.colorbarW)

        # ==================================================================
        # COLORBAR TEXT
        # ==================================================================
        # Colorbar maximum :
        self.cbmaxW = Text(text='', color=self._cb['fontcolor'],
                           font_size=self['fontsize']-2, pos=(4.5, 20),
                           anchor_x='left', anchor_y='center')
        self.cbwc.add(self.cbmaxW)
        # Colorbar minimum :
        self.cbminW = Text(text='', color=self._cb['fontcolor'],
                           font_size=self['fontsize']-2, pos=(4.5, -20-0.5),
                           anchor_x='left', anchor_y='center')
        self.cbwc.add(self.cbminW)
        # Colorbar label :
        self.cblabelW = Text(text='', color=self._cb['fontcolor'],
                             font_size=self['fontsize'], pos=(6, 0),
                             rotation=-90, anchor_y='center',
                             anchor_x='center')
        self.cbwc.add(self.cblabelW)

        # ==================================================================
        # COLORBAR PROPERTIES
        # ==================================================================
        self.set_cb(None, (0, 1), self['label'], self['fontsize'],
                    self['fontcolor'])

    def cbcolor(self, data, length=10):
        """Set the color of the colorbar.

        Args:
            data: array
                Array of data. This array is used to automatically set the
                minimum and maximum of the colorbar.

        Kargs:
            length: int, optional, (def: 10)
                Length of the colorbar lines.

        Return:
            cmap: vispy colormap
                The vispy colormap to use to create the colorbar.
        """
        # Define a vector of linearly spaced values :
        try:
            colval = np.linspace(self['clim'][0], self['clim'][1], num=length)
        except:
            colval = np.linspace(data.min(), data.max())
        # Turn the colval vector into a RGB array of colors. The clim parameter
        # is not usefull here :
        colorbar = array2colormap(colval, vmin=self['vmin'], vmax=self['vmax'],
                                  under=self['under'], over=self['over'],
                                  cmap=self['cmap'], clim=None)
        # Use the Colormap function of vispy to create a colormap :
        cmap = Colormap(np.flipud(colorbar))

        return cmap

    def cbupdate(self, data, cmap, clim=None, vmin=None, under=None, vmax=None,
                 over=None, label='', fontsize=20, fontcolor='w', export=True,
                 length=10):
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

            fontcolor: string, optional, (def: 'w')
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

        # Get data colors :
        cmap = self.cbcolor(data, length=length)

        # Update colorbar proerties :
        clim = (str(clim[0]), str(clim[1]))
        self.set_cb(cmap=cmap, clim=clim, label=label, fontsize=fontsize,
                    fontcolor=fontcolor)

    def set_cb(self, cmap=None, clim=None, label='', fontsize=None,
               fontcolor='w'):
        """Set some colorbar properties.

        Kargs:
            clim: tuple/list, optional, (def: None)
                Limit of the colormap. The clim parameter must be a tuple /
                list of two float number each one describing respectively the
                (min, max) of the colormap. Every values under clim[0] or over
                clim[1] will peaked.

            label: string, optional, (def: '')
                Colorbar label / title.

            fontsize: int, optional, (def: 10)
                Font-size of the colorbar text (min / max / title).

            fontcolor: string, optional, (def: 'w')
                Font-color of the colorbar text (min / max / title).
        """
        if cmap is not None:
            self.colorbarW.cmap = cmap
        if clim is not None:
            self.cbminW.text = str(clim[0])
            self.cbmaxW.text = str(clim[1])
        if label is not None:
            self.cblabelW.text = label
        if fontsize is not None:
            self.colorbarW.label.font_size = fontsize
        if fontcolor is not None:
            color = tuple(color2vb(fontcolor).ravel()[0:-1])
            self.colorbarW.label.color = color
            self.cbminW.color = color
            self.cbmaxW.color = color
        # self.colorbarW.update()
