"""Main class for managing the interaction between the user and sources.

Manage how sources has to be displayed (all / none / left or right hemisphere /
inside or outside [experimental] of the brain).
This script is also essential to update the text object of each source and make
the bridge between the user and the GUI.
"""

import vispy.visuals.transforms as vist

from ...utils import textline2color


class uiSources(object):
    """Main class for managing the interaction between the user and sources."""

    def __init__(self,):
        """Init."""
        # Sources :
        self.show_Sources.clicked.connect(self._fcn_disp_sources)
        self.s_LeftH.clicked.connect(self._fcn_left_right_H)
        self.s_RightH.clicked.connect(self._fcn_left_right_H)
        self.s_Inside.clicked.connect(self._fcn_inside_outside_H)
        self.s_Outside.clicked.connect(self._fcn_inside_outside_H)

        # Text elements :
        if self.sources.stext is None:
            self.q_stextshow.setEnabled(False)
            self.q_stextcolor.setEnabled(False)
            self.q_stextsize.setEnabled(False)
        else:
            self.q_stextshow.setChecked(True)
            self.q_stextsize.setValue(self.sources.stextsize)
            self.q_stextcolor.setText(str(self.sources.stextcolor))
            self.x_text.setValue(self.sources.stextshift[0])
            self.y_text.setValue(self.sources.stextshift[1])
            self.z_text.setValue(self.sources.stextshift[2])
        self.q_stextshow.clicked.connect(self._fcn_textupdate)
        self.q_stextsize.valueChanged.connect(self._fcn_textupdate)
        self.q_stextcolor.editingFinished.connect(self._fcn_textupdate)
        self.x_text.valueChanged.connect(self._fcn_textupdate)
        self.y_text.valueChanged.connect(self._fcn_textupdate)
        self.z_text.valueChanged.connect(self._fcn_textupdate)

    def _fcn_disp_sources(self):
        """Display sources either All or None of the sources.

        This method call the s_display() source's transformation method.
        """
        if self.show_Sources.isChecked():
            self.s_display(select='all')
        else:
            self.s_display(select='none')

    def _fcn_left_right_H(self):
        """Display sources either in the Left or Right hemisphere.

        This method call the s_display() source's transformation method.
        """
        if self.s_LeftH.isChecked():
            self.s_display(select='left')
        if self.s_RightH.isChecked():
            self.s_display(select='right')

    def _fcn_inside_outside_H(self):
        """Display sources either inside or outside the MNI brain.

        This method call the s_display() source's transformation method.
        """
        if self.s_Inside.isChecked():
            self.s_display(select='inside')
        elif self.s_Outside.isChecked():
            self.s_display(select='outside')

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
        _, self.sources.stextcolor = textline2color(self.q_stextcolor.text())
        self.sources.stextsize = self.q_stextsize.value()
        # Update text :
        self.sources.text_update()
