"""Main class for info managment."""

from PyQt5 import QtWidgets

from ....utils import sleepstats
from os import path


class UiInfo(object):
    """Main class for info managment."""

    def __init__(self):
        """Init."""
        pass

    def _fcn_info_update(self):
        """Complete the table sleep info."""
        table = self._infoTable
        # Get sleep stats :
        stats = sleepstats(self._hyp.gui_to_hyp(), self._sf)

        # Add global informations to stats dict
        is_file = isinstance(self._file, str)
        stats['Filename'] = path.basename(self._file) if is_file else ''
        stats['Sampling frequency'] = str(self._sfori) + " Hz"
        stats['Down-sampling'] = str(self._sf) + " Hz"

        self._keysInfo = [''] * len(stats)
        self._valInfo = [''] * len(stats)
        # Check line number:
        table.setRowCount(len(stats))
        # Fill table :
        for num, (k, v) in enumerate(stats.items()):
            # Add keys :
            table.setItem(int(num), 0, QtWidgets.QTableWidgetItem(k))
            # Add values :
            table.setItem(int(num), 1, QtWidgets.QTableWidgetItem(str(v)))
            # Remember variables :
            self._keysInfo[int(num)] = k
            self._valInfo[int(num)] = str(v)
