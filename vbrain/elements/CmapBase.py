import numpy as np
from vispy.scene.visuals import ColorBar, Text
from vispy.color import Colormap

from ..utils import slider2opacity, array2colormap, color2vb, _colormap


class CmapBase(_colormap):

    """docstring for CmapBase
    """

    def __init__(self, parent, cmap='inferno', vmin=None, vmax=None, under=None, over=None, 
                 cb_export=False, cb_fontsize=15, cb_label='', **kwargs):

        # Initialize colorbar elements :
        _colormap.__init__(self, cmap, vmin, vmax, under, over)

        # Colorbar elements :
        self.cbwc = parent
        self._cb['export'] = cb_export
        self._cb['label'] = cb_label
        self._cb['fontsize'] = cb_fontsize
        self._cb['length'] = 10

        # Create the colorbar :
        self.cbcreate()


    # ***************************************************************
    # ***************************************************************
    # COLORBAR
    # ***************************************************************
    # ***************************************************************

    def cbcreate(self):
        """Create a default colorbar between 0 and 1
        """
        # Define colors :
        cmap = self.cbcolor(np.array([0,1]), length=self['length'])

        # Create colorbar object :
        self.colorbarW = ColorBar(cmap=cmap, orientation='right', size=(40,5), label='', clim=('', ''),
                                  border_color="w", padding=-10, margin=-10, border_width=1)
        self.cbwc.add(self.colorbarW)

        # Create a more controlable text :
        self.cbmaxW = Text(text='', color='w', font_size=self['fontsize']-2, pos=(4.5,20), anchor_x='left',
                           anchor_y='center')
        self.cbminW = Text(text='', color='w', font_size=self['fontsize']-2, pos=(4.5,-20-0.5), anchor_x='left',
                           anchor_y='center')
        self.cblabelW = Text(text='', color='w', font_size=self['fontsize'], pos=(6,0), rotation=-90,
                             anchor_y='center', anchor_x='center')
        self.cbwc.add(self.cbminW)
        self.cbwc.add(self.cbmaxW)
        self.cbwc.add(self.cblabelW)

        # Set colorbar properties :
        self.set_cb(None, (0,1), self['label'], self['fontsize'])


    def cbcolor(self, data, length=10):
        """
        """
        colval = np.linspace(data.min(), data.max(), num=length)
        colorbar = array2colormap(colval, vmin=self['vmin'], vmax=self['vmax'], under=self['under'],
                                  over=self['over'], cmap=self['cmap'])
        return Colormap(np.flipud(colorbar))


    def cbupdate(self, data, cmap, vmin=None, vmax=None, under=None, over=None, label='',
                 fontsize=20, export=True, length=10):
        """
        """
        # Set all values :
        self['cmap'] = cmap
        self['vmin'], self['vmax'] = vmin, vmax
        self['under'], self['over'] = under, over

        # Get data colors :
        cmap = self.cbcolor(data, length=length)

        # Update colorbar proerties :
        clim = (str(data.min()), str(data.max()))
        self.set_cb(cmap=cmap, clim=clim, label=label, fontsize=fontsize)


    def set_cb(self, cmap=None, clim=None, label=None, fontsize=None):
        """Update colorbar attributes :
        """
        if cmap is not None: self.colorbarW.cmap = cmap
        if clim is not None:
            self.cbminW.text = str(clim[0])
            self.cbmaxW.text = str(clim[1])
        if label is not None: self.cblabelW.text = label
        if fontsize is not None: self.colorbarW.label.font_size = fontsize
        # self.colorbarW.update()


