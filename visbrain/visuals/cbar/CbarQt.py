"""Mehods to manage interactions between the GUI and objects."""

from ...utils import color2json, mpl_cmap, mpl_cmap_index
from .gui import CbarForm
from .CbarVisual import CbarVisual

__all__ = ['CbarQt']


class CbarQt(object):
    """Link the GUI colorbar with the VisPy based colorbar.

    self[obj_name] : get the item from the GUI
    self[obj_name] = value : set the value to the VisPy based colorbar.

    Parameters
    ----------
    guiW: PyQt widget
        The widget for adding the GUI colorar properties.
    vizW: PyQt widget
        The widget for adding the VisPy based colorbar.
    """

    def __init__(self, guiW, vizW, cbobjs, parent=None, camera=None):
        """Init."""
        # --------------------------------------------------------------------
        #                             GUI COMPONENTS
        # --------------------------------------------------------------------
        # Add colorbar properties to guiW :
        self.cbui = CbarForm()
        self.cbui.setupUi(guiW)
        # Add VisPy based colorbar :
        self.cbviz = CbarVisual(parent=parent)
        vizW.addWidget(self.cbviz._canvas.native)
        self.cbobjs = cbobjs

        self['object'].addItems(self.cbobjs.keys())

    ###########################################################################
    ###########################################################################
    #                            GET / SET ITEMS
    ###########################################################################
    ###########################################################################
    def __getitem__(self, key):
        """Get the item from the GUI."""
        return eval('self.cbui.' + key)

    def __setitem__(self, key, value):
        """Set VisPy based colormap item from GUI properties."""
        if not isinstance(value, str):
            exec('self.cbviz.' + key + '=' + str(value))
        else:
            exec("self.cbviz." + key + "='" + value + "'")

    ###########################################################################
    ###########################################################################
    #                            LOAD / SAVE
    ###########################################################################
    ###########################################################################
    def save(self, filename):
        """Save all colorbar configurations.

        Parameters
        ----------
        filename : string
            Name of the file to be saved.
        """
        self.cbobjs.save(filename)

    def load(self, filename, **kwargs):
        """Load a colorbar configuration file.

        Parameters
        ----------
        filename : string
            Name of the file to load.
        kwargs : dict, optional, (def: {})
            Further arguments to pass to the CbarObjects class.
        """
        self.cbobjs.load(filename, **kwargs)

    def add_camera(self, camera):
        """Add a camera to the VisPy based colorbar."""
        self.cbviz._wc.camera = camera

    def to_dict(self):
        """Return a dictionary of the current visual state."""
        self.cbviz.to_dict()

    def link(self, name, fcn, minmaxfcn):
        """Link an object with a function.

        When an colormap argument changed, a function associated to the object
        is executed (only for colormap arguments i.e. cmap, clim, vmin, vmax,
        under, over).
        """
        self.cbobjs._objs[name]._fcn = fcn
        self.cbobjs._objs[name]._minmaxfcn = minmaxfcn

    def select(self, name, onload=False):
        """Select an object.

        Parameters
        ----------
        name : string
            Name of the object to select.
        """
        # Get the list of all current objects :
        allItems = [self['object'].itemText(i) for i in range(
            self['object'].count())]
        if name in allItems:
            # Select object in the cbar object manager :
            self.cbobjs.select(name)
            # Find the index and set it in the combobox :
            idx = allItems.index(name)
            self['object'].setCurrentIndex(idx)
        else:
            raise ValueError(name + " not in the list of objects.")

    def setEnabled(self, name, enable=True):
        """Deactivate an object."""
        # Get the list of all current objects :
        allItems = [self['object'].itemText(i) for i in range(
            self['object'].count())]
        if name in allItems:
            # Find the index and set it in the combobox :
            idx = allItems.index(name)
            self['object'].model().item(idx).setEnabled(enable)

    ###########################################################################
    ###########################################################################
    #                CONNECT / DISCONNECT / INITIALIZE
    ###########################################################################
    ###########################################################################
    # --------------------------------------------------------------------
    #                          INITIALIZE GUI
    # --------------------------------------------------------------------
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
        # Clim should never be None :
        self['climm'].setValue(self.cbobjs['clim'][0])
        self['climM'].setValue(self.cbobjs['clim'][1])

        # _____________ VMIN/VMAX _____________
        # Set vmin/vmax limits :
        self._vminvmaxCheck()
        # Vmin/under :
        self['isvmin'].setChecked(self.cbobjs['isvmin'])
        self['vmin'].setValue(self.cbobjs['vmin'])
        self['under'].setText(str(self.cbobjs['under']))
        # Vmax/over :
        self['isvmax'].setChecked(self.cbobjs['isvmax'])
        self['vmax'].setValue(self.cbobjs['vmax'])
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

    # --------------------------------------------------------------------
    #                             GUI -> VISUAL
    # --------------------------------------------------------------------
    def _gui2visual(self):
        # Settings :
        self._fcn_BckCol()
        self._fcn_TxtCol()
        self._fcn_Digits()
        self._fcn_Width()
        self._fcn_Border()
        self._fcn_Bw()
        self._fcn_Limits()
        # Cmap/Clim/Vmin/Vmax :
        self._fcn_cmapChanged()
        self._fcn_climchanged()
        self._fcn_vminChanged()
        self._fcn_vmaxChanged()
        # Text :
        self._fcn_CbTitle()
        self._fcn_cbTxtSize()
        self._fcn_cbTxtShift()
        self._fcn_TxtSize()
        self._fcn_TxtShift()

    # --------------------------------------------------------------------
    #                             CONNECT
    # --------------------------------------------------------------------
    def _connect(self):
        """Connect cbui to cbviz."""
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
        self['isvmin'].clicked.connect(self._fcn_vminChanged)
        self['vmin'].valueChanged.connect(self._fcn_vminChanged)
        self['under'].editingFinished.connect(self._fcn_vminChanged)
        self['vmin'].setKeyboardTracking(False)
        # Vmax :
        self['isvmax'].clicked.connect(self._fcn_vmaxChanged)
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

        # _____________ AUTOSCALE _____________
        self['autoscale'].clicked.connect(self._fcn_cbAutoscale)

    # --------------------------------------------------------------------
    #                             DISCONNECT
    # --------------------------------------------------------------------
    def _disconnect(self):
        def _try(obj):
            """Be sure to deconnect to all interactions."""
            while True:
                try:
                    obj.disconnect()
                except TypeError:
                    break
        # Settings :
        _try(self['object'])
        _try(self['bckCol'])
        _try(self['txtCol'])
        _try(self['ndigits'])
        _try(self['width'])
        _try(self['border'])
        _try(self['bw'])
        _try(self['limTxt'])
        # Cmap :
        _try(self['cmap'])
        _try(self['cmapRev'])
        # Clim :
        _try(self['climm'])
        _try(self['climM'])
        # Vmin/Vmax/Under/Over :
        _try(self['isvmin'])
        _try(self['vmin'])
        _try(self['under'])
        _try(self['isvmax'])
        _try(self['vmax'])
        _try(self['over'])
        # Text :
        _try(self['cblabel'])
        _try(self['cbTxtSz'])
        _try(self['cbTxtSh'])
        _try(self['txtSz'])
        _try(self['txtSh'])
        # Autoscale :
        _try(self['autoscale'])

    ###########################################################################
    ###########################################################################
    #                              SUB-FONCTION
    ###########################################################################
    ###########################################################################
    # --------------------------------------------------------------------
    #                             SETTINGS
    # --------------------------------------------------------------------
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

    # --------------------------------------------------------------------
    #                                CMAP
    # --------------------------------------------------------------------
    def _fcn_cmapChanged(self):
        """Change the colormap."""
        rv = self['cmapRev'].isChecked() * '_r'
        self['cmap'] = str(self['cmap'].currentText()) + rv
        self.cbobjs['cmap'] = self.cbviz.cmap
        # Run object's update function :
        self.cbobjs.update()

    # --------------------------------------------------------------------
    #                             CLIM
    # --------------------------------------------------------------------
    def _fcn_climchanged(self):
        """Update colorbar limits."""
        # Get value (climm, climM):
        climm = float(self['climm'].value())
        climM = float(self['climM'].value())
        # Fix (climm, climM) limits :
        if climm < climM:
            # Update clim :
            self['clim'] = (climm, climM)
            self.cbobjs['clim'] = self.cbviz.clim
            # Update vmin/vmax limits :
            self._vminvmaxCheck()
            # Run object's update function :
            self.cbobjs.update()
        else:
            raise ValueError(str(tuple((climm, climM))) + " : clim.min() "
                             "> clim.max().")

    # --------------------------------------------------------------------
    #                   VMIN / VMAX / UNDER / OVER
    # --------------------------------------------------------------------
    def _vminvmaxCheck(self):
        """Activate checkboxs if vmin/vmax not None."""
        # Get clim and define step :
        climm = float(self['climm'].value())
        climM = float(self['climM'].value())
        step = (climM - climm) / 100.
        # -------------- Vmin --------------
        if not isinstance(self.cbobjs['vmin'], (int, float)):
            self.cbobjs['vmin'] = climm - 1.
        self['vmin'].setMinimum(climm)
        self['vmin'].setMaximum(climM)
        self['vmin'].setSingleStep(step)

        # -------------- Vmax --------------
        if not isinstance(self.cbobjs['vmax'], (int, float)):
            self.cbobjs['vmax'] = climM + 1.
        self['vmax'].setMinimum(climm)
        self['vmax'].setMaximum(climM)
        self['vmax'].setSingleStep(step)

    def _fcn_vminChanged(self):
        """Change vmin/vmax/under/over."""
        isvmin = self['isvmin'].isChecked()
        # Enable/Disable panels :
        self['vminW'].setEnabled(isvmin)
        # Vmin :
        self['isvmin'] = isvmin
        self['vmin'] = self['vmin'].value()
        self['under'] = color2json(self['under'])
        self.cbobjs['isvmin'] = self.cbviz.isvmin
        self.cbobjs['vmin'] = self.cbviz.vmin
        self.cbobjs['under'] = self.cbviz.under
        # Run object's update function :
        self.cbobjs.update()

    def _fcn_vmaxChanged(self):
        """Change vmin/vmax/under/over."""
        isvmax = self['isvmax'].isChecked()
        self['vmaxW'].setEnabled(isvmax)
        # Vmax
        self['isvmax'] = isvmax
        self['vmax'] = self['vmax'].value()
        self['over'] = color2json(self['over'])
        self.cbobjs['isvmax'] = self.cbviz.isvmax
        self.cbobjs['vmax'] = self.cbviz.vmax
        self.cbobjs['over'] = self.cbviz.over
        # Run object's update function :
        self.cbobjs.update()

    def _fcn_Limits(self):
        """Display/hide vmin/vmax."""
        self['limtxt'] = self['limTxt'].isChecked()
        self.cbobjs['limtxt'] = self.cbviz.limtxt

    # --------------------------------------------------------------------
    #                             TEXT
    # --------------------------------------------------------------------
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

    def _fcn_TxtCol(self):
        """Change text color."""
        txtcolor = color2json(self['txtCol'])
        self['txtcolor'] = txtcolor
        self.cbobjs['txtcolor'] = self.cbviz.txtcolor
        self.cbobjs['txtsh'] = self.cbviz.txtsh

    # --------------------------------------------------------------------
    #                             TEXT
    # --------------------------------------------------------------------
    def _fcn_cbAutoscale(self, *args, name=None):
        """Autoscale limits to data (Min, Max)."""
        # Select object if it's not the current one :
        if (name is not None) and self.cbobjs.name != name:
            self.select(name)
        # Disconnect clim buttons :
        self['climm'].disconnect()
        self['climM'].disconnect()
        # Run the auto-scaling function :
        self.cbobjs.autoscale()
        # Set clim to the gui :
        self['climm'].setValue(self.cbobjs['clim'][0])
        self['climM'].setValue(self.cbobjs['clim'][1])
        # Check vmin/vmax values :
        self._vminvmaxCheck()
        # Set clim the the VisPy based colorbar :
        self['clim'] = self.cbobjs['clim']
        # Reconnect clim buttons :
        self['climm'].valueChanged.connect(self._fcn_climchanged)
        self['climM'].valueChanged.connect(self._fcn_climchanged)
        self['climm'].setKeyboardTracking(False)
        self['climM'].setKeyboardTracking(False)
        # Deactivate vmin/vmax :
        self['isvmin'].setChecked(False)
        self['isvmax'].setChecked(False)
        self['isvmin'] = self['isvmax'] = False
