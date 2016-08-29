import numpy as np
from vispy.scene.visuals import ColorBar, Text
from vispy.color import Colormap

from ..utils import slider2opacity, array2colormap, color2vb


class CmapBase(object):

    """docstring for CmapBase"""

    def __init__(self, **kwargs):
        # Colormap elements :
        self.cmap = kwargs['cmap']
        self.cmap_vmin = kwargs['cmap_vmin']
        self.cmap_vmax = kwargs['cmap_vmax']
        self.cmap_under = kwargs['cmap_under']
        self.cmap_over = kwargs['cmap_over']

        # Colorbar elements :
        self.cbexport = kwargs['cb_export']
        self.cblength = 10
        self.cblabel = kwargs['cb_label']
        self.cbfontsize = kwargs['cb_fontsize']

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
        cmap = self.cbcolor(np.array([0,1]), self.cmap, length=self.cblength)

        # Create colorbar object :
        self.colorbarW = ColorBar(cmap=cmap, orientation='right', size=(40,5), label='', clim=('', ''),
                                  border_color="w", padding=-10, margin=-10, border_width=1)
        self.view.cbwc.add(self.colorbarW)

        # Create a more controlable text :
        self.cbminW = Text(text='', color='w', font_size=self.cbfontsize-2, pos=(4.5,20),anchor_x='left', anchor_y='center')
        self.cbmaxW = Text(text='', color='w', font_size=self.cbfontsize-2, pos=(4.5,-20-0.5), anchor_x='left', anchor_y='center')
        self.cblabelW = Text(text='', color='w', font_size=self.cbfontsize, pos=(6,0), rotation=-90, anchor_y='center', anchor_x='center')
        self.view.cbwc.add(self.cbminW)
        self.view.cbwc.add(self.cbmaxW)
        self.view.cbwc.add(self.cblabelW)

        # Set colorbar properties :
        self.set_cb(None, (0,1), self.cblabel, self.cbfontsize)


    def cbcolor(self, data, cmap, length=10, vmin=None, vmax=None, under=None, over=None):
        """
        """
        colval = np.linspace(data.min(), data.max(), num=length)
        colorbar = array2colormap(colval, vmin=vmin, vmax=vmax, under=under, over=over, cmap=cmap)
        return Colormap(np.flipud(colorbar))


    def cbupdate(self, data, cmap, vmin=None, vmax=None, under=None, over=None, label='', fontsize=20):
        """
        """
        # Get data colors :
        cmap = self.cbcolor(data, self.cmap, length=self.cblength, vmin=vmin,
                            vmax=vmax, under=under, over=over)
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
