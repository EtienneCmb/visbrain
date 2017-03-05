"""Main class for info managment."""

from PyQt4 import QtGui

from ....utils import sleepstats

__all__ = ['uiInfo']


class uiInfo(object):
    """Main class for info managment."""

    def __init__(self):
        """Init."""
        # Get sleep info :
        stats = sleepstats(self._hypno, self._sf)
        # Complete table :
        self._infoTable.setRowCount(len(stats))
        for num, (k, v) in enumerate(stats.items()):
            # Get keys and row :
            key, r = k.split('_')
            # Add keys :
            self._infoTable.setItem(int(r), 0, QtGui.QTableWidgetItem(key))
            # Add values :
            self._infoTable.setItem(int(r), 1, QtGui.QTableWidgetItem(str(v)))
