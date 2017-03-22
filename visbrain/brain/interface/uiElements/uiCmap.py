"""Interaction between colormap's variables and the GUI colorbar.

The uiCmap class is used to control the colormap of several elements (sources /
connectivity).
"""

from matplotlib import cm
from ....utils import textline2color


class uiCmap(object):
    """Manage interactions between the GUI colorbar and colormap objects.

    Some objects have their own colormap (sources / connectivity). This class
    can be used to control their colormap's arguments directly using the GUI.
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

        # Interactive :
        self._qcmapVisible.clicked.connect(self._toggle_cmap)
        self._toggle_cmap()

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
        self.q_over.editingFinished.connect(self._GUI2cmap)
        self.q_cblabel.editingFinished.connect(self._GUI2cmap)
        self.q_auto_scale.clicked.connect(self._auto_scale)
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
            self.cb['vmin'] = None
            self.cb['under'] = None
        if self.cb['vmax'] is not None:
            self.q_vmax.setValue(self.cb['vmax'])
            self.q_vmax_chk.setChecked(True)
        else:
            self.q_vmax.setEnabled(False)
            self.cb['vmax'] = None
            self.cb['over'] = None

        # Set under / over to the GUI :
        if self.cb['under'] is not None:
            self.q_under.setText(str(self.cb['under']))
            self.qUnder_txt.setEnabled(True)
        else:
            self.q_under.setEnabled(False)
            self.qUnder_txt.setEnabled(False)
        if self.cb['over'] is not None:
            self.q_over.setText(str(self.cb['over']))
            self.qOver_txt.setEnabled(True)
        else:
            self.q_over.setEnabled(False)
            self.qOver_txt.setEnabled(False)

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
                self.cb['cmap'] = str(self.q_cmap_list.currentText()) + '_r'
            else:
                self.cb['cmap'] = str(self.q_cmap_list.currentText())

            # Get clim and set to cb object :
            self.cb['clim'] = (self.q_cmin.value(), self.q_cmax.value())

            # Get vmin / under and vmax / over and set to cb object :
            # vmin / under :
            if self.q_vmin_chk.isChecked():
                self.q_vmin.setEnabled(True)
                self.qUnder_txt.setEnabled(True)
                self.q_under.setEnabled(True)
                if self.q_vmin.value() > self.cb['clim'][0]:
                    self.cb['vmin'] = self.q_vmin.value()
                else:
                    self.cb['vmin'] = None
                self.cb['under'], _ = textline2color(str(self.q_under.text()))
            else:
                self.q_vmin.setEnabled(False)
                self.qUnder_txt.setEnabled(False)
                self.q_under.setEnabled(False)
                self.cb['vmin'] = None
                self.cb['under'] = None
            # vmax :
            if self.q_vmax_chk.isChecked():
                self.q_vmax.setEnabled(True)
                self.qOver_txt.setEnabled(True)
                self.q_over.setEnabled(True)
                if self.q_vmax.value() < self.cb['clim'][1]:
                    self.cb['vmax'] = self.q_vmax.value()
                else:
                    self.cb['vmax'] = None
                self.cb['over'], _ = textline2color(str(self.q_over.text()))
            else:
                self.q_vmax.setEnabled(False)
                self.q_vmax.setEnabled(False)
                self.qOver_txt.setEnabled(False)
                self.q_over.setEnabled(False)
                self.cb['vmax'] = None
                self.cb['over'] = None
            # Vmin / vmax :
            if (self.cb['vmin'] is not None) and (self.cb['vmax'] is not None):
                if self.cb['vmin'] >= self.cb['vmax']:
                    self.cb['vmin'] = None
                    self.cb['vmax'] = None

            # Update colorbar label :
            self.cb['label'] = str(self.q_cblabel.text())

            # Direct interaction : if this button is checked, the user can see
            # the colormap changements inline :
            # Update sources :
            if self.cmapSources.isChecked():
                # If cortical projection never run :
                if self.current_mask is None:
                    self._userMsg("To control the colormap of sources, "
                                  "run either the cortical\nprojection / "
                                  "repartition first.", 'warn', 10, 9)
                    # self._cortical_projection()
                # Otherwise update colormap :
                else:
                    self.sources.cbUpdateFrom(self.cb)
                    self._array2cmap(self.current_mask,
                                     non_zero=self.current_non_zero)
                # Update colorbar :
                self.cb.cbupdate(self.current_mask, **self.cb._cb)

            # Update connectivity :
            elif self.cmapConnect.isChecked():
                self.connect.cbUpdateFrom(self.cb)
                self.connect._check_color()
                self.cb.cbupdate(self.connect._all_nnz, **self.cb._cb)

            # except:
            #     pass

    def _select_object_cmap(self):
        """Specify the object for which colormap properties need to be applied.

        The GUI colorbar / colormap can be used either for connectivity or for
        sources. This function can be used to switch between both of this
        object.
        """
        # First, get the latest (min(), max()) :
        self._cmap_MinMax()

        # The cbUpdateFrom() function take a colorbar object (the one for
        # sources or connectivity), take attributes and set it to be the
        # default colormap / colorbar.

        # Sources object :
        if self.cmapSources.isChecked():
            self.cb.cbUpdateFrom(self.sources)

        # Connectivity object :
        elif self.cmapConnect.isChecked():
            self.cb.cbUpdateFrom(self.connect)

        self._cmap2GUI()

    def _cmap_MinMax(self):
        """Get the (min(), max()) of the selected object.

        The (min(), max()) couple is used for auto-scaling data.
        """
        # Sources :
        if self.cmapSources.isChecked():
            self.cb.cbUpdateFrom(self.sources)
        # Connectivity object :
        elif self.cmapConnect.isChecked():
            self.cb.cbUpdateFrom(self.connect)

    def _auto_scale(self):
        """Automatically scale the colorbar between (data.min(), data.max()).

        This function turn the user colorbar limits into the most optimal ones
        i.e those defining by the Minimum and Maximum of the printed data (for
        the selected object).
        """
        # Get latest updated (min(), max()) :
        self._cmap_MinMax()
        self.cb['clim'] = self.cb._MinMax

        # Turn vmin / vmax off :
        self.cb['vmin'], self.cb['vmax'] = None, None
        self.q_vmin_chk.setChecked(False)
        self.q_vmax_chk.setChecked(False)

        # Update GUI elements :
        self._cmap2GUI()

    def _toggle_cmap(self):
        """Toggle colorbar panel."""
        viz = self._qcmapVisible.isChecked()
        self.colorbar_pan.setEnabled(viz)
        self.cbpanelW.setVisible(viz)
