from matplotlib import cm


class uiCmap(object):

    """docstring for uiCmap
    """

    def __init__(self,):
        self.cmap_lst = [k for k in list(
            cm.datad.keys()) + list(cm.cmaps_listed.keys()) if not k.find('_r') + 1]
        self.cmap_lst.sort()
        self.q_cmap_list.addItems(self.cmap_lst)
        self.q_cmap_list.setCurrentIndex(self.cmap_lst.index(self.cmap))
        self.q_cmap_list.currentIndexChanged.connect(self.select_cmap)
        self.q_cmap_invert.clicked.connect(self.select_cmap)
        # vmin/vmax mngmt :
        if self.cmap_vmin is not None:
            self.q_vmin.setValue(self.cmap_vmin)
            self.q_vmin_chk.setChecked(True)
        else:
            self.q_vmin.setEnabled(False)
        if self.cmap_vmax is not None:
            self.q_vmax.setValue(self.cmap_vmax)
            self.q_vmax_chk.setChecked(True)
        else:
            self.q_vmax.setEnabled(False)
        # under/over mngmt :
        if self.cmap_under is not None:
            self.q_under.setText(str(self.cmap_under))
            self.q_under_chk.setChecked(True)
        else:
            self.q_under.setEnabled(False)
        if self.cmap_over is not None:
            self.q_over.setText(str(self.cmap_over))
            self.q_over_chk.setChecked(True)
        else:
            self.q_over.setEnabled(False)
        # Colorbar label :
        self.q_cblabel.setText(self.cblabel)
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


    def select_cmap(self):
        """Apply ui changes to the colormap
        """
        # Get colormap name :
        if self.q_cmap_invert.isChecked():
            self.cmap = self.q_cmap_list.currentText() + '_r'
        else:
            self.cmap = self.q_cmap_list.currentText()
        if self.q_auto_scale.isChecked():
            self.q_vmin_chk.setChecked(False)
            self.q_vmax_chk.setChecked(False)
        else:
            pass
        # Get vmin and vmax :
        if self.q_vmin_chk.isChecked():
            self.q_vmin.setEnabled(True)
            self.cmap_vmin = self.q_vmin.value()
        else:
            self.q_vmin.setEnabled(False)
            self.q_under_chk.setChecked(False)
            self.cmap_vmin = None
        if self.q_vmax_chk.isChecked():
            self.q_vmax.setEnabled(True)
            self.cmap_vmax = self.q_vmax.value()
        else:
            self.q_vmax.setEnabled(False)
            self.q_over_chk.setChecked(False)
            self.cmap_vmax = None
        # Get color under/over :
        if self.q_under_chk.isChecked():
            self.q_under.setEnabled(True)
            self.cmap_under = self.q_under.text()
        else:
            self.q_under.setEnabled(False)
            self.cmap_under = None
        if self.q_over_chk.isChecked():
            self.q_over.setEnabled(True)
            self.cmap_over = self.q_over.text()
        else:
            self.q_over.setEnabled(False)
            self.cmap_over = None
        self.cblabel = self.q_cblabel.text()
        # Manage tuple type for Under/Over :
        try:
            if isinstance(eval(self.cmap_under), tuple):
                self.cmap_under = eval(self.cmap_under)
        except:
            pass
        try:
            if isinstance(eval(self.cmap_over), tuple):
                self.cmap_over = eval(self.cmap_over)
        except:
            pass
        # Interact directly with cmap :
        if self.q_cmap_interact.isChecked():
            try:
                # If cortical projection never run :
                if self.current_mask is None:
                    self.cortical_projection()
                # Otherwise update colormap :
                else:
                    self._array2cmap(self.current_mask, non_zero=self.current_non_zero, vmin=self.cmap_vmin, vmax=self.cmap_vmax,
                                     under=self.cmap_under, over=self.cmap_over)
                # Update colorbar :
                self.cbupdate(self.current_mask, self.cmap, vmin=self.cmap_vmin, vmax=self.cmap_vmax,
                              under=self.cmap_under, over=self.cmap_over, label=self.cblabel, fontsize=self.cbfontsize)
            except:
                pass

