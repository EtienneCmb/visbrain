
import sys
from PyQt5 import QtWidgets

import vispy.app as visapp

from .uiInit import uiInit
from .uiMenu import uiMenu
from .uiInteract import uiInteract
from ..utils import CbarVisual, CbarObjetcs


class Colorbar(uiInit, uiInteract, uiMenu):
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
        uiMenu.__init__(self)

        # Enable control of multiple colorbar objects :
        self.objs = CbarObjetcs()

        # Create the colorbar object and add it to the GUI :
        if config is None:
            self.cb = CbarVisual(**kwargs)
            self.objs.add_object(**self.cb.to_dict())
        else:
            self.cb = CbarVisual()
            self.loadConfig(config)
        self.CbarLayout.addWidget(self.cb._canvas.native)

        # Set colorbar values to the GUI :
        self._cb2GUI()
        self._fcn_Name()

        # Initialize GUI interactions :
        uiInteract.__init__(self)

        # Latest updates of the colorbar :
        self._initialize()

    def add_colorbar(self, title, **kwargs):
        kwargs['name'] = title
        self.objs.add_object(**kwargs)
        self._fcn_Name()

    def show(self):
        """Display the graphical user interface."""
        self.showMaximized()
        visapp.run()
