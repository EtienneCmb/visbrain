"""Interaction between colormap's buttons in the GUI and the user.

The uiCmap class...
"""

from matplotlib import cm
from ...utils import textline2color


class uiCmap(object):

    """Main
    """

    def __init__(self,):
        """Init."""
        # Get the list of possible colormaps :
        self.cmap_lst = [k for k in list(cm.datad.keys()) + list(
                            cm.cmaps_listed.keys()) if not k.find('_r') + 1]
        self.cmap_lst.sort()
        # Add this list to the GUI :
        self.q_cmap_list.addItems(self.cmap_lst)
        # The "uiCmap_update" parameter is True if the colorbar need to be
        # updated :
        self.uiCmap_update = True
        self._cmap2GUI()

        # Colorbar label :
        self.q_cmap_invert.clicked.connect(self._GUI2cmap)
        self.q_cmap_list.currentIndexChanged.connect(self._GUI2cmap)
        self.q_cmin.valueChanged.connect(self._GUI2cmap)
        self.q_cmax.valueChanged.connect(self._GUI2cmap)
        self.q_vmin_chk.clicked.connect(self._GUI2cmap)
        self.q_vmin.valueChanged.connect(self._GUI2cmap)
        self.q_vmax.valueChanged.connect(self._GUI2cmap)
        self.q_vmax_chk.clicked.connect(self._GUI2cmap)
        self.q_under.editingFinished.connect(self._GUI2cmap)
        self.q_under_chk.clicked.connect(self._GUI2cmap)
        self.q_over.editingFinished.connect(self._GUI2cmap)
        self.q_over_chk.clicked.connect(self._GUI2cmap)
        self.q_cmap_interact.clicked.connect(self._GUI2cmap)
        self.q_auto_scale.clicked.connect(self._GUI2cmap)
        self.q_cblabel.editingFinished.connect(self._GUI2cmap)
        self.cmapSources.clicked.connect(self._select_object_cmap)
        self.cmapConnect.clicked.connect(self._select_object_cmap)

        # Default properties :
        self.q_under.setPlaceholderText("'red',  #ab4642...")
        self.q_over.setPlaceholderText("(1,0,0), 'black'...")
        self.q_cblabel.setPlaceholderText("My colorbar")

        self._select_object_cmap()

    def _cmap2GUI(self):
        """Get colorbar properties and set to the GUI if possible.

        This function take all colorbar properties of a specific object
        (sources / connectivity) and applied those properties to the GUI
        colorbar. This function works in asociation with the _GUI2cmap()
        function.
        """
        # Don't update while setting elements :
        self.uiCmap_update = False

        # Set colormap to the GUI :
        if self.cb['cmap'].find('_r') == -1:
            cmap, _r = self.cb['cmap'], ''
        else:
            cmap, _r = self.cb['cmap'][0:-2], '_r'
        self.q_cmap_list.setCurrentIndex(self.cmap_lst.index(cmap))
        self.cb['cmap'] += _r

        # Set vmin / vmax to the GUI :
        if self.cb['vmin'] is not None:
            self.q_vmin.setValue(self.cb['vmin'])
            self.q_vmin_chk.setChecked(True)
        else:
            self.q_vmin.setEnabled(False)
        if self.cb['vmax'] is not None:
            self.q_vmax.setValue(self.cb['vmax'])
            self.q_vmax_chk.setChecked(True)
        else:
            self.q_vmax.setEnabled(False)

        # Set under / over to the GUI :
        if self.cb['under'] is not None:
            self.q_under.setText(str(self.cb['under']))
            self.q_under_chk.setChecked(True)
        else:
            self.q_under.setEnabled(False)
        if self.cb['over'] is not None:
            self.q_over.setText(str(self.cb['over']))
            self.q_over_chk.setChecked(True)
        else:
            self.q_over.setEnabled(False)

        # Set clim to the GUI :
        if self.cb['clim'] != (None, None):
            self.q_cmin.setValue(self.cb['clim'][0])
            self.q_cmax.setValue(self.cb['clim'][1])

        # Set colorbar label :
        if isinstance(self.cb['label'], str):
            self.q_cblabel.setText(self.cb['label'])

        # Update colorbar GUI :
        self.uiCmap_update = True
        self._GUI2cmap()  # <--------------- USEFULL???????

    def _GUI2cmap(self):
        """Get GUI colorbar properties and set to the object if possible.

        This function get all GUI colorbar properties and set them to a
        specific object (sources / connectivity). This function works in
        asociation with the _cmap2GUI() function.
        """
        # If an update is needed :
        if self.uiCmap_update:
            # try:
            # Get colormap name and set to cb object :
            if self.q_cmap_invert.isChecked():
                self.cb['cmap'] = self.q_cmap_list.currentText() + '_r'
            else:
                self.cb['cmap'] = self.q_cmap_list.currentText()
            if self.q_auto_scale.isChecked():
                self.q_vmin_chk.setChecked(False)
                self.q_vmax_chk.setChecked(False)
                self.cb['clim'] = self.cb._climBck
                self.q_cmin.setValue(self.cb['clim'][0])
                self.q_cmax.setValue(self.cb['clim'][1])
            else:
                pass

            # Get clim and set to cb object :
            self.cb['clim'] = (self.q_cmin.value(), self.q_cmax.value())

            # Get vmin and vmax and set to cb object :
            if self.q_vmin_chk.isChecked():
                self.q_vmin.setEnabled(True)
                self.cb['vmin'] = self.q_vmin.value()
            else:
                self.q_vmin.setEnabled(False)
                self.q_under_chk.setChecked(False)
                self.cb['vmin'] = None
            if self.q_vmax_chk.isChecked():
                self.q_vmax.setEnabled(True)
                self.cb['vmax'] = self.q_vmax.value()
            else:
                self.q_vmax.setEnabled(False)
                self.q_over_chk.setChecked(False)
                self.cb['vmax'] = None

            # Get color under/over and set to cb object :
            if self.q_under_chk.isChecked():
                self.q_under.setEnabled(True)
                self.cb['under'], _ = textline2color(self.q_under.text())
            else:
                self.q_under.setEnabled(False)
                self.cb['under'] = None
            if self.q_over_chk.isChecked():
                self.q_over.setEnabled(True)
                self.cb['over'], _ = textline2color(self.q_over.text())
            else:
                self.q_over.setEnabled(False)
                self.cb['over'] = None
            self.cb['label'] = self.q_cblabel.text()

            # Direct interaction : if this button is checked, the user can see
            # the colormap changements inline :
            if self.q_cmap_interact.isChecked():

                # Update sources :
                if self.cmapSources.isChecked():
                    # If cortical projection never run :
                    if self.current_mask is None:
                        self.cortical_projection()
                    # Otherwise update colormap :
                    else:
                        self.sources.cbUpdateFrom(self.cb)
                        self._array2cmap(self.current_mask,
                                         non_zero=self.current_non_zero)
                    # Update colorbar :
                    self.cb.cbupdate(self.current_mask, **self.cb._cb)
                elif self.cmapConnect.isChecked():
                    print('PAS OK')
                    self.connect.cbUpdateFrom(self.cb)
                    self.connect.mesh.set_color(colorby=self.connect.colorby,
                                                dynamic=self.connect.dynamic,
                                                **self.connect._cb)
                    self.connect.mesh.update()
                    self.cb.cbupdate(self.connect.mesh._all_nnz, **self.cb._cb)

            # except:
            #     pass

    def _select_object_cmap(self):
        """Specify the object for which colormap properties need to be applied.

        The GUI colorbar / colormap can be used either for connectivity or for
        sources. This function can be used to switch between both of this
        object.
        """
        # The cbUpdateFrom() function take a colorbar object (the one for
        # sources or connectivity), take attributes and set it to be the
        # default colormap / colorbar.
        # Sources object :
        if self.cmapSources.isChecked():
            self.cb.cbUpdateFrom(self.sources)
            # self.cb.cbupdate(self.current_mask, **self.cb._cb)
        # Connectivity object :
        elif self.cmapConnect.isChecked():
            self.cb.cbUpdateFrom(self.connect)
        self._cmap2GUI()
