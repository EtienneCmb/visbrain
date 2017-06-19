"""Main class for info managment."""

from PyQt5 import QtWidgets

from ....utils import sleepstats

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
        # Get sleep info :
        win = self._infoTime.value()
        stats = sleepstats(self._file, self._hyp.GUI2hyp(), self._N,
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
            self._infoTable.setItem(int(r), 0, QtWidgets.QTableWidgetItem(key))
            # Add values :
            self._infoTable.setItem(int(r), 1, QtWidgets.QTableWidgetItem(str(v)))
            # Remember variables :
            self._keysInfo[int(r) + 1] = key
            self._valInfo[int(r) + 1] = str(v)
