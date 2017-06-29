
import sys
from PyQt5 import QtWidgets

import vispy.app as visapp

from .uiInit import uiInit
from ..utils import CbarQt, CbarBase, CbarObjetcs


class Colorbar(uiInit, CbarQt):
    """Display a colorbar editor.

    Kargs:
        config: string, optional, (def: None)
            Path to a configuration file.

        cmap: string, optional, (def: inferno)
            Matplotlib colormap

        clim: tuple/list, optional, (def: None)
            Limit of the colormap. The clim parameter must be a tuple / list
            of two float number each one describing respectively the (min, max)
            of the colormap. Every values under clim[0] or over clim[1] will
            peaked.

        vmin: float, optional, (def: None)
            Threshold from which every color will have the color defined using
            the under parameter bellow.

        under: tuple/string, optional, (def: 'gray')
            Matplotlib color for values under vmin.

        vmax: float, optional, (def: None)
            Threshold from which every color will have the color defined using
            the over parameter bellow.

        over: tuple/string, optional, (def: 'red')
            Matplotlib color for values over vmax.

        cblabel: string, optional, (def: '')
            Colorbar label.

        cbtxtsz: float, optional, (def: 26.)
            Text size of the colorbar label.

        cbtxtsh: float, optional, (def: 2.3)
            Shift for the colorbar label.

        txtcolor: string, optional, (def: 'white')
            Text color.

        txtsz: float, optional, (def: 20.)
            Text size for clim/vmin/vmax text.

        txtsh: float, optional, (def: 1.2)
            Shift for clim/vmin/vmax text.

        border: bool, optional, (def: True)
            Display colorbar borders.

        limtxt: bool, optional, (def: True)
            Display vmin/vmax text.

        bgcolor: tuple/string, optional, (def: (.1, .1, .1))
            Background color of the colorbar canvas.

        ndigits: int, optional, (def: 2)
            Number of digits for the text.
    """

    def __init__(self, config=None, **kwargs):
        """Init."""
        # Create the app and initialize all graphical elements :
        self._app = QtWidgets.QApplication(sys.argv)
        # Initialise GUI :
        uiInit.__init__(self)

        obj1 = CbarBase(cmap='jet', vmin=-31, vmax=33, clim=(-32, 37), bgcolor='green', cblabel='OKiii !')
        obj2 = CbarBase(cmap='viridis', vmin=2, vmax=4, clim=(21, 23))
        self.cbobjs = CbarObjetcs()
        self.cbobjs.add_object('obj1', obj1)
        self.cbobjs.add_object('obj2', obj2, overwrite=False)
        self.cbobjs.select('obj1')

        CbarQt.__init__(self, self.guiW, self.vizW)

    def show(self):
        """Display the graphical user interface."""
        self.showMaximized()
        visapp.run()
