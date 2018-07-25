"""Signal annotations."""
from PyQt5 import QtWidgets
import numpy as np

from visbrain.utils import textline2color
from visbrain.io import dialog_color


class UiAnnotations(object):
    """Annotations interactions."""

    def __init__(self):
        """Init."""
        # Table :
        self._annot_table.itemSelectionChanged.connect(self._fcn_annot_goto)
        self._annot_table.cellChanged.connect(self._fcn_text_edited)
        # Appearance :
        self._annot_txtsz.valueChanged.connect(self._fcn_annot_appear)
        self._annot_marksz.valueChanged.connect(self._fcn_annot_appear)
        self._annot_color.editingFinished.connect(self._fcn_annot_appear)
        self._sig_annot_picker.clicked.connect(self._fcn_color_annot_picker)
        self._annot_viz.clicked.connect(self._fcn_annot_appear)

    def _annotate_event(self, signal, coord, text="Enter annotation"):
        """Annotate event."""
        self.QuickSettings.setCurrentIndex(2)
        self._annot_viz.setChecked(True)
        self._annot_table.setRowCount(self._annot_table.rowCount() + 1)
        rw = self._annot_table.rowCount() - 1
        # Be sure to have latest text appearance properties :
        self._fcn_annot_appear()
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

    def _fcn_annot_appear(self):
        """Control annotations appearance."""
        pos = self._signal._annot_mark._data['a_position']
        self._signal._annot_mark._data = np.array([])
        color = textline2color(self._annot_color.text())[1]
        self._signal._annot_text.font_size = self._annot_txtsz.value()
        self._signal._annot_text.color = color
        self._signal._annot_mark.set_data(pos=pos, face_color=color,
                                          size=self._annot_marksz.value(),
                                          edge_width=0.)
        self._signal._annot_text.update()
        self._signal._annot_text.visible = self._annot_viz.isChecked()
        self._signal._annot_mark.visible = self._annot_viz.isChecked()

    def _fcn_color_annot_picker(self):
        """Pick color for annotation."""
        color = dialog_color()
        self._annot_color.setText(str(color))
        self._fcn_annot_appear()
