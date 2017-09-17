"""Main class for info managment."""

from PyQt5 import QtWidgets

from ....utils import sleepstats
from os import path

__all__ = ['uiInfo']


class uiInfo(object):
    """Main class for info managment."""

    def __init__(self):
        """Init."""
        # Time window changed :
        self._infoTime.valueChanged.connect(self._fcn_infoUpdate)
        self._infoTime.setKeyboardTracking(False)

    def _fcn_infoUpdate(self):
        """Complete the table sleep info."""
        # Get sleep stats :
        stats = sleepstats(self._hyp.gui_to_hyp(), self._sf)

        # Add global informations to stats dict
        stats['Filename'] = path.basename(self._file) if self._file is not None else ''
        stats['Sampling frequency'] = str(self._sfori) + " Hz"
        stats['Down-sampling'] = str(self._sf) + " Hz"

        self._keysInfo = [''] * len(stats)
        self._valInfo = [''] * len(stats)
        # Check line number:
        self._infoTable.setRowCount(len(stats))
        # Fill table :
        for num, (k, v) in enumerate(stats.items()):
            # Add keys :
            self._infoTable.setItem(int(num), 0, QtWidgets.QTableWidgetItem(k))
            # Add values :
            self._infoTable.setItem(int(num), 1, QtWidgets.QTableWidgetItem(str(v)))
            # Remember variables :
            self._keysInfo[int(num)] = k
            self._valInfo[int(num)] = str(v)
