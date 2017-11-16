"""Visbrain configurations."""
import sys
import getopt
import logging

from PyQt5 import QtWidgets
from vispy import app as visapp

from .utils import Profiler, set_log_level

logger = logging.getLogger('visbrain')

"""Configuration dict
"""
CONFIG = {}

"""Visbrain profiler (derived from the VisPy profiler)
"""
PROFILER = Profiler()

"""PyQt application
"""
PYQT_APP = QtWidgets.QApplication.instance()
if PYQT_APP is None:
    PYQT_APP = QtWidgets.QApplication([''])
CONFIG['SHOW_PYQT_APP'] = True

"""VisPy application
"""
VISPY_APP = visapp.application.Application()

"""Input command line arguments
"""
VISBRAIN_HELP = """
Visbrain command line arguments:

  --visbrain-log=(debug|info|warning|error|critical)
    Sets the verbosity of logging output. The default is 'info'.

  --visbrain-show=(True|False)
    Control if GUI have to be displayed.

  --visbrain-help
    Display help Visbrain command line help.

"""


def init_config(argv):
    """Initialize visbrain configuration."""
    global CONFIG

    argnames = ['visbrain-log=', 'visbrain-show=', 'visbrain-help']
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', argnames)
    except getopt.GetoptError:
        opts = []

    for o, a in opts:
        if o.startswith('--visbrain'):
            if o == '--visbrain-help':
                print(VISBRAIN_HELP)
            if o == '--visbrain-log':
                set_log_level(a)
            if o == '--visbrain-show':
                CONFIG['SHOW_PYQT_APP'] = eval(a)
                logger.debug("Show PyQt app : %r" % CONFIG['SHOW_PYQT_APP'])

init_config(sys.argv[1:])  # noqa
