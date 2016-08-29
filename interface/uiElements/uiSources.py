

class uiSources(object):

    """docstring for uiSources
    """

    def __init__(self,):
        self.s_allSources.clicked.connect(self.disp_all_sources)
        self.s_noSources.clicked.connect(self.hide_all_sources)
        self.s_LeftH.clicked.connect(self.left_right_H)
        self.s_RightH.clicked.connect(self.left_right_H)
        self.s_Inside.clicked.connect(self.inside_outside_H)
        self.s_Outside.clicked.connect(self.inside_outside_H)
        
    def disp_all_sources(self):
        """Display sources in both hemisphere
        """
        self.display(select='all')

    def hide_all_sources(self):
        """Hide all sources
        """
        self.display(select='none')

    def left_right_H(self):
        """Display sources either in the left or right hemisphere
        """
        if self.s_LeftH.isChecked():
            self.display(select='left')
        if self.s_RightH.isChecked():
            self.display(select='right')

    def inside_outside_H(self):
        """Display sources either inside or outside the MNI brain
        """
        if self.s_Inside.isChecked():
            self.display(select='inside')
        elif self.s_Outside.isChecked():
            self.display(select='outside')