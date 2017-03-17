"""Main class for Colorbar inteactions."""

from ....utils import mpl_cmap, is_color


__all__ = ['uiCbar']


class uiCbar(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        self._cbForceUpdate = False
        self._able_to_update = True
        self._notOnStarting = False

        # ===================================================================
        # Update objects :
        # ===================================================================
        self._cb.update_from_object('ndplt', self._ndplt.mesh)
        self._cb.update_from_object('line', self._1dplt.mesh)

        # ===================================================================
        # Predefinitions :
        # ===================================================================
        # Add all defined objects (except histogram) :
        obj = [self._cbObjects.itemText(i) for i in range(
                                                    self._cbObjects.count())]
        # Set ndplt as the default view :
        self._cbObjects.setCurrentIndex(obj.index('ndplt'))
        self._cb.set_default('ndplt', run_fcn=False)
        # Link object selection :
        self._cbObjects.currentIndexChanged.connect(self._fcn_LoadObject)
        self._cbObjects.currentIndexChanged.connect(self._fcn_PanelObjects)
        # Add the list of existing colormaps :
        self._mplcmaps = mpl_cmap()
        self._cbCmap.addItems(self._mplcmaps)
        self._fcn_LoadObject()

        # ===================================================================
        # Connect cmap / clim / cmap / vmin / vmax / under / over :
        # ===================================================================
        self._cbCmap.currentIndexChanged.connect(self._fcn_uiCbInteract)
        self._cbClimMin.valueChanged.connect(self._fcn_uiCbInteract)
        self._cbClimMax.valueChanged.connect(self._fcn_uiCbInteract)
        self._cbVminChk.clicked.connect(self._fcn_uiCbInteract)
        self._cbVmin.valueChanged.connect(self._fcn_uiCbInteract)
        self._cbUnder.editingFinished.connect(self._fcn_uiCbInteract)
        self._cbVmaxChk.clicked.connect(self._fcn_uiCbInteract)
        self._cbVmax.valueChanged.connect(self._fcn_uiCbInteract)
        self._cbOver.editingFinished.connect(self._fcn_uiCbInteract)
        self._cbLabel.editingFinished.connect(self._fcn_uiCbInteract)
        self._cbAutoScale.clicked.connect(self._fcn_uiCbInteract)
        self._cbInvert.clicked.connect(self._fcn_uiCbInteract)
        self._cbUnder.setPlaceholderText("'red',  #ab4642...")
        self._cbOver.setPlaceholderText("(1,0,0), 'black'...")
        self._cbLabel.setPlaceholderText("My colorbar")
        self._cbAutoScale.clicked.connect(self._fcn_cbautoscale)

        self._cbForceUpdate = True

    def _fcn_LoadObject(self):
        """Load an object and set it args to the colorbar."""
        self._cbForceUpdate = False
        # Get current object and update:
        self._cb.set_default(str(self._cbObjects.currentText()), update=False)
        # Clim :
        self.uiclim = self._cb['clim']
        # Vmin / under :
        self.uivmin = self._cb['vmin']
        self.uiunder = self._cb['under']
        # Vmax / over :
        self.uivmax = self._cb['vmax']
        self.uiover = self._cb['over']
        # Label :
        self.uilabel = self._cb['label']
        # Minmax :
        self.uiminmax = self._cb['minmax']
        # Cmap / invert:
        cmap = self._cb['cmap']
        self.uiinvert = bool(self._cb['cmap'].find('_r') + 1)
        self.uicmap = cmap.replace('_r', '')

        self._cbForceUpdate = True
        self._fcn_uiCbInteract()

    def _fcn_PanelObjects(self):
        """Automatically display corresponding panel while interactions."""
        cobj = str(self._cbObjects.currentText())
        # Nd-plt :
        if cobj == 'ndplt':
            self._CanVisNd.setChecked(True)
            self._NdVizPanel.setVisible(True)
        # Line / Marker / Spectrogram :
        elif cobj in ['line', 'marker', 'spectrogram']:
            self._CanVis1d.setChecked(True)
            self._1dVizPanel.setVisible(True)
            self._1dPltPick.setCurrentIndex(self._1dplt.mesh._name.index(cobj))
        # Image :
        elif cobj == 'image':
            self._CanVisIm.setChecked(True)
            self._1dVizPanel.setVisible(True)
            self._fcn_imAxis_update()

    def _fcn_cbautoscale(self):
        """Autos-cale current object to [min, max]."""
        self._cb.auto_scale()
        # Clim :
        self.uiclim = self._cb['clim']

    # ==================================================================
    # PROPERTIES
    # ==================================================================
    def _fcn_uiCbInteract(self):
        """Ui interactions with the colorbar in the GUI."""
        if self._cbForceUpdate:
            # Avoid updates :
            # ------------- CLIM ------------
            self._clim = self.uiclim

            # ------------- CMAP / INVERT ------------
            self._invert = self.uiinvert
            self._cmap = self.uicmap

            # ------------- VMIN / UNDER ------------
            # Set vmin object minimum / maximum / step :
            # Display / hide panels for None values :
            vmchk = self._cbVminChk.isChecked()
            [k.setEnabled(vmchk) for k in [self._cbVmin, self._cbUnder]]
            # Set deep values to None if it's not a color :
            if vmchk and is_color(self.uiunder, 'textline'):
                self._vmin, self._under = self.uivmin, self.uiunder
            else:
                self._vmin = None

            # ------------- VMAX / OVER ------------
            # Display / hide panels for None values :
            vMchk = self._cbVmaxChk.isChecked()
            [k.setEnabled(vMchk) for k in [self._cbVmax, self._cbOver]]
            # Set deep values to None if it's not a color :
            if vMchk and is_color(self.uiover, 'textline'):
                self._vmax, self._over = self.uivmax, self.uiover
            else:
                self._vmax = None

            # ------------- LABEL ------------
            self._label = self.uilabel

            # ------------- MINMAX ------------

            # ------------- ABLE TO UPDATE ------------
            clim, vmin, vmax = self._clim, self._vmin, self._vmax
            # Test if any clim[1] > clim[0]
            abclim = (clim[1] > clim[0])
            # Test if vmin is not None, and clim[0] < vmin < clim[1] :
            abvmc = (vmin > clim[0]) and (vmin < clim[1]) if vmin else True
            # Test if vmax is not None, and clim[0] < vmax < clim[1] :
            abvMc = (vmax > clim[0]) and (vmax < clim[1]) if vmax else True
            # Test if vmin < vmax :
            abvmM = (vmin < vmax) if vmin and vmax else True
            # Update only if all conditions are True :
            if all([abclim, abvmc, abvmM, abvMc]):
                self._able_to_update = True
            else:
                self._able_to_update = False

            # Finally, update the config :
            self._fcn_Ui2Cb()

    def _fcn_Ui2Cb(self):
        """From deep ui-values, update colorbar object."""
        if self._able_to_update:
            # Get clim :
            self._cb['clim'] = self._clim
            # Get cmap :
            self._cb['cmap'] = self._cmap + '_r'*self._invert
            # Get vmin / under :
            self._cb['vmin'], self._cb['under'] = self._vmin, self._under
            # Get vmax / over :
            self._cb['vmax'], self._cb['over'] = self._vmax, self._over
            # Set label :
            self._cb['label'] = self._label
            # Update object :
            self._cb.update(run_fcn=self._notOnStarting)
            self._notOnStarting = True

    # ==================================================================
    # PROPERTIES
    # ==================================================================
    # ----------- CLIM -----------
    @property
    def uiclim(self):
        """Get the uiclim value."""
        return (self._cbClimMin.value(), self._cbClimMax.value())

    @uiclim.setter
    def uiclim(self, value):
        """Set uiclim value."""
        self._clim = value
        self._cbClimMin.setValue(value[0])
        self._cbClimMax.setValue(value[1])

    # ----------- CMAP -----------
    @property
    def uicmap(self):
        """Get the uicmap value."""
        return str(self._cbCmap.currentText())

    @uicmap.setter
    def uicmap(self, value):
        """Set uicmap value."""
        self._cmap = value
        self._cbCmap.setCurrentIndex(self._mplcmaps.index(value))

    # ----------- VMIN -----------
    @property
    def uivmin(self):
        """Get the uivmin value."""
        return self._cbVmin.value()

    @uivmin.setter
    def uivmin(self, value):
        """Set uivmin value."""
        if value:
            self._vmin = value
            self._cbVmin.setValue(value)
            self._cbVminChk.setChecked(True)
        else:
            self._vmin = None
            self._cbVminChk.setChecked(False)

    # ----------- UNDER -----------
    @property
    def uiunder(self):
        """Get the uiunder value."""
        return self._cbUnder.text()

    @uiunder.setter
    def uiunder(self, value):
        """Set uiunder value."""
        self._under = value
        self._cbUnder.setText(value)

    # ----------- VMAX -----------
    @property
    def uivmax(self):
        """Get the uivmax value."""
        return self._cbVmax.value()

    @uivmax.setter
    def uivmax(self, value):
        """Set uivmax value."""
        if value:
            self._vmax = value
            self._cbVmax.setValue(value)
            self._cbVmaxChk.setChecked(True)
        else:
            self._vmax = None
            self._cbVmaxChk.setChecked(False)

    # ----------- OVER -----------
    @property
    def uiover(self):
        """Get the uiover value."""
        return self._cbOver.text()

    @uiover.setter
    def uiover(self, value):
        """Set uiover value."""
        self._over = value
        self._cbOver.setText(value)

    # ----------- INVERT -----------
    @property
    def uiinvert(self):
        """Get the uiinvert value."""
        return self._cbInvert.isChecked()

    @uiinvert.setter
    def uiinvert(self, value):
        """Set uiinvert value."""
        self._invert = value
        self._cbInvert.setChecked(value)

    # ----------- LABEL -----------
    @property
    def uilabel(self):
        """Get the uilabel value."""
        return self._cbLabel.text()

    @uilabel.setter
    def uilabel(self, value):
        """Set uilabel value."""
        self._label = value
        self._cbLabel.setText(value)

    # ----------- MINMAX -----------
    @property
    def uiminmax(self):
        """Get the uiminmax value."""
        return self._minmax

    @uiminmax.setter
    def uiminmax(self, value):
        """Set uiminmax value."""
        self._minmax = value
