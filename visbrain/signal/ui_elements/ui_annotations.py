"""Signal annotations."""
from PyQt5 import QtWidgets

from ...utils import safely_set_spin

__all__ = ('UiAnnotations')


class UiAnnotations(object):
    """Annotations interactions."""

    def __init__(self):
        """Init."""
        self._annot_table.itemSelectionChanged.connect(self._fcn_annot_goto)
        # Table edited :
        self._annot_table.cellChanged.connect(self._fcn_text_edited)

    def _annotate_event(self, signal, coord, text="Enter your annotation"):
        """Annotate event."""
        self._annot_table.setRowCount(self._annot_table.rowCount() + 1)
        rw = self._annot_table.rowCount() - 1
        # Add annotation :
        self._annot_table.setItem(rw, 0, QtWidgets.QTableWidgetItem(
            str(coord)))
        self._annot_table.setItem(rw, 1, QtWidgets.QTableWidgetItem(
            str(signal)))
        self._annot_table.setItem(rw, 2, QtWidgets.QTableWidgetItem(
            str(text)))
        # Select the text item :
        self._annot_table.setCurrentCell(rw, 2)
        item = QtWidgets.QTableWidgetItem()
        item.setText(text)
        self._annot_table.setItem(rw, 2, item)
        self._annot_table.editItem(self._annot_table.item(rw, 2))

    def _fcn_annot_goto(self):
        """Select the annotation."""
        row = self._annot_table.currentRow()
        if row >= 0:
            # Get coordinates and the signal :
            coord = self._annot_table.item(row, 0).text()
            signal = self._annot_table.item(row, 1).text()
            # Transform string coordinates into a tuple :
            coord = self._signal._coord_to_tuple(coord)
            # Get index of the signal :
            idx_sig = self._signal._get_signal_index(signal)
            # Update plot only if needed :
            if idx_sig != self._signal._index:
                self._safely_set_index(idx_sig - 1, True, True)
            # Finally, select annotations :
            self._signal.select_annotation(signal, coord)

    def _fcn_text_edited(self):
        """Update text label of selected row."""
        row = self._annot_table.currentRow()
        if row >= 0:
            # Get coordinates, signal and annotation text :
            coord = self._annot_table.item(row, 0).text()
            signal = self._annot_table.item(row, 1).text()
            text = self._annot_table.item(row, 2).text()
            self._signal.set_text(signal, coord, text)
