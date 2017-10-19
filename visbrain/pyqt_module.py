"""All visbrain modules based on PyQt5 should inherit from PyQtModule."""
import sys
import os
import sip
from PyQt5 import QtWidgets, QtGui
import logging

import vispy.app as visapp

from .utils import set_widget_size, set_log_level, get_data_path

sip.setdestroyonexit(False)
logger = logging.getLogger('visbrain')


class PyQtModule(object):
    """Shared methods across PyQt based Visbrain modules.

    Parameters
    ----------
    verbose : logging.level | None
        Verbosity level.
    to_describe : string | None
        The parent node to describe. Only available if verbose level is on
        debug.
    icon : str | None
        Name of the icon to use.
    """

    def __init__(self, verbose=None, to_describe=None, icon=None):
        """Init."""
        self._app = QtWidgets.QApplication(sys.argv)
        self._need_description = to_describe
        if isinstance(self._need_description, str):
            self._need_description = [self._need_description]
        self._module_icon = icon
        set_log_level(verbose)

    def show(self):
        """Display the graphical user interface."""
        # Fixed size for the settings panel :
        if hasattr(self, 'q_widget'):
            set_widget_size(self._app, self.q_widget, 23)
            self.q_widget.setVisible(True)
        # Force the quick settings tab to be on the first tab :
        if hasattr(self, 'QuickSettings'):
            self.QuickSettings.setCurrentIndex(0)
        # Set icon (if possible) :
        if isinstance(self._module_icon, str):
            path_ico = get_data_path(folder='icons', file=self._module_icon)
            if os.path.isfile(path_ico):
                app_icon = QtGui.QIcon()
                app_icon.addFile(path_ico)
                self.setWindowIcon(app_icon)
            else:  # don't crash just for an icon...
                logger.debug("No icon found (%s)" % self._module_icon)
        # Tree description if log level is on debug :
        if isinstance(self._need_description, list) and (logger.level == 10):
            print('\n' + '=' * 60)
            for k in self._need_description:
                print(eval('self.%s.describe_tree()' % k))
            print('=' * 60 + '\n')
        # Show and maximized the window :
        self.showMaximized()
        visapp.run()

    def closeEvent(self, event):
        """Executed method when the GUI closed."""
        QtWidgets.qApp.quit()
        logger.debug("App closed.")
