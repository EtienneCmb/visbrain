"""Enable to annotate a Sleep file."""

from PyQt5 import QtWidgets
import numpy as np


class UiAnnotate(object):
    """Interactions with annotations."""

    def __init__(self):
        """Init."""
        # Add/remove line :
        self._AnnotateAdd.clicked.connect(self._fcn_annotate_add)
        self._AnnotateRm.clicked.connect(self._fcn_annotate_rm)
        self._AnnotateTable.itemSelectionChanged.connect(
            self._fcn_annotate_goto)

    def _fcn_annotate_add(self, _, xlim=None, txt="Enter your annotation"):
        """Add a ligne to the annotation table."""
        # Add a ligne :
        self._AnnotateTable.setRowCount(self._AnnotateTable.rowCount() + 1)
        rw = self._AnnotateTable.rowCount() - 1
        if xlim is None:
            # Get the current window :
            val = self._SlVal.value()
            step = self._SigSlStep.value()
            win = self._SigWin.value()
            xlim = (val * step, val * step + win)
        # Automatically set the window :
        self._AnnotateTable.setItem(rw, 0, QtWidgets.QTableWidgetItem(
            str(xlim[0])))
        self._AnnotateTable.setItem(rw, 1, QtWidgets.QTableWidgetItem(
            str(xlim[1])))
        # Select the text item :
        self._AnnotateTable.setCurrentCell(rw, 2)
        item = QtWidgets.QTableWidgetItem()
        item.setText(txt)
        self._AnnotateTable.setItem(rw, 2, item)
        self._AnnotateTable.editItem(self._AnnotateTable.item(rw, 2))
        # Send marker annotation to the time-axis :
        self._annot_mark = np.append(self._annot_mark, np.array(xlim).mean())
        self._fcn_slider_move()

    def _fcn_annotate_rm(self):
        """Remove a line to the annotation table."""
        row = self._AnnotateTable.currentRow()
        self._AnnotateTable.removeRow(row)
        self._annot_mark = np.delete(self._annot_mark, row, 0)
        self._fcn_slider_move()

    def _fcn_annotate_goto(self):
        """Go to the annotation location."""
        row = self._AnnotateTable.currentRow()
        if row >= 0:
            sta = float(str(self._AnnotateTable.item(row, 0).text()))
            self._SlGoto.setValue(sta)
