import os
from PyQt4.QtGui import *

from vispy import io
import vispy.scene.cameras as viscam

__all__ = ['uiSettings']

class uiSettings(object):

    """ui settings elements 
    """

    def __init__(self):
        # ***********************************************************
        # MENU
        # ***********************************************************
        self.progressBar.hide()

        # --------------- FILE ---------------
        # Screenshot :
        screenshot = QAction("Screenshot",self)
        screenshot.setShortcut("Ctrl+N")
        screenshot.triggered.connect(self.screenshot)
        self.menuFiles.addAction(screenshot)

        # Save :
        save = QAction("Save",self)
        save.setShortcut("Ctrl+S")
        save.triggered.connect(self.saveFile)
        self.menuFiles.addAction(save)

        # Load :
        openm = QAction("Load",self)
        openm.setShortcut("Ctrl+O")
        openm.triggered.connect(self.openFile)
        self.menuFiles.addAction(openm)

        # Quit :
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        self.menuFiles.addAction(exitAction)

        # Transform :
        self.actionProjection.triggered.connect(self.cortical_projection)
        self.actionRepartition.triggered.connect(self.cortical_repartition)

        # ***********************************************************
        # SETTINGS PANEL
        # ***********************************************************

        # Quick settings panel :
        self.actionQuick_settings.triggered.connect(self.show_hide_quick_settings)

        # Background color :
        self.bgd_green.valueChanged.connect(self.fcn_bgd_color)
        self.bgd_red.valueChanged.connect(self.fcn_bgd_color)
        self.bgd_blue.valueChanged.connect(self.fcn_bgd_color)

    def screenshot(self):
        """
        """
        filename = QFileDialog.getSaveFileName(self, 'Save screenshot', os.getenv('HOME'))
        img = self.view.canvas.render()
        # print(img.shape)
        # img = mapinterpolation(img, interpx=0.5, interpy=0.5)
        io.imsave(filename, img, format='png')
        if self.cbexport:
            cbimg = self.view.cbcanvas.render()
            if filename.find('.')+1:
                filename = filename.replace('.', '_colorbar.')
            else:
                filename += '_colorbar'
            io.imsave(filename, cbimg, format='png')



    def saveFile(self):
        """
        """
        filename = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'))
        # f = open(filename, 'w')
        # filedata = self.text.toPlainText()
        # f.write(filedata)
        # f.close()

    def openFile(self):
        """
        """
        filename = QFileDialog.getSaveFileName(self, 'Open File', os.getenv('HOME'))
        # f = open(filename, 'w')
        # filedata = self.text.toPlainText()
        # f.write(filedata)
        # f.close()


    def show_hide_quick_settings(self):
        """
        """
        isVisible = self.q_widget.isVisible()
        if not isVisible:
            self.q_widget.show()
        else:
            self.q_widget.hide()


    def fcn_bgd_color(self):
        """Change canvas background color
        """
        bgd = (self.bgd_red.value(), self.bgd_green.value(), self.bgd_blue.value())
        self.view.canvas.bgcolor = bgd