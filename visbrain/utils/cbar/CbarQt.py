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

        self['object'].addItems(self.cbobjs.keys())
        self._initialize()
        self._connect()

    def __getitem__(self, key):
        """Get the item from the GUI."""
        return eval('self.cbui.'+key)

    def __setitem__(self, key, value):
        """Set VisPy based colormap item from GUI properties."""
        if not isinstance(value, str):
            exec('self.cbviz.'+key+'='+str(value))
        else:
            exec("self.cbviz."+key+"='"+value+"'")

    def _initialize(self):
        # _____________ SETTINGS _____________
        self['bckCol'].setText(str(self.cbobjs['bgcolor']))
        self['txtCol'].setText(str(self.cbobjs['txtcolor']))
        self['ndigits'].setValue(self.cbobjs['ndigits'])
        self['width'].setValue(self.cbobjs['width'])
        self['border'].setChecked(self.cbobjs['border'])
        self['bw'].setValue(self.cbobjs['bw'])
        self['limTxt'].setChecked(self.cbobjs['limtxt'])

        # _____________ COLORMAPS _____________
        self['cmap'].clear()
        self._cmaps = mpl_cmap()
        self['cmap'].addItems(self._cmaps)
        idx, rev = mpl_cmap_index(self.cbobjs['cmap'])
        self['cmap'].setCurrentIndex(idx)
        self['cmapRev'].setChecked(rev)

        # _____________ CLIM _____________
        self['climm'].setValue(self.cbobjs['clim'][0])
        self['climM'].setValue(self.cbobjs['clim'][1])

        # _____________ VMIN/VMAX _____________
        # Set vmin/vmax limits :
        self._vminvmaxCheck()
        # Vmin/under :
        if self.cbobjs['vmin']:
            self['vmin'].setValue(self.cbobjs['vmin'])
        else:
            self['vminChk'].setChecked(False)
        self['under'].setText(str(self.cbobjs['under']))
        # Vmax/over :
        if self.cbobjs['vmax']:
            self['vmax'].setValue(self.cbobjs['vmax'])
        else:
            self['vmaxChk'].setChecked(False)
        self['over'].setText(str(self.cbobjs['over']))

        # _____________ TEXT _____________
        # Colorbar :
        self['cblabel'].setText(str(self.cbobjs['cblabel']))
        self['cbTxtSz'].setValue(self.cbobjs['cbtxtsz'])
        self['cbTxtSh'].setValue(self.cbobjs['cbtxtsh'])
        # Text limits :
        self['txtSz'].setValue(self.cbobjs['txtsz'])
        self['txtSh'].setValue(self.cbobjs['txtsh'])

        self._gui2visual()

    def _gui2visual(self):
        # Settings :
        self._fcn_BckCol()
        self._fcn_TxtCol()
        self._fcn_Digits()
        self._fcn_Width()
        self._fcn_Border()
        self._fcn_Bw()
        self._fcn_Limits()
        # Clim/Vmin/Vmax :
        self._fcn_climchanged()
        self._fcn_vminChanged()
        self._fcn_vmaxChanged()
        # Text :
        self._fcn_CbTitle()
        self._fcn_cbTxtSize()
        self._fcn_cbTxtShift()
        self._fcn_TxtSize()
        self._fcn_TxtShift()

    def _connect(self):
        """Connect cbui to cbviz."""
        # --------------------------------------------------------------------
        #                             GUI INTERACTIONS
        # --------------------------------------------------------------------
        # _____________ SETTINGS _____________
        self['object'].currentIndexChanged.connect(self._fcn_ChangeObj)
        self['bckCol'].editingFinished.connect(self._fcn_BckCol)
        self['txtCol'].editingFinished.connect(self._fcn_TxtCol)
        self['ndigits'].valueChanged.connect(self._fcn_Digits)
        self['width'].valueChanged.connect(self._fcn_Width)
        self['border'].clicked.connect(self._fcn_Border)
        self['bw'].valueChanged.connect(self._fcn_Bw)
        self['limTxt'].clicked.connect(self._fcn_Limits)
        self['ndigits'].setKeyboardTracking(False)
        self['width'].setKeyboardTracking(False)

        # _____________ COLORMAPS _____________
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

    def _disconnect(self):
        # Settings :
        self['object'].disconnect()
        self['bckCol'].disconnect()
        self['txtCol'].disconnect()
        self['ndigits'].disconnect()
        self['width'].disconnect()
        self['border'].disconnect()
        self['bw'].disconnect()
        self['limTxt'].disconnect()
        # Cmap :
        self['cmap'].disconnect()
        self['cmapRev'].disconnect()
        # Clim :
        self['climm'].disconnect()
        self['climM'].disconnect()
        # Vmin/Vmax/Under/Over :
        self['vminChk'].disconnect()
        self['vmin'].disconnect()
        self['under'].disconnect()
        self['vmaxChk'].disconnect()
        self['vmax'].disconnect()
        self['over'].disconnect()
        # Text :
        self['cblabel'].disconnect()
        self['cbTxtSz'].disconnect()
        self['cbTxtSh'].disconnect()
        self['txtSz'].disconnect()
        self['txtSh'].disconnect()

    ###########################################################################
    ###########################################################################
    #                              SETTINGS
    ###########################################################################
    ###########################################################################
    def _fcn_ChangeObj(self, *args, clean=False):
        """Change colorbar object."""
        # Disconnect interactions :
        self._disconnect()
        # Clean drowdown box for object selection :
        if clean:
            self['object'].clear()
            self['object'].addItems(self.cbobjs.keys())
        # Get the current selected text :
        name = str(self['object'].currentText())
        # Select this object :
        self.cbobjs.select(name)
        # Update GUI :
        self._initialize()
        # Re-connect interactions :
        self._connect()

    def _fcn_BckCol(self):
        """Change background color."""
        bgcolor = color2json(self['bckCol'])
        self['bgcolor'] = bgcolor
        self.cbobjs['bgcolor'] = self.cbviz.bgcolor

    def _fcn_TxtCol(self):
        """Change text color."""
        txtcolor = color2json(self['txtCol'])
        self['txtcolor'] = txtcolor
        self.cbobjs['txtcolor'] = self.cbviz.txtcolor

    def _fcn_Digits(self):
        """Change the number of digits."""
        ndigits = self['ndigits'].value()
        if 0 < ndigits:
            self['ndigits'] = ndigits
            self.cbobjs['ndigits'] = self.cbviz.ndigits
            self['climm'].setDecimals(ndigits)
            self['climM'].setDecimals(ndigits)
            self['vmin'].setDecimals(ndigits)
            self['vmax'].setDecimals(ndigits)

    def _fcn_Width(self):
        """Change colorbar width."""
        self['width'] = self['width'].value()
        self.cbobjs['width'] = self.cbviz.width

    def _fcn_Border(self):
        """Set the border."""
        viz = self['border'].isChecked()
        self['border'] = viz
        self.cbobjs['border'] = self.cbviz.border
        self['bw'].setEnabled(viz)

    def _fcn_Bw(self):
        """Change border width."""
        self['bw'] = self['bw'].value()
        self.cbobjs['bw'] = self.cbviz.bw

    def _fcn_Limits(self):
        """Display/hide vmin/vmax."""
        self['limtxt'] = self['limTxt'].isChecked()
        self.cbobjs['limtxt'] = self.cbviz.limtxt

    ###########################################################################
    ###########################################################################
    #                              COLORMAP
    ###########################################################################
    ###########################################################################
    def _fcn_cmapChanged(self):
        """Change the colormap."""
        rv = self['cmapRev'].isChecked() * '_r'
        self['cmap'] = str(self['cmap'].currentText()) + rv
        self.cbobjs['cmap'] = self.cbviz.cmap

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
        self.cbobjs['clim'] = self.cbviz.clim
        # Update vmin/vmax limits :
        self._vminvmaxCheck()

    ###########################################################################
    ###########################################################################
    #                              VMIN/VMAX
    ###########################################################################
    ###########################################################################
    def _vminvmaxCheck(self):
        """Activate checkboxs if vmin/vmax not None."""
        if isinstance(self.cbobjs['vmin'], (int, float)):
            self['vminChk'].setChecked(True)
        if isinstance(self.cbobjs['vmax'], (int, float)):
            self['vmaxChk'].setChecked(True)
        climm = float(self['climm'].value())
        climM = float(self['climM'].value())
        # Define step :
        step = (climM - climm) / 100.
        self['vmin'].setMinimum(climm)
        self['vmin'].setMaximum(climM)
        self['vmin'].setSingleStep(step)
        self['vmax'].setMinimum(climm)
        self['vmax'].setMaximum(climM)
        self['vmax'].setSingleStep(step)

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
        self.cbobjs['vmin'] = self.cbviz.vmin
        self.cbobjs['under'] = self.cbviz.under

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
        self.cbobjs['vmax'] = self.cbviz.vmax
        self.cbobjs['over'] = self.cbviz.over

    ###########################################################################
    ###########################################################################
    #                              TEXT
    ###########################################################################
    ###########################################################################
    def _fcn_CbTitle(self):
        """Change colorbar title."""
        self['cblabel'] = str(self['cblabel'].text())
        self.cbobjs['cblabel'] = self.cbviz.cblabel

    def _fcn_cbTxtSize(self):
        """Change colorbar text size."""
        self['cbtxtsz'] = self['cbTxtSz'].value()
        self.cbobjs['cbtxtsz'] = self.cbviz.cbtxtsz

    def _fcn_cbTxtShift(self):
        """Change cblabel shift."""
        self['cbtxtsh'] = self['cbTxtSh'].value()
        self.cbobjs['cbtxtsh'] = self.cbviz.cbtxtsh

    def _fcn_TxtSize(self):
        """Change text size for limits."""
        self['txtsz'] = self['txtSz'].value()
        self.cbobjs['txtsz'] = self.cbviz.txtsz

    def _fcn_TxtShift(self):
        """Change text shift."""
        self['txtsh'] = self['txtSh'].value()
        self.cbobjs['txtsh'] = self.cbviz.txtsh
