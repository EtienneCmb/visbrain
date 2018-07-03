"""Colorbar module."""
import sys
from PyQt5 import QtWidgets

import vispy.app as visapp

from .ui_init import UiInit
from ..visuals import CbarQt, CbarBase, CbarObjetcs


class Colorbar(UiInit):
    """Display a colorbar editor.

    Parameters
    ----------
    config : string | None
        Path to a configuration file.
    cmap : string | inferno
        Matplotlib colormap
    clim : tuple/list | None
        Limit of the colormap. The clim parameter must be a tuple / list
        of two float number each one describing respectively the (min, max)
        of the colormap. Every values under clim[0] or over clim[1] will
        peaked.
    vmin : float | None
        Threshold from which every color will have the color defined using
        the under parameter bellow.
    under : tuple/string | 'gray'
        Matplotlib color for values under vmin.
    vmax : float | None
        Threshold from which every color will have the color defined using
        the over parameter bellow.
    over : tuple/string | 'red'
        Matplotlib color for values over vmax.
    cblabel : string | ''
        Colorbar label.
    cbtxtsz : float | 26.
        Text size of the colorbar label.
    cbtxtsh : float | 2.3
        Shift for the colorbar label.
    txtcolor : string | 'white'
        Text color.
    txtsz : float | 20.
        Text size for clim/vmin/vmax text.
    txtsh : float | 1.2
        Shift for clim/vmin/vmax text.
    border : bool | True
        Display colorbar borders.
    limtxt : bool | True
        Display vmin/vmax text.
    bgcolor : tuple/string | (.1, .1, .1)
        Background color of the colorbar canvas.
    ndigits : int | 2
        Number of digits for the text.
    """

    def __init__(self, config=None, **kwargs):
        """Init."""
        # Manage isvmin / isvmax :
        if 'vmin' in list(kwargs.keys()) and (kwargs['vmin'] is not None):
            kwargs['isvmin'] = True
        if 'vmax' in list(kwargs.keys()) and (kwargs['vmax'] is not None):
            kwargs['isvmax'] = True
        # Create the app and initialize all graphical elements :
        self._app = QtWidgets.QApplication(sys.argv)
        # Initialise GUI :
        UiInit.__init__(self)

        cbobjs = CbarObjetcs()
        if isinstance(config, str):
            cbobjs.load(config)
        elif isinstance(config, dict):
            for k, i in config.items():
                cbobjs.add_object(k, CbarBase(**i), overwrite=False)
        else:
            if 'name' in kwargs.keys():
                name = kwargs['name']
                del kwargs['name']
            else:
                name = 'Colorbar'
            obj1 = CbarBase(**kwargs)
            cbobjs.add_object(name, obj1, overwrite=False)
        self.cbqt = CbarQt(self.guiW, self.vizW, cbobjs)
        self.cbqt._fcn_change_object(clean=True)

    def show(self):
        """Display the graphical user interface."""
        self.showMaximized()
        visapp.run()
