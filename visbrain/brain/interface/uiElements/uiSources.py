"""Main class for managing the interaction between the user and sources.

Manage how sources has to be displayed (all / none / left or right hemisphere /
inside or outside [experimental] of the brain).
This script is also essential to update the text object of each source and make
the bridge between the user and the GUI.
"""

import numpy as np

import vispy.visuals.transforms as vist

from ....utils import textline2color


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
            self.q_stextshow.setEnabled(False)
            self.q_stextcolor.setEnabled(False)
            self.q_stextsize.setEnabled(False)
        else:
            self.q_stextshow.setChecked(True)
            self.q_stextsize.setValue(self.sources.stextsize)
            txtcol = np.ndarray.tolist(self.sources.stextcolor.ravel())
            self.q_stextcolor.setText(str(tuple(txtcol)))
            self.x_text.setValue(self.sources.stextshift[0])
            self.y_text.setValue(self.sources.stextshift[1])
            self.z_text.setValue(self.sources.stextshift[2])
        self.q_stextshow.clicked.connect(self._fcn_textupdate)
        self.q_stextsize.valueChanged.connect(self._fcn_textupdate)
        self.q_stextcolor.editingFinished.connect(self._fcn_textupdate)
        self.x_text.valueChanged.connect(self._fcn_textupdate)
        self.y_text.valueChanged.connect(self._fcn_textupdate)
        self.z_text.valueChanged.connect(self._fcn_textupdate)

        # ====================== PROJECTION ======================
        self._uitRadius.setValue(self._tradius)
        self._uitApply.clicked.connect(self._fcn_sourcesProjection)

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
        """Update the avaible projction list objects."""
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
        self.sources.stextmesh.visible = self.q_stextshow.isChecked()
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
