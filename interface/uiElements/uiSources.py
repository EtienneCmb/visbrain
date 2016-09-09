import vispy.visuals.transforms as vist

from ...utils import textline2color, color2vb

class uiSources(object):

    """docstring for uiSources
    """

    def __init__(self,):
        # Sources :
        self.show_Sources.clicked.connect(self.disp_sources)
        self.s_LeftH.clicked.connect(self.left_right_H)
        self.s_RightH.clicked.connect(self.left_right_H)
        self.s_Inside.clicked.connect(self.inside_outside_H)
        self.s_Outside.clicked.connect(self.inside_outside_H)
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
        self.q_stextshow.clicked.connect(self.fcn_textupdate)
        self.q_stextsize.valueChanged.connect(self.fcn_textupdate)
        self.q_stextcolor.editingFinished.connect(self.fcn_textupdate)
        self.x_text.valueChanged.connect(self.fcn_textupdate)
        self.y_text.valueChanged.connect(self.fcn_textupdate)
        self.z_text.valueChanged.connect(self.fcn_textupdate)

        
    def disp_sources(self):
        """Show/hide sources
        """
        if self.show_Sources.isChecked():
            self.s_display(select='all')
        else:
            self.s_display(select='none')

    def left_right_H(self):
        """Display sources either in the left or right hemisphere
        """
        if self.s_LeftH.isChecked():
            self.s_display(select='left')
        if self.s_RightH.isChecked():
            self.s_display(select='right')

    def inside_outside_H(self):
        """Display sources either inside or outside the MNI brain
        """
        if self.s_Inside.isChecked():
            self.s_display(select='inside')
        elif self.s_Outside.isChecked():
            self.s_display(select='outside')

    def fcn_textupdate(self):
        """Update text sources
        """
        # Text :
        self.sources.stextmesh.visible = self.q_stextshow.isChecked()
        t = vist.STTransform(translate=list([self.x_text.value(), self.y_text.value(), self.z_text.value()]))
        self.sources.stextmesh.transform = t
        # Color and fontsize :
        _, self.sources.stextcolor = textline2color(self.q_stextcolor.text())
        self.sources.stextsize = self.q_stextsize.value()
        # Update text :
        self.sources.text_update()
