"""Enable to annotate a Sleep file."""

from PyQt5 import QtWidgets

__all__ = ['uiAnnotate']


class uiAnnotate(object):
    """Interactions with annotations."""

    def __init__(self):
        """Init."""
        # Add/remove line :
        self._AnnotateAdd.clicked.connect(self._fcn_annotateAdd)
        self._AnnotateRm.clicked.connect(self._fcn_annotateRm)
        self._AnnotateTable.itemSelectionChanged.connect(
            self._fcn_annotateGoto)

    def _fcn_annotateAdd(self):
        """Add a ligne to the annotation table."""
        # Add a ligne :
        self._AnnotateTable.setRowCount(self._AnnotateTable.rowCount() + 1)
        rw = self._AnnotateTable.rowCount() - 1
        # Get the current window :
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        win = self._SigWin.value()
        xlim = (val*step, val*step+win)
        # Automatically set the window :
        self._AnnotateTable.setItem(rw, 0, QtWidgets.QTableWidgetItem(
                                                              str(xlim[0])))
        self._AnnotateTable.setItem(rw, 1, QtWidgets.QTableWidgetItem(
                                                              str(xlim[1])))
        # Select the text item :
        self._AnnotateTable.setCurrentCell(rw, 2)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Enter your annotation")
        self._AnnotateTable.setItem(rw, 2, item)
        self._AnnotateTable.editItem(self._AnnotateTable.item(rw, 2))

    def _fcn_annotateRm(self):
        """Remove a line to the annotation table."""
        self._AnnotateTable.removeRow(self._AnnotateTable.currentRow())

    def _fcn_annotateGoto(self):
        """Go to the annotation location."""
        row = self._AnnotateTable.currentRow()
        if row >= 0:
            sta = float(str(self._AnnotateTable.item(row, 0).text()))
            self._SlGoto.setValue(sta)
