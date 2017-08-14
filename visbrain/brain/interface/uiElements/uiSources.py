"""Main class for managing the interaction between the user and sources.

Manage how sources has to be displayed (all / none / left or right hemisphere /
inside or outside [experimental] of the brain).
This script is also essential to update the text object of each source and make
the bridge between the user and the GUI.
"""

import numpy as np
from PyQt5 import QtWidgets

import vispy.visuals.transforms as vist

from ....utils import textline2color, color2tuple


class uiSources(object):
    """Main class for managing the interaction between the user and sources."""

    def __init__(self,):
        """Init."""
        # ====================== SOURCES ======================
        # ---------- Visibility ----------
        self._sourcesPickdisp.currentIndexChanged.connect(
            self._fcn_sourcesDisplay)
        # ---------- Change marker look ----------
        # Symbol :
        sym = [self.s_Symbol.itemText(i) for i in range(self.s_Symbol.count())]
        self.s_Symbol.setCurrentIndex(sym.index(self.sources.symbol))
        self.s_Symbol.currentIndexChanged.connect(self._fcn_MarkerLook)
        # Edge color / width :
        edgcol = np.ndarray.tolist(self.sources.edgecolor.ravel())
        self.s_EdgeColor.setText(str(tuple(edgcol)))
        self.s_EdgeColor.editingFinished.connect(self._fcn_MarkerLook)
        self.s_EdgeWidth.setValue(self.sources.edgewidth)
        self.s_EdgeWidth.valueChanged.connect(self._fcn_MarkerLook)
        # ---------- Marker's radius ----------
        self.s_radiusMin.setValue(self.sources.radiusmin)
        self.s_radiusMin.valueChanged.connect(self._fcn_MarkerRadius)
        self.s_radiusMax.setValue(self.sources.radiusmax)
        self.s_radiusMax.valueChanged.connect(self._fcn_MarkerRadius)
        self.s_Scaling.setChecked(self.sources.scaling)
        self.s_Scaling.clicked.connect(self._fcn_MarkerRadius)

        # ====================== SOURCE'S TEXT ======================
        if self.sources.stext is None:
            self.grpText.setChecked(False)
            self.q_stextcolor.setEnabled(False)
            self.q_stextsize.setEnabled(False)
        else:
            self.grpText.setChecked(True)
            self.q_stextsize.setValue(self.sources.stextsize)
            txtcol = np.ndarray.tolist(self.sources.stextcolor.ravel())
            self.q_stextcolor.setText(str(tuple(txtcol)))
            self.x_text.setValue(self.sources.stextshift[0])
            self.y_text.setValue(self.sources.stextshift[1])
            self.z_text.setValue(self.sources.stextshift[2])
        self.grpText.clicked.connect(self._fcn_textupdate)
        self.q_stextsize.valueChanged.connect(self._fcn_textupdate)
        self.q_stextcolor.editingFinished.connect(self._fcn_textupdate)
        self.x_text.valueChanged.connect(self._fcn_textupdate)
        self.y_text.valueChanged.connect(self._fcn_textupdate)
        self.z_text.valueChanged.connect(self._fcn_textupdate)

        # ====================== PROJECTION ======================
        # Radius :
        self._uitRadius.setValue(self._tradius)
        self._uitApply.clicked.connect(self._fcn_sourcesProjection)
        # Contribute :
        self._uitContribute.setChecked(self._tcontribute)

        # ====================== TIME-SERIES ======================
        # Groupbox :
        self.grpTs.clicked.connect(self._fcn_ts_update)
        # Width :
        self._tsWidth.setValue(self.tseries.width)
        self._tsWidth.valueChanged.connect(self._fcn_ts_update)
        # Lw :
        self._tsLw.setValue(self.tseries.lw)
        self._tsLw.valueChanged.connect(self._fcn_ts_update)
        # Amplitude :
        self._tsAmp.setValue(self.tseries.amp)
        self._tsAmp.valueChanged.connect(self._fcn_ts_update)
        # Color :
        self._tsColor.setText(str(color2tuple(self.tseries.color)))
        self._tsColor.editingFinished.connect(self._fcn_ts_update)
        # (dx, dy, dz) :
        self._tsDx.setValue(self.tseries.dxyz[0])
        self._tsDy.setValue(self.tseries.dxyz[1])
        self._tsDz.setValue(self.tseries.dxyz[2])
        self._tsDx.valueChanged.connect(self._fcn_ts_update)
        self._tsDy.valueChanged.connect(self._fcn_ts_update)
        self._tsDz.valueChanged.connect(self._fcn_ts_update)

        # ====================== PICTURES ======================
        if self.pic.mesh.name is not 'NonePic':
            # Groupbox :
            self.grpPic.clicked.connect(self._fcn_pic_update)
            # Width :
            self._picWidth.setValue(self.pic.mesh.w)
            self._picWidth.valueChanged.connect(self._fcn_pic_update)
            # Height :
            self._picHeight.setValue(self.pic.mesh.h)
            self._picHeight.valueChanged.connect(self._fcn_pic_update)
            # (dx, dy, dz) :
            self._picDx.setValue(self.pic.mesh._dxyz[0])
            self._picDx.valueChanged.connect(self._fcn_pic_update)
            self._picDy.setValue(self.pic.mesh._dxyz[1])
            self._picDy.valueChanged.connect(self._fcn_pic_update)
            self._picDz.setValue(self.pic.mesh._dxyz[2])
            self._picDz.valueChanged.connect(self._fcn_pic_update)

        # ====================== TABLE ======================
        if self.sources.name is not 'NoneSources':
            # Set table length :
            n_sources = self.sources.xyz.shape[0]
            self._sourcesTable.setRowCount(n_sources)
            # Enable table :
            self._sourcesTable.setEnabled(True)
            rg = np.arange(n_sources)
            # Source's text :
            if self.sources.stextmesh.name == 'NoneText':
                txt = np.full((n_sources), 'e')
                txt = np.core.defchararray.add(txt, rg.astype(str))
            else:
                txt = self.sources.stext
            for k in rg:
                # Text :
                self._sourcesTable.setItem(k, 0, QtWidgets.QTableWidgetItem(
                    txt[k]))
                # X :
                self._sourcesTable.setItem(k, 1, QtWidgets.QTableWidgetItem(
                    str(self.sources.xyz[k, 0])))
                # Y :
                self._sourcesTable.setItem(k, 2, QtWidgets.QTableWidgetItem(
                    str(self.sources.xyz[k, 1])))
                # Z :
                self._sourcesTable.setItem(k, 3, QtWidgets.QTableWidgetItem(
                    str(self.sources.xyz[k, 2])))
            # Connect table :
            self._sourcesTable.itemSelectionChanged.connect(self._fcn_goto_cs)

    # =====================================================================
    # SOURCES
    # =====================================================================
    def _fcn_sourcesDisplay(self):
        """Select which part of sources to display."""
        idx = int(self._sourcesPickdisp.currentIndex())
        if idx == 0:
            self.sources_display(select='all')
        elif idx == 1:
            self.sources_display(select='none')
        elif idx == 2:
            self.sources_display(select='left')
        elif idx == 3:
            self.sources_display(select='right')
        elif idx == 4:
            self.sources_display(select='inside')
        elif idx == 5:
            self.sources_display(select='outside')

    def _fcn_MarkerLook(self):
        """Change how marker looks."""
        self.sources.symbol = str(self.s_Symbol.currentText())
        self.sources.edgecolor = textline2color(
            str(self.s_EdgeColor.text()))[1]
        self.sources.edgewidth = self.s_EdgeWidth.value()
        self.sources.update()

    def _fcn_MarkerRadius(self):
        """Marker radius related functions."""
        self.sources.scaling = self.s_Scaling.isChecked()
        self.sources.radiusmin = self.s_radiusMin.value()
        self.sources.radiusmax = self.s_radiusMax.value()
        self.sources.array2radius()
        self.sources.update()

    # =====================================================================
    # PROJECTION
    # =====================================================================
    def _fcn_updateProjList(self):
        """Update the available projection list objects."""
        self._uitProjectOn.clear()
        self._uitProjectOn.addItems(list(self._tobj.keys()))

    def _fcn_sourcesProjection(self):
        """Apply source projection."""
        # Get projection radius :
        new_radius = self._uitRadius.value()
        if self._tradius != new_radius:
            self._tradius = new_radius
            self._cleanProj()
        # Get if activity has to be projected on surface / ROI :
        new_projecton = str(self._uitProjectOn.currentText()).lower()
        if self._tprojecton != new_projecton:
            self._tprojecton = new_projecton
            self._cleanProj()
        # Get if projection has to contribute on both hemisphere :
        new_contribute = self._uitContribute.isChecked()
        if self._tcontribute != new_contribute:
            self._tcontribute = new_contribute
            self._cleanProj()
        # Run either the activity / repartition projection :
        idxproj = int(self._uitPickProj.currentIndex())
        if idxproj == 0:
            self._tprojectas = 'activity'
        elif idxproj == 1:
            self._tprojectas = 'repartition'
        self._sourcesProjection()

    # =====================================================================
    # TEXT
    # =====================================================================
    def _fcn_textupdate(self):
        """Update text of each sources.

        This method can be used to set text visible / hide, to translate the
        text in order to not cover the source sphere and to change the color /
        fontsize of each text. Finally, this method update the text according
        to selected properties.
        """
        # Text visible :
        self.sources.stextmesh.visible = self.grpText.isChecked()
        # Translate text (do not cover the source):
        t = vist.STTransform(translate=list([self.x_text.value(),
                                             self.y_text.value(),
                                             self.z_text.value()]))
        self.sources.stextmesh.transform = t
        # Color and fontsize :
        _, self.sources.stextcolor = textline2color(
            str(self.q_stextcolor.text()))
        self.sources.stextsize = self.q_stextsize.value()
        # Update text :
        self.sources.text_update()

    # =====================================================================
    # TIME-SERIES
    # =====================================================================
    def _fcn_ts_update(self):
        """Update time-series properties."""
        width = self._tsWidth.value()
        amp = self._tsAmp.value()
        lw = self._tsLw.value()
        dxyz = (self._tsDx.value(), self._tsDy.value(), self._tsDz.value())
        color = textline2color(str(self._tsColor.text()))[1]
        viz = self.grpTs.isChecked()
        self.tseries.set_data(width=width, amp=amp, dxyz=dxyz, color=color,
                              lw=lw, visible=viz)

    # =====================================================================
    # TIME-SERIES
    # =====================================================================
    def _fcn_pic_update(self):
        """Update pictures."""
        # Visibility :
        self.pic.mesh.visible = self.grpPic.isChecked()
        # Get width, height and (dx, dy, dz) :
        w, h = self._picWidth.value(), self._picHeight.value()
        x, y, z = self._picDx.value(), self._picDy.value(), self._picDz.value()
        # Get latest color properties :
        kwargs = self.cbqt.cbobjs._objs['Pictures'].to_kwargs()
        # Update pictures :
        self.pic.mesh.set_data(width=w, height=h, dxyz=(x, y, z), **kwargs)
        self.pic.mesh.update()

    # =====================================================================
    # GOTO CROSS-SECTIONS
    # =====================================================================
    def _fcn_goto_cs(self):
        """Cross-section at source location."""
        # Get selected row and xyz :
        row = self._sourcesTable.currentRow()
        xyz = self.sources.xyz[row, :]
        # Set menu cross-sections menu checked :
        self.grpSec.setChecked(True)
        self._fcn_crossec_viz()
        # Get transformation and apply to xyz :
        ixyz = self.volume.transform.imap(xyz)[0:-1]
        ixyz = np.round(ixyz).astype(int)
        # Set it to cross-sections sliders :
        self._csSagit.setValue(ixyz[0])
        self._csCoron.setValue(ixyz[1])
        self._csAxial.setValue(ixyz[2])
        self._fcn_crossec_move()
