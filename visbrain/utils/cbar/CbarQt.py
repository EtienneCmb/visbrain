"""Mehods to manage interactions between the GUI and objects."""

from .CbarVisual import CbarVisual
from .gui import CbarForm
from ..guitools import color2json
from ..color import mpl_cmap, mpl_cmap_index

__all__ = ['CbarQt']


class CbarQt(object):
    """Link the GUI colorbar with the VisPy based colorbar.

    Args:
        guiW: PyQt widget
            The widget for adding the GUI colorar properties.

        vizW: PyQt widget
            The widget for adding the VisPy based colorbar.
    """

    def __init__(self, guiW, vizW):
        """Init."""
        # --------------------------------------------------------------------
        #                             GUI COMPONENTS
        # --------------------------------------------------------------------
        # Add colorbar properties to guiW :
        self.cbui = CbarForm()
        self.cbui.setupUi(guiW)
        # Add VisPy based colorbar :
        self.cbviz = CbarVisual()
        vizW.addWidget(self.cbviz._canvas.native)

        # --------------------------------------------------------------------
        #                             GUI INTERACTIONS
        # --------------------------------------------------------------------
        # _____________ SETTINGS _____________
        self['object'].currentIndexChanged.connect(self._fcn_ChangeObj)
        self['bckCol'].editingFinished.connect(self._fcn_BckCol)
        self['txtCol'].editingFinished.connect(self._fcn_TxtCol)
        self['digits'].valueChanged.connect(self._fcn_Digits)
        self['width'].valueChanged.connect(self._fcn_Width)
        self['border'].clicked.connect(self._fcn_Border)
        self['bw'].valueChanged.connect(self._fcn_Bw)
        self['limTxt'].clicked.connect(self._fcn_Limits)
        self['digits'].setKeyboardTracking(False)
        self['width'].setKeyboardTracking(False)

        # _____________ COLORMAPS _____________
        self._cmaps = mpl_cmap()
        self['cmap'].addItems(self._cmaps)
        idx, rev = mpl_cmap_index(self.cbviz.cmap)
        self['cmap'].setCurrentIndex(idx)
        self['cmapRev'].setChecked(rev)
        self['cmap'].currentIndexChanged.connect(self._fcn_cmapChanged)
        self['cmapRev'].clicked.connect(self._fcn_cmapChanged)

        # _____________ CLIM _____________
        self['climm'].valueChanged.connect(self._fcn_climchanged)
        self['climM'].valueChanged.connect(self._fcn_climchanged)
        self['climm'].setKeyboardTracking(False)
        self['climM'].setKeyboardTracking(False)

        # _____________ VMIN/VMAX _____________
        # Vmin :
        self['vminChk'].clicked.connect(self._fcn_vminChanged)
        self['vmin'].valueChanged.connect(self._fcn_vminChanged)
        self['under'].editingFinished.connect(self._fcn_vminChanged)
        self['vmin'].setKeyboardTracking(False)
        # Vmax :
        self['vmaxChk'].clicked.connect(self._fcn_vmaxChanged)
        self['vmax'].valueChanged.connect(self._fcn_vmaxChanged)
        self['over'].editingFinished.connect(self._fcn_vmaxChanged)
        self['vmax'].setKeyboardTracking(False)

        # _____________ TEXT _____________
        # Colorbar label :
        self['cblabel'].editingFinished.connect(self._fcn_CbTitle)
        self['cbTxtSz'].valueChanged.connect(self._fcn_cbTxtSize)
        self['cbTxtSh'].valueChanged.connect(self._fcn_cbTxtShift)
        self['cbTxtSz'].setKeyboardTracking(False)
        self['cbTxtSh'].setKeyboardTracking(False)
        # Limits label :
        self['txtSz'].valueChanged.connect(self._fcn_TxtSize)
        self['txtSh'].valueChanged.connect(self._fcn_TxtShift)
        self['txtSz'].setKeyboardTracking(False)
        self['txtSh'].setKeyboardTracking(False)

    def __getitem__(self, key):
        """Get the item from the GUI."""
        return eval('self.cbui.'+key)

    def __setitem__(self, key, value):
        """Set VisPy based colormap item from GUI properties."""
        if not isinstance(value, str):
            exec('self.cbviz.'+key+'='+str(value))
        else:
            exec("self.cbviz."+key+"='"+value+"'")

    ###########################################################################
    ###########################################################################
    #                              SETTINGS
    ###########################################################################
    ###########################################################################
    def _fcn_ChangeObj(self):
        """Change colorbar object."""
        raise NotImplementedError()

    def _fcn_BckCol(self):
        """Change background color."""
        self['bgcolor'] = color2json(self['bckCol'])

    def _fcn_TxtCol(self):
        """Change text color."""
        self['txtcolor'] = color2json(self['txtCol'])

    def _fcn_Digits(self):
        """Change the number of digits."""
        ndigits = self['digits'].value()
        if 0 < ndigits:
            self['ndigits'] = ndigits
            self['climm'].setDecimals(ndigits)
            self['climM'].setDecimals(ndigits)
            self['vmin'].setDecimals(ndigits)
            self['vmax'].setDecimals(ndigits)

    def _fcn_Width(self):
        """Change colorbar width."""
        self['width'] = self['width'].value()

    def _fcn_Border(self):
        """Set the border."""
        viz = self['border'].isChecked()
        self['border'] = viz
        self['bw'].setEnabled(viz)

    def _fcn_Bw(self):
        """Change border width."""
        self['bw'] = self['bw'].value()

    def _fcn_Limits(self):
        """Display/hide vmin/vmax."""
        self['limtxt'] = self['limTxt'].isChecked()

    ###########################################################################
    ###########################################################################
    #                              COLORMAP
    ###########################################################################
    ###########################################################################
    def _fcn_cmapChanged(self):
        """Change the colormap."""
        rv = self['cmapRev'].isChecked() * '_r'
        self['cmap'] = str(self['cmap'].currentText()) + rv

    ###########################################################################
    ###########################################################################
    #                              CLIM
    ###########################################################################
    ###########################################################################
    def _fcn_climchanged(self):
        """Update colorbar limits."""
        # Get value :
        climm = float(self['climm'].value())
        climM = float(self['climM'].value())
        # Update clim :
        self['clim'] = (climm, climM)

    ###########################################################################
    ###########################################################################
    #                              VMIN/VMAX
    ###########################################################################
    ###########################################################################
    def _fcn_vminChanged(self):
        """Change vmin/vmax/under/over."""
        isvmin = self['vminChk'].isChecked()
        # Enable/Disable panels :
        self['vminW'].setEnabled(isvmin)
        # Vmin :
        if isvmin:
            self['vmin'] = self['vmin'].value()
            self['under'] = color2json(self['under'])
        else:
            self['vmin'] = None

    def _fcn_vmaxChanged(self):
        """Change vmin/vmax/under/over."""
        isvmax = self['vmaxChk'].isChecked()
        self['vmaxW'].setEnabled(isvmax)
        # Vmax
        if isvmax:
            self['vmax'] = self['vmax'].value()
            self['over'] = color2json(self['over'])
        else:
            self['vmax'] = None

    ###########################################################################
    ###########################################################################
    #                              TEXT
    ###########################################################################
    ###########################################################################
    def _fcn_CbTitle(self):
        """Change colorbar title."""
        self['cblabel'] = str(self['cblabel'].text())

    def _fcn_cbTxtSize(self):
        """Change colorbar text size."""
        self['cbtxtsz'] = self['cbTxtSz'].value()

    def _fcn_cbTxtShift(self):
        """Change cblabel shift."""
        self['cbtxtsh'] = self['cbTxtSh'].value()

    def _fcn_TxtSize(self):
        """Change text size for limits."""
        self['txtsz'] = self['txtSz'].value()

    def _fcn_TxtShift(self):
        """Change text shift."""
        self['txtsh'] = self['txtSh'].value()
