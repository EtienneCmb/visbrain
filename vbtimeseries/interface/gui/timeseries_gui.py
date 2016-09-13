# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timeseries_gui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1215, 917)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.tabSettings = QtGui.QTabWidget(self.centralwidget)
        self.tabSettings.setMaximumSize(QtCore.QSize(500, 16777215))
        self.tabSettings.setObjectName(_fromUtf8("tabSettings"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabSettings.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabSettings.addTab(self.tab_2, _fromUtf8(""))
        self.mainLayout.addWidget(self.tabSettings)
        self.gridVbt = QtGui.QGridLayout()
        self.gridVbt.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridVbt.setObjectName(_fromUtf8("gridVbt"))
        self.mainLayout.addLayout(self.gridVbt)
        self.horizontalLayout_2.addLayout(self.mainLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1215, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Time series", None))
        self.tabSettings.setTabText(self.tabSettings.indexOf(self.tab), _translate("MainWindow", "Tab 1", None))
        self.tabSettings.setTabText(self.tabSettings.indexOf(self.tab_2), _translate("MainWindow", "Tab 2", None))

