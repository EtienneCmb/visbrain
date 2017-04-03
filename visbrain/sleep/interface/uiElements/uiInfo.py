"""Main class for info managment."""

from PyQt4 import QtGui
import os

from ....utils import sleepstats, listToCsv, listToTxt

__all__ = ['uiInfo']


class uiInfo(object):
    """Main class for info managment."""

    def __init__(self):
        """Init."""
        # Time window changed :
        self._infoTime.valueChanged.connect(self._fcn_infoUpdate)
        self._infoTime.setKeyboardTracking(False)
        # Export file :
        self._infoExport.clicked.connect(self._fcn_exportInfos)

    def _fcn_infoUpdate(self):
        """Complete the table sleep info."""
        # Get sleep info :
        win = self._infoTime.value()
        stats = sleepstats(self._file, -self._hyp.mesh.pos[:, 1], self._N,
                           sf=self._sf, sfori=self._sfori,
                           time_window=win)
        self._keysInfo = ['Window'] + [''] * len(stats)
        self._valInfo = [str(win)] + [''] * len(stats)
        # Check line number:
        self._infoTable.setRowCount(len(stats))
        # Fill table :
        for num, (k, v) in enumerate(stats.items()):
            # Get keys and row :
            key, r = k.split('_')
            # Add keys :
            self._infoTable.setItem(int(r), 0, QtGui.QTableWidgetItem(key))
            # Add values :
            self._infoTable.setItem(int(r), 1, QtGui.QTableWidgetItem(str(v)))
            # Remember variables :
            self._keysInfo[int(r) + 1] = key
            self._valInfo[int(r) + 1] = str(v)

    def _fcn_exportInfos(self):
        """Export stat info."""
        # Find extension :
        selected_ext = str(self._infoExportAs.currentText())
        # Get file name :
        path = QtGui.QFileDialog.getSaveFileName(
            self, "Save File", "statsinfo",
            filter=selected_ext)
        if path:
            file = os.path.splitext(str(path))[0]
            if selected_ext.find('csv') + 1:
                listToCsv(file + '.csv', zip(self._keysInfo, self._valInfo))
            elif selected_ext.find('txt') + 1:
                listToTxt(file + '.txt', zip(self._keysInfo, self._valInfo))
