"""GUI interactions with sources and text."""
from .ui_objects import _run_method_if_needed
from ....utils import textline2color, safely_set_cbox
from ....io import dialog_color


class UiSources(object):
    """Main class for managing the interaction between the user and sources."""

    def __init__(self,):
        """Init."""
        # ====================== SOURCES ======================
        self._s_grp.clicked.connect(self._fcn_source_visible)
        self._s_symbol.currentIndexChanged.connect(self._fcn_source_symbol)
        self._s_radiusmin.valueChanged.connect(self._fcn_source_radius)
        self._s_radiusmax.valueChanged.connect(self._fcn_source_radius)
        self._s_edge_color.editingFinished.connect(self._fcn_source_edgecolor)
        self._s_edge_color_p.clicked.connect(self._fcn_source_edgecolor_p)
        self._s_edge_width.valueChanged.connect(self._fcn_source_edgewidth)
        self._s_alpha.valueChanged.connect(self._fcn_source_alpha)

        # ====================== TEXT ======================
        self._st_font_size.valueChanged.connect(self._fcn_text_fontsize)
        self._st_color.editingFinished.connect(self._fcn_text_color)
        self._st_color_p.clicked.connect(self._fcn_text_color_p)
        self._st_dx.valueChanged.connect(self._fcn_text_translate)
        self._st_dy.valueChanged.connect(self._fcn_text_translate)
        self._st_dz.valueChanged.connect(self._fcn_text_translate)










        # self._sourcesPickdisp.currentIndexChanged.connect(
        #     self._fcn_sources_display)
        # # ---------- Change marker look ----------
        # # Symbol :
        # sym = [self.s_Symbol.itemText(i) for i in range(self.s_Symbol.count())]
        # self.s_Symbol.setCurrentIndex(sym.index(self.sources.symbol))
        # self.s_Symbol.currentIndexChanged.connect(self._fcn_sources_look)
        # # Edge color / width :
        # edgcol = np.ndarray.tolist(self.sources.edgecolor.ravel())
        # self.s_EdgeColor.setText(str(tuple(edgcol)))
        # self.s_EdgeColor.editingFinished.connect(self._fcn_sources_look)
        # self.s_EdgeWidth.setValue(self.sources.edgewidth)
        # self.s_EdgeWidth.valueChanged.connect(self._fcn_sources_look)
        # # ---------- Marker's radius ----------
        # self.s_radiusMin.setValue(self.sources.radiusmin)
        # self.s_radiusMin.valueChanged.connect(self._fcn_sources_radius)
        # self.s_radiusMax.setValue(self.sources.radiusmax)
        # self.s_radiusMax.valueChanged.connect(self._fcn_sources_radius)
        # self.s_Scaling.setChecked(self.sources.scaling)
        # self.s_Scaling.clicked.connect(self._fcn_sources_radius)

        # # ====================== SOURCE'S TEXT ======================
        # if self.sources.stext is None:
        #     self.grpText.setChecked(False)
        #     self.q_stextcolor.setEnabled(False)
        #     self.q_stextsize.setEnabled(False)
        # else:
        #     self.grpText.setChecked(True)
        #     self.q_stextsize.setValue(self.sources.stextsize)
        #     txtcol = np.ndarray.tolist(self.sources.stextcolor.ravel())
        #     self.q_stextcolor.setText(str(tuple(txtcol)))
        #     self.x_text.setValue(self.sources.stextshift[0])
        #     self.y_text.setValue(self.sources.stextshift[1])
        #     self.z_text.setValue(self.sources.stextshift[2])
        # self.grpText.clicked.connect(self._fcn_textupdate)
        # self.q_stextsize.valueChanged.connect(self._fcn_textupdate)
        # self.q_stextcolor.editingFinished.connect(self._fcn_textupdate)
        # self.x_text.valueChanged.connect(self._fcn_textupdate)
        # self.y_text.valueChanged.connect(self._fcn_textupdate)
        # self.z_text.valueChanged.connect(self._fcn_textupdate)

        # # ====================== PROJECTION ======================
        # # Radius :
        # self._uitRadius.setValue(self._tradius)
        # self._uitApply.clicked.connect(self._fcn_sources_proj)
        # # Contribute :
        # self._uitContribute.setChecked(self._tcontribute)

        # # ====================== TIME-SERIES ======================
        # # Groupbox :
        # self.grpTs.clicked.connect(self._fcn_ts_update)
        # # Width :
        # self._tsWidth.setValue(self.tseries.width)
        # self._tsWidth.valueChanged.connect(self._fcn_ts_update)
        # # Lw :
        # self._tsLw.setValue(self.tseries.lw)
        # self._tsLw.valueChanged.connect(self._fcn_ts_update)
        # # Amplitude :
        # self._tsAmp.setValue(self.tseries.amp)
        # self._tsAmp.valueChanged.connect(self._fcn_ts_update)
        # # Color :
        # self._tsColor.setText(str(color2tuple(self.tseries.color)))
        # self._tsColor.editingFinished.connect(self._fcn_ts_update)
        # # (dx, dy, dz) :
        # self._tsDx.setValue(self.tseries.dxyz[0])
        # self._tsDy.setValue(self.tseries.dxyz[1])
        # self._tsDz.setValue(self.tseries.dxyz[2])
        # self._tsDx.valueChanged.connect(self._fcn_ts_update)
        # self._tsDy.valueChanged.connect(self._fcn_ts_update)
        # self._tsDz.valueChanged.connect(self._fcn_ts_update)

        # # ====================== PICTURES ======================
        # if self.pic.mesh.name is not 'NonePic':
        #     # Groupbox :
        #     self.grpPic.clicked.connect(self._fcn_pic_update)
        #     # Width :
        #     self._picWidth.setValue(self.pic.mesh.w)
        #     self._picWidth.valueChanged.connect(self._fcn_pic_update)
        #     # Height :
        #     self._picHeight.setValue(self.pic.mesh.h)
        #     self._picHeight.valueChanged.connect(self._fcn_pic_update)
        #     # (dx, dy, dz) :
        #     self._picDx.setValue(self.pic.mesh._dxyz[0])
        #     self._picDx.valueChanged.connect(self._fcn_pic_update)
        #     self._picDy.setValue(self.pic.mesh._dxyz[1])
        #     self._picDy.valueChanged.connect(self._fcn_pic_update)
        #     self._picDz.setValue(self.pic.mesh._dxyz[2])
        #     self._picDz.valueChanged.connect(self._fcn_pic_update)

        # # ====================== TABLE ======================
        # if self.sources.name is not 'NoneSources':
        #     # Set table length :
        #     n_sources = self.sources.xyz.shape[0]
        #     self._sourcesTable.setRowCount(n_sources)
        #     # Enable table :
        #     self._sourcesTable.setEnabled(True)
        #     rg = np.arange(n_sources)
        #     # Source's text :
        #     if self.sources.stextmesh.name == 'NoneText':
        #         txt = np.full((n_sources), 'e')
        #         txt = np.core.defchararray.add(txt, rg.astype(str))
        #     else:
        #         txt = self.sources.stext
        #     for k in rg:
        #         # Text :
        #         self._sourcesTable.setItem(k, 0, QtWidgets.QTableWidgetItem(
        #             txt[k]))
        #         # X :
        #         self._sourcesTable.setItem(k, 1, QtWidgets.QTableWidgetItem(
        #             str(self.sources.xyz[k, 0])))
        #         # Y :
        #         self._sourcesTable.setItem(k, 2, QtWidgets.QTableWidgetItem(
        #             str(self.sources.xyz[k, 1])))
        #         # Z :
        #         self._sourcesTable.setItem(k, 3, QtWidgets.QTableWidgetItem(
        #             str(self.sources.xyz[k, 2])))
        #     # Connect table :
        #     self._sourcesTable.itemSelectionChanged.connect(self._fcn_goto_cs)

    # =====================================================================
    # SOURCES
    # =====================================================================
    def _sources_to_gui(self):
        """Update GUI using a source object."""
        obj = self._get_select_object()
        self._s_grp.setChecked(obj.visible_obj)
        safely_set_cbox(self._s_symbol, obj.symbol)
        self._s_radiusmin.setValue(obj.radius_min)
        self._s_radiusmax.setValue(obj.radius_max)
        self._s_edge_color.setText(str(obj.edge_color))
        self._s_edge_width.setValue(obj.edge_width)
        self._s_alpha.setValue(obj.alpha * 100.)
        self._st_font_size.setValue(obj.text_size)
        self._st_color.setText(str(obj.text_color))
        dxyz = obj.text_translate
        self._st_dx.setValue(dxyz[0])
        self._st_dy.setValue(dxyz[1])
        self._st_dz.setValue(dxyz[2])

    @_run_method_if_needed
    def _fcn_source_visible(self):
        """Display / hide source object."""
        viz = self._s_grp.isChecked()
        self._get_select_object().visible_obj = viz
        self._st_grp.setEnabled(viz)

    @_run_method_if_needed
    def _fcn_source_symbol(self):
        """Change the source symbol."""
        self._get_select_object().symbol = self._s_symbol.currentText()

    @_run_method_if_needed
    def _fcn_source_radius(self):
        """Change the radius (min, max)."""
        obj = self._get_select_object()
        obj._radius_min = self._s_radiusmin.value()  # don't update
        obj.radius_max = self._s_radiusmax.value()   # update
        self._vbNode.update()
        self.sources.update()

    @_run_method_if_needed
    def _fcn_source_edgecolor(self):
        """Update source edge color."""
        color = textline2color(str(self._s_edge_color.text()))[1]
        self._get_select_object().edge_color = color

    def _fcn_source_edgecolor_p(self):
        """Edge color picker."""
        color = dialog_color()
        self._s_edge_color.setText(color)
        self._fcn_source_edgecolor()

    @_run_method_if_needed
    def _fcn_source_edgewidth(self):
        """Update source edge width."""
        self._get_select_object().edge_width = self._s_edge_width.value()

    @_run_method_if_needed
    def _fcn_source_alpha(self):
        """Update source alpha."""
        self._get_select_object().alpha = self._s_alpha.value() / 100.

    # =====================================================================
    # TEXT
    # =====================================================================
    @_run_method_if_needed
    def _fcn_text_fontsize(self):
        """Update text font size."""
        self._get_select_object().text_size = self._st_font_size.value()

    @_run_method_if_needed
    def _fcn_text_color(self):
        """Update text color."""
        color = textline2color(str(self._st_color.text()))[1]
        self._get_select_object().text_color = color

    def _fcn_text_color_p(self):
        """Text color picker."""
        color = dialog_color()
        self._st_color.setText(color)
        self._fcn_text_color()

    def _fcn_text_translate(self):
        """Translate text."""
        tr = (self._st_dx.value(), self._st_dy.value(), self._st_dz.value())
        self._get_select_object().text_translate = tr
















    # def _fcn_sources_display(self):
    #     """Select which part of sources to display."""
    #     idx = int(self._sourcesPickdisp.currentIndex())
    #     if idx == 0:
    #         self.sources_display(select='all')
    #     elif idx == 1:
    #         self.sources_display(select='none')
    #     elif idx == 2:
    #         self.sources_display(select='left')
    #     elif idx == 3:
    #         self.sources_display(select='right')
    #     elif idx == 4:
    #         self.sources_display(select='inside')
    #     elif idx == 5:
    #         self.sources_display(select='outside')

    # def _fcn_sources_look(self):
    #     """Change how marker looks."""
    #     self.sources.symbol = str(self.s_Symbol.currentText())
    #     self.sources.edgecolor = textline2color(
    #         str(self.s_EdgeColor.text()))[1]
    #     self.sources.edgewidth = self.s_EdgeWidth.value()
    #     self.sources.update()

    # def _fcn_sources_radius(self):
    #     """Marker radius related functions."""
    #     self.sources.scaling = self.s_Scaling.isChecked()
    #     self.sources.radiusmin = self.s_radiusMin.value()
    #     self.sources.radiusmax = self.s_radiusMax.value()
    #     self.sources.array2radius()
    #     self.sources.update()

    # # =====================================================================
    # # PROJECTION
    # # =====================================================================
    # def _fcn_update_proj_list(self):
    #     """Update the available projection list objects."""
    #     self._uitProjectOn.clear()
    #     self._uitProjectOn.addItems(list(self._tobj.keys()))

    # def _fcn_sources_proj(self):
    #     """Apply source projection."""
    #     # Get projection radius :
    #     new_radius = self._uitRadius.value()
    #     if self._tradius != new_radius:
    #         self._tradius = new_radius
    #         self._cleanProj()
    #     # Get if activity has to be projected on surface / ROI :
    #     new_projecton = str(self._uitProjectOn.currentText()).lower()
    #     if self._tprojecton != new_projecton:
    #         self._tprojecton = new_projecton
    #         self._cleanProj()
    #     # Get if projection has to contribute on both hemisphere :
    #     new_contribute = self._uitContribute.isChecked()
    #     if self._tcontribute != new_contribute:
    #         self._tcontribute = new_contribute
    #         self._cleanProj()
    #     # Run either the activity / repartition projection :
    #     idxproj = int(self._uitPickProj.currentIndex())
    #     if idxproj == 0:
    #         self._tprojectas = 'activity'
    #     elif idxproj == 1:
    #         self._tprojectas = 'repartition'
    #     self._sourcesProjection()

    # # =====================================================================
    # # TEXT
    # # =====================================================================
    # def _fcn_textupdate(self):
    #     """Update text of each sources.

    #     This method can be used to set text visible / hide, to translate the
    #     text in order to not cover the source sphere and to change the color /
    #     fontsize of each text. Finally, this method update the text according
    #     to selected properties.
    #     """
    #     # Text visible :
    #     self.sources.stextmesh.visible = self.grpText.isChecked()
    #     # Translate text (do not cover the source):
    #     t = vist.STTransform(translate=list([self.x_text.value(),
    #                                          self.y_text.value(),
    #                                          self.z_text.value()]))
    #     self.sources.stextmesh.transform = t
    #     # Color and fontsize :
    #     _, self.sources.stextcolor = textline2color(
    #         str(self.q_stextcolor.text()))
    #     self.sources.stextsize = self.q_stextsize.value()
    #     # Update text :
    #     self.sources.text_update()

    # # =====================================================================
    # # TIME-SERIES
    # # =====================================================================
    # def _fcn_ts_update(self):
    #     """Update time-series properties."""
    #     width = self._tsWidth.value()
    #     amp = self._tsAmp.value()
    #     lw = self._tsLw.value()
    #     dxyz = (self._tsDx.value(), self._tsDy.value(), self._tsDz.value())
    #     color = textline2color(str(self._tsColor.text()))[1]
    #     viz = self.grpTs.isChecked()
    #     self.tseries.set_data(width=width, amp=amp, dxyz=dxyz, color=color,
    #                           lw=lw, visible=viz)

    # # =====================================================================
    # # TIME-SERIES
    # # =====================================================================
    # def _fcn_pic_update(self):
    #     """Update pictures."""
    #     # Visibility :
    #     self.pic.mesh.visible = self.grpPic.isChecked()
    #     # Get width, height and (dx, dy, dz) :
    #     w, h = self._picWidth.value(), self._picHeight.value()
    #     x, y, z = self._picDx.value(), self._picDy.value(), self._picDz.value()
    #     # Get latest color properties :
    #     kwargs = self.cbqt.cbobjs._objs['Pictures'].to_kwargs()
    #     # Update pictures :
    #     self.pic.mesh.set_data(width=w, height=h, dxyz=(x, y, z), **kwargs)
    #     self.pic.mesh.update()

    # # =====================================================================
    # # GOTO CROSS-SECTIONS
    # # =====================================================================
    # def _fcn_goto_cs(self):
    #     """Cross-section at source location."""
    #     # Get selected row and xyz :
    #     row = self._sourcesTable.currentRow()
    #     xyz = self.sources.xyz[row, :]
    #     # Set menu cross-sections menu checked :
    #     self.grpSec.setChecked(True)
    #     self._fcn_crossec_viz()
    #     # Get transformation and apply to xyz :
    #     ixyz = self.volume.transform.imap(xyz)[0:-1]
    #     ixyz = np.round(ixyz).astype(int)
    #     # Set it to cross-sections sliders :
    #     self._csSagit.setValue(ixyz[0])
    #     self._csCoron.setValue(ixyz[1])
    #     self._csAxial.setValue(ixyz[2])
    #     self._fcn_crossec_move()
