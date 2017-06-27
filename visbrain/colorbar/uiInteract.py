from ..utils import (mpl_cmap, mpl_cmap_index, textline2color, color2vb,
                     color2tuple)

__all__ = ['uiInteract']


class uiInteract(object):
    """docstring for uiInteract"""

    def __init__(self):
        """Init."""
        self._connect()

    def _connect(self):
        # _____________ SETTINGS _____________
        self.cbObject.currentIndexChanged.connect(self._fcn_ChangeObj)
        self.cbBckCol.editingFinished.connect(self._fcn_BckCol)
        self.cbTxtCol.editingFinished.connect(self._fcn_TxtCol)
        self.cbDigits.valueChanged.connect(self._fcn_Digits)
        self.cbWidth.valueChanged.connect(self._fcn_Width)
        self.cbBorder.clicked.connect(self._fcn_Border)
        self.cbBw.valueChanged.connect(self._fcn_Bw)
        self.cbLimTxt.clicked.connect(self._fcn_Limits)
        self.cbDigits.setKeyboardTracking(False)
        self.cbWidth.setKeyboardTracking(False)

        # _____________ COLORMAPS _____________
        self._cmaps = mpl_cmap()
        self.cbCmap.addItems(self._cmaps)
        idx, rev = mpl_cmap_index(self.cb.cmap)
        self.cbCmap.setCurrentIndex(idx)
        self.cbCmapRev.setChecked(rev)
        self.cbCmap.currentIndexChanged.connect(self._fcn_cmapChanged)
        self.cbCmapRev.clicked.connect(self._fcn_cmapChanged)

        # _____________ CLIM _____________
        self.cbClimm.valueChanged.connect(self._fcn_climchanged)
        self.cbClimM.valueChanged.connect(self._fcn_climchanged)
        self.cbClimm.setKeyboardTracking(False)
        self.cbClimM.setKeyboardTracking(False)

        # _____________ VMIN/VMAX _____________
        # Vmin :
        self.cbVminChk.clicked.connect(self._fcn_vminChanged)
        self.cbVminVal.valueChanged.connect(self._fcn_vminChanged)
        self.cbVminUnder.editingFinished.connect(self._fcn_vminChanged)
        self.cbVminVal.setKeyboardTracking(False)
        # Vmax :
        self.cbVmaxChk.clicked.connect(self._fcn_vmaxChanged)
        self.cbVmaxVal.valueChanged.connect(self._fcn_vmaxChanged)
        self.cbVmaxOver.editingFinished.connect(self._fcn_vmaxChanged)
        self.cbVmaxVal.setKeyboardTracking(False)

        # _____________ TEXT _____________
        # Colorbar label :
        self.cbCblabel.editingFinished.connect(self._fcn_CbTitle)
        self.cbCbTxtSz.valueChanged.connect(self._fcn_cbTxtSize)
        self.cbCbTxtSh.valueChanged.connect(self._fcn_cbTxtShift)
        self.cbCbTxtSz.setKeyboardTracking(False)
        self.cbCbTxtSh.setKeyboardTracking(False)
        # Limits label :
        self.cbTxtSz.valueChanged.connect(self._fcn_TxtSize)
        self.cbTxtSh.valueChanged.connect(self._fcn_TxtShift)
        self.cbTxtSz.setKeyboardTracking(False)
        self.cbTxtSh.setKeyboardTracking(False)

    def _disconnect(self):
        # Settings :
        self.cbObject.disconnect()
        self.cbBckCol.disconnect()
        self.cbTxtCol.disconnect()
        self.cbDigits.disconnect()
        self.cbWidth.disconnect()
        self.cbBorder.disconnect()
        self.cbBw.disconnect()
        self.cbLimTxt.disconnect()
        # Cmap :
        self.cbCmap
        self.cbCmapRev
        # Clim :
        self.cbClimm.disconnect()
        self.cbClimM.disconnect()
        # Vmin/Vmax/Under/Over :
        self.cbVminChk.disconnect()
        self.cbVminVal.disconnect()
        self.cbVminUnder.disconnect()
        self.cbVmaxChk.disconnect()
        self.cbVmaxVal.disconnect()
        self.cbVmaxOver.disconnect()
        # Text :
        self.cbCblabel.disconnect()
        self.cbCbTxtSz.disconnect()
        self.cbCbTxtSh.disconnect()
        self.cbTxtSz.disconnect()
        self.cbTxtSh.disconnect()

    def _initialize(self):
        """"""
        # Settings :
        # self._fcn_Name()
        self._fcn_BckCol()
        self._fcn_TxtCol()
        self._fcn_Digits()
        self._fcn_Width()
        self._fcn_Border()
        self._fcn_Bw()
        self._fcn_Limits()
        # Clim/Vmin/Vmax :
        self._fcn_climchanged()
        self._vminvmax_onLoad()
        self._fcn_vminChanged()
        self._fcn_vmaxChanged()
        # TEXT :
        self._fcn_CbTitle()
        self._fcn_cbTxtSize()
        self._fcn_cbTxtShift()
        self._fcn_TxtSize()
        self._fcn_TxtShift()

    def _cb2GUI(self):
        """Update the displayed colorbar from the cb object."""
        # ________________ SETTINGS ________________
        self.cbBckCol.setText(str(color2tuple(self.cb.bgcolor)))
        self.cbTxtCol.setText(str(color2tuple(self.cb.txtcolor)))
        self.cbDigits.setValue(self.cb.ndigits)
        self.cbWidth.setValue(self.cb.width)
        self.cbBorder.setChecked(self.cb.border)
        self.cbBw.setValue(self.cb.bw)
        self.cbLimTxt.setChecked(self.cb.limtxt)

        # ________________ CMAP ________________
        idx, rev = mpl_cmap_index(self.cb.cmap)
        self.cbCmapRev.setChecked(rev)
        self.cbCmap.setCurrentIndex(idx)

        # ________________ CLIM ________________
        self.cbClimm.setValue(self.cb.clim[0])
        self.cbClimM.setValue(self.cb.clim[1])

        # ________________ VMIN ________________
        vminIsNone = self.cb.vmin is None
        self.cbVminChk.setChecked(not vminIsNone)
        if not vminIsNone:
            self._vminvmax_onLoad()
            self.cbVminVal.setValue(self.cb.vmin)
            self.cbVminUnder.setText(str(color2tuple(self.cb.under)))

        # ________________ VMAX ________________
        vmaxIsNone = self.cb.vmax is None
        self.cbVmaxChk.setChecked(not vmaxIsNone)
        if not vmaxIsNone:
            self._vminvmax_onLoad()
            self.cbVmaxVal.setValue(self.cb.vmax)
            self.cbVmaxOver.setText(str(color2tuple(self.cb.over)))

        # ________________ TEXT ________________
        # Cblabel :
        self.cbCblabel.setText(self.cb.cblabel)
        self.cbCbTxtSz.setValue(self.cb.cbtxtsz)
        self.cbCbTxtSh.setValue(self.cb.cbtxtsh)
        # Limits :
        self.cbTxtSz.setValue(self.cb.txtsz)
        self.cbTxtSh.setValue(self.cb.txtsh)

    ###########################################################################
    ###########################################################################
    #                              SETTINGS
    ###########################################################################
    ###########################################################################
    def _fcn_ChangeObj(self):
        """Change colorbar object."""
        # Get the current selected text :
        name = self.cbObject.currentText()
        # Select this object :
        self.objs.select(name)
        # Update colorbar visual from loaded objects :
        self.objs.update_from_obj(self.cb)
        # re-build colorbar :
        self.cb._build(True, 'all')
        # Disconnect interactions :
        self._disconnect()
        # Update GUI :
        self._cb2GUI()
        self._initialize()
        # Re-connect interactions :
        self._connect()

    def _fcn_Name(self):
        """Add object name."""
        self.cbObject.clear()
        self.cbObject.addItems(self.objs.list())

    def _fcn_BckCol(self):
        """Change background color."""
        self.cb.bgcolor = textline2color(str(self.cbBckCol.text()))[0]
        self.objs['bgcolor'] = self.cb.bgcolor

    def _fcn_TxtCol(self):
        """Change text color."""
        self.cb.txtcolor = textline2color(str(self.cbTxtCol.text()))[0]
        self.objs['txtcolor'] = self.cb.txtcolor

    def _fcn_Digits(self):
        """Change the number of digits."""
        ndigits = self.cbDigits.value()
        if 0 < ndigits:
            self.cb.ndigits = ndigits
            self.objs['ndigits'] = ndigits
            self.cbClimm.setDecimals(ndigits)
            self.cbClimM.setDecimals(ndigits)
            self.cbVminVal.setDecimals(ndigits)
            self.cbVmaxVal.setDecimals(ndigits)

    def _fcn_Width(self):
        """Change colorbar width."""
        self.cb.width = self.cbWidth.value()
        self.objs['width'] = self.cb.width

    def _fcn_Border(self):
        """Set the border."""
        viz = self.cbBorder.isChecked()
        self.cb.border = viz
        self.objs['border'] = self.cb.border
        self.cbBw.setEnabled(viz)

    def _fcn_Bw(self):
        """Change border width."""
        self.cb.bw = self.cbBw.value()
        self.objs['bw'] = self.cb.bw

    def _fcn_Limits(self):
        """Display/hide vmin/vmax."""
        self.cb.limtxt = self.cbLimTxt.isChecked()
        self.objs['limtxt'] = self.cb.limtxt

    ###########################################################################
    ###########################################################################
    #                              COLORMAP
    ###########################################################################
    ###########################################################################
    def _fcn_cmapChanged(self):
        """Change the colormap."""
        rv = self.cbCmapRev.isChecked() * '_r'
        self.cb.cmap = str(self.cbCmap.currentText()) + rv
        self.objs['cmap'] = self.cb.cmap

    ###########################################################################
    ###########################################################################
    #                              CLIM
    ###########################################################################
    ###########################################################################
    def _fcn_climchanged(self):
        """Update colorbar limits."""
        # Get value :
        climm, climM = float(self.cbClimm.value()), float(self.cbClimM.value())
        # Update clim :
        self.cb.clim = (climm, climM)
        self.objs['clim'] = self.cb.clim
        # Fix new vmin/max limits and step :
        self._vminvmax_onLoad()

    ###########################################################################
    ###########################################################################
    #                              VMIN/VMAX
    ###########################################################################
    ###########################################################################
    def _vminvmax_onLoad(self):
        """Activate checkboxs if vmin/vmax not None."""
        if isinstance(self.cb.vmin, (int, float)):
            self.cbVminChk.setChecked(True)
        if isinstance(self.cb.vmax, (int, float)):
            self.cbVmaxChk.setChecked(True)
        climm, climM = float(self.cbClimm.value()), float(self.cbClimM.value())
        # Define step :
        step = (climM - climm) / 100.
        self.cbVminVal.setMinimum(climm)
        self.cbVminVal.setMaximum(climM)
        self.cbVminVal.setSingleStep(step)
        self.cbVmaxVal.setMinimum(climm)
        self.cbVmaxVal.setMaximum(climM)
        self.cbVmaxVal.setSingleStep(step)

    def _fcn_vminChanged(self):
        """Change vmin/vmax/under/over."""
        isvmin = self.cbVminChk.isChecked()
        # Enable/Disable panels :
        self.cbVminW.setEnabled(isvmin)
        # Vmin :
        if isvmin:
            self.cb.vmin = self.cbVminVal.value()
            self.cb.under = textline2color(str(self.cbVminUnder.text()))[0]
        else:
            self.cb.vmin = None
        self.objs['vmin'] = self.cb.vmin
        self.objs['under'] = self.cb.under

    def _fcn_vmaxChanged(self):
        """Change vmin/vmax/under/over."""
        isvmax = self.cbVmaxChk.isChecked()
        self.cbVmaxW.setEnabled(isvmax)
        # Vmax
        if isvmax:
            self.cb.vmax = self.cbVmaxVal.value()
            self.cb.over = textline2color(str(self.cbVmaxOver.text()))[0]
        else:
            self.cb.vmax = None
        self.objs['vmax'] = self.cb.vmax
        self.objs['over'] = self.cb.over

    ###########################################################################
    ###########################################################################
    #                              VMIN/VMAX
    ###########################################################################
    ###########################################################################
    def _fcn_CbTitle(self):
        """Change colorbar title."""
        self.cb.cblabel = str(self.cbCblabel.text())
        self.objs['cblabel'] = self.cb.cblabel

    def _fcn_cbTxtSize(self):
        """Change colorbar text size."""
        self.cb.cbtxtsz = self.cbCbTxtSz.value()
        self.objs['cbtxtsz'] = self.cb.cbtxtsz

    def _fcn_cbTxtShift(self):
        """Change cblabel shift."""
        self.cb.cbtxtsh = self.cbCbTxtSh.value()
        self.objs['cbtxtsh'] = self.cb.cbtxtsh

    def _fcn_TxtSize(self):
        """Change text size for limits."""
        self.cb.txtsz = self.cbTxtSz.value()
        self.objs['txtsz'] = self.cb.txtsz

    def _fcn_TxtShift(self):
        """Change text shift."""
        self.cb.txtsh = self.cbTxtSh.value()
        self.objs['txtsh'] = self.cb.txtsh
