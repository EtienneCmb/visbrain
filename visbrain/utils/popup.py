"""Create basic popup."""

from PyQt4.Qt import *
from PyQt4 import QtGui

__all__ = ['ShortcutPopup']


def _translate(context, text, disambig):
    return QtGui.QApplication.translate(context, text, disambig, _encoding)


class ShortcutPopup(QWidget):
    """Popup window with the list of shorcuts."""

    def __init__(self):
        """Init."""
        QWidget.__init__(self)
        self.setGeometry(QRect(400, 200, 700, 600))
        layout = QtGui.QGridLayout(self)
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setStretchLastSection(False)
        layout.addWidget(self.table)
        # Add column names :
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = self.table.horizontalHeaderItem(0)
        item.setText("Keys")
        self.table.setHorizontalHeaderItem(1, item)
        item = self.table.horizontalHeaderItem(1)
        item.setText("Description")

    def set_shortcuts(self, shdic):
        """Fill table."""
        self.table.setRowCount(len(shdic))
        for num, k in enumerate(shdic):
            self.table.setItem(num, 0, QtGui.QTableWidgetItem(k[0]))
            self.table.setItem(num, 1, QtGui.QTableWidgetItem(k[1]))
