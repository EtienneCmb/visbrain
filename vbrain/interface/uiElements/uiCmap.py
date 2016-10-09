from matplotlib import cm
from ...utils import textline2color


class uiCmap(object):

    """docstring for uiCmap
    """

    def __init__(self,):
        self.cmap_lst = [k for k in list(
            cm.datad.keys()) + list(cm.cmaps_listed.keys()) if not k.find('_r') + 1]
        self.cmap_lst.sort()
        self.q_cmap_list.addItems(self.cmap_lst)
        self.uiCmap_update = True
        self.set_default_cmap()

        # Colorbar label :
        self.q_cmap_invert.clicked.connect(self.select_cmap)
        self.q_cmap_list.currentIndexChanged.connect(self.select_cmap)
        self.q_vmin_chk.clicked.connect(self.select_cmap)
        self.q_vmin.valueChanged.connect(self.select_cmap)
        self.q_vmax.valueChanged.connect(self.select_cmap)
        self.q_vmax_chk.clicked.connect(self.select_cmap)
        self.q_under.editingFinished.connect(self.select_cmap)
        self.q_under_chk.clicked.connect(self.select_cmap)
        self.q_over.editingFinished.connect(self.select_cmap)
        self.q_over_chk.clicked.connect(self.select_cmap)
        self.q_cmap_interact.clicked.connect(self.select_cmap)
        self.q_auto_scale.clicked.connect(self.select_cmap)
        self.q_cblabel.editingFinished.connect(self.select_cmap)
        self.cmapSources.clicked.connect(self.select_object_cmap)
        self.cmapConnect.clicked.connect(self.select_object_cmap)

        # Default properties :
        self.q_under.setPlaceholderText("'red',  #ab4642...")
        self.q_over.setPlaceholderText("(1,0,0), 'black'...")
        self.q_cblabel.setPlaceholderText("My colorbar")



    def set_default_cmap(self):
        """
        """
        # Don't update while setting elements :
        self.uiCmap_update = False

        # Set colormap in list :
        if self.cb['cmap'].find('_r') == -1:
            cmap, _r = self.cb['cmap'], ''
        else:
            cmap, _r = self.cb['cmap'][0:-2], '_r'
        self.q_cmap_list.setCurrentIndex(self.cmap_lst.index(cmap))
        self.cb['cmap'] += _r 

        # vmin/vmax mngmt :
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

        # under/over mngmt :
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
        self.q_cblabel.setText(self.cb['label'])

        self.uiCmap_update = True
        self.select_cmap()


    def select_cmap(self):
        """Apply ui changes to the colormap
        """
        # If an update is needed :
        if self.uiCmap_update:
            # try:
            # Get colormap name :
            if self.q_cmap_invert.isChecked():
                self.cb['cmap'] = self.q_cmap_list.currentText() + '_r'
            else:
                self.cb['cmap'] = self.q_cmap_list.currentText()
            if self.q_auto_scale.isChecked():
                self.q_vmin_chk.setChecked(False)
                self.q_vmax_chk.setChecked(False)
            else:
                pass

            # Get vmin and vmax :
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

            # Get color under/over :
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

            # Interact directly with cmap :
            if self.q_cmap_interact.isChecked():

                # Update sources :
                if self.cmapSources.isChecked():
                    # If cortical projection never run :
                    if self.current_mask is None:
                        self.cortical_projection()
                    # Otherwise update colormap :
                    else:
                        self.sources.cbUpdateFrom(self.cb)
                        self._array2cmap(self.current_mask, non_zero=self.current_non_zero)
                    # Update colorbar :
                    self.cb.cbupdate(self.current_mask, **self.cb._cb)
                elif self.cmapConnect.isChecked():
                    print('PAS OK')
                    self.connect.cbUpdateFrom(self.cb)
                    self.connect.mesh.set_color(colorby=self.connect.colorby, dynamic=self.connect.dynamic, **self.connect._cb)
                    self.connect.mesh.update()
                    self.cb.cbupdate(self.connect.mesh._all_nnz, **self.cb._cb)

            # except:
            #     pass


    def select_object_cmap(self):
        """
        """
        if self.cmapSources.isChecked():
            self.cb.cbUpdateFrom(self.sources)
            # self.cb.cbupdate(self.current_mask, **self.cb._cb)
        elif self.cmapConnect.isChecked():
            self.cb.cbUpdateFrom(self.connect)
        self.set_default_cmap()