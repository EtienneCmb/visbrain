"""Main class for settings managment."""

import os
from PyQt4.QtGui import *
from vispy import io


__all__ = ['uiSignal']


class uiSignal(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # MENU & FILES
        # =====================================================================
        self._SigFilt.clicked.connect(self._fcn_filtViz)

    # =====================================================================
    # MENU & FILE MANAGMENT
    # =====================================================================
    def _fcn_filtViz(self):
        """Toggle visibility of the filtering panel."""
        viz = self._SigFilt.isChecked()
        self._SigFiltW.setEnabled(viz)

