# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/etienne/Toolbox/visbrain/visbrain/colorbar/gui/cbar_gui.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1198, 908)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.guiW = QtWidgets.QWidget(self.centralwidget)
        self.guiW.setMinimumSize(QtCore.QSize(300, 0))
        self.guiW.setMaximumSize(QtCore.QSize(400, 16777215))
        self.guiW.setObjectName("guiW")
        self.horizontalLayout_2.addWidget(self.guiW)
        self.vizW = QtWidgets.QHBoxLayout()
        self.vizW.setObjectName("vizW")
        self.horizontalLayout_2.addLayout(self.vizW)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1198, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuConfiguration = QtWidgets.QMenu(self.menuFile)
        self.menuConfiguration.setObjectName("menuConfiguration")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuCbarScreenshot = QtWidgets.QAction(MainWindow)
        self.menuCbarScreenshot.setObjectName("menuCbarScreenshot")
        self.menuCbarSaveConfig = QtWidgets.QAction(MainWindow)
        self.menuCbarSaveConfig.setObjectName("menuCbarSaveConfig")
        self.menuCbarLoadConfig = QtWidgets.QAction(MainWindow)
        self.menuCbarLoadConfig.setObjectName("menuCbarLoadConfig")
        self.menuConfiguration.addAction(self.menuCbarSaveConfig)
        self.menuConfiguration.addAction(self.menuCbarLoadConfig)
        self.menuFile.addAction(self.menuConfiguration.menuAction())
        self.menuFile.addAction(self.menuCbarScreenshot)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Colorbar editor"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuConfiguration.setTitle(_translate("MainWindow", "Configuration"))
        self.menuCbarScreenshot.setText(_translate("MainWindow", "Screenshot"))
        self.menuCbarSaveConfig.setText(_translate("MainWindow", "Save"))
        self.menuCbarLoadConfig.setText(_translate("MainWindow", "Load"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

