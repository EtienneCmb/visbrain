"""Signal annotations."""
from PyQt5 import QtWidgets

__all__ = ('UiAnnotations')


class UiAnnotations(object):
    """Annotations interactions."""

    def __init__(self):
        """Init."""
        self._annot_table.itemSelectionChanged.connect(self._fcn_annot_goto)
        # Table edited :
        self._annot_table.cellChanged.connect(self._fcn_text_edited)

    def _annotate_event(self, signal, coord, text="Enter annotation"):
        """Annotate event."""
        self.QuickSettings.setCurrentIndex(2)
        self._annot_table.setRowCount(self._annot_table.rowCount() + 1)
        rw = self._annot_table.rowCount() - 1
        # Add annotation :
        self._annot_table.setItem(rw, 0, QtWidgets.QTableWidgetItem(
            str(coord[0])))
        self._annot_table.setItem(rw, 1, QtWidgets.QTableWidgetItem(
            str(coord[1])))
        self._annot_table.setItem(rw, 2, QtWidgets.QTableWidgetItem(
            str(signal)))
        self._annot_table.setItem(rw, 3, QtWidgets.QTableWidgetItem(
            str(text)))
        # Select the text item :
        self._annot_table.setCurrentCell(rw, 3)
        item = QtWidgets.QTableWidgetItem()
        item.setText(text)
        self._annot_table.setItem(rw, 3, item)
        self._annot_table.editItem(self._annot_table.item(rw, 3))
        # Update annotations in visual :
        self._signal.add_annotations(str(self._signal), coord, text=text)
        self._signal.update_annotations(str(self._signal))
        self._signal.select_annotation(str(self._signal), coord)

    def _fcn_annot_goto(self):
        """Select the annotation."""
        row = self._annot_table.currentRow()
        if row >= 0:
            # Get coordinates and the signal :
            t_coord = self._annot_table.item(row, 0).text()
            a_coord = self._annot_table.item(row, 1).text()
            coord = (float(t_coord), float(a_coord))
            signal = self._annot_table.item(row, 2).text()
            # Get index of the signal :
            idx_sig = self._signal._get_signal_index(signal)
            # Update plot only if needed :
            if idx_sig != self._signal._index:
                self._safely_set_index(idx_sig, True, True)
            # Finally, select annotations :
            self._signal.select_annotation(signal, coord)

    def _fcn_text_edited(self):
        """Update text label of selected row."""
        row = self._annot_table.currentRow()
        if row >= 0:
            # Get coordinates, signal and annotation text :
            t_coord = self._annot_table.item(row, 0).text()
            a_coord = self._annot_table.item(row, 1).text()
            coord = '(' + t_coord + ', ' + a_coord + ')'
            signal = self._annot_table.item(row, 2).text()
            text = self._annot_table.item(row, 3).text()
            self._signal.set_text(signal, coord, text)
