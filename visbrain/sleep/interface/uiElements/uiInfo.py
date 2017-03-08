"""Main class for info managment."""

from PyQt4 import QtGui
import csv
import os

from ....utils import sleepstats

__all__ = ['uiInfo']


class uiInfo(object):
    """Main class for info managment."""

    def __init__(self):
        """Init."""
        # Time window changed :
        self._infoTime.valueChanged.connect(self._fcn_infoUpdate)
        self._infoTime.setKeyboardTracking(False)
        # Export file :
        self._infoExport.clicked.connect(self._fcn_exportFile)

    def _fcn_infoUpdate(self):
        """Complete the table sleep info."""
        # Get sleep info :
        win = self._infoTime.value()
        stats = sleepstats(self._file, self._hyp.mesh.pos[:, 1], self._sf, win)
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

    def _fcn_exportFile(self):
        """Export stat info."""
        # Get file name :
        path = QtGui.QFileDialog.getSaveFileName(
            self, "Save File", "",
            filter="CSV Files (*.csv);;Text Files (*.txt)")
        # Find extension :
        selected_ext = self._infoExportAs.currentText()
        file = os.path.splitext(path)[0]
        if selected_ext.find('csv') + 1:
            self.listToCsv(file + '.csv', zip(self._keysInfo, self._valInfo))
        elif selected_ext.find('txt') + 1:
            self.listToTxt(file + '.txt', zip(self._keysInfo, self._valInfo))

    def listToCsv(self, file, data):
        """Write a csv file.

        Args:
            file: string
                File name for saving file.

            data: list
                List of data to save to the csv file.
        """
        with open(file, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel',
                                quoting=csv.QUOTE_NONNUMERIC)
            for k in data:
                writer.writerow(k)
        return

    def listToTxt(self, file, data):
        """Write a txt file.

        Args:
            file: string
                File name for saving file.

            data: list
                List of data to save to the txt file.
        """
        # Open file :
        ofile = open(file, 'w')
        for k in data:
            ofile.write("%s\n" % ', '.join(k))
        return
