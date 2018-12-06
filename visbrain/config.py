"""Visbrain configurations."""
import sys
import getopt
import logging

from PyQt5 import QtWidgets
from vispy import app as visapp

from .utils import Profiler, set_log_level

# Set 'info' as the default logging level
logger = logging.getLogger('visbrain')
set_log_level('info')

# Configuration dict
CONFIG = {}

# Visbrain profiler (derived from the VisPy profiler)
PROFILER = Profiler()

# PyQt application
PYQT_APP = QtWidgets.QApplication.instance()
if PYQT_APP is None:
    PYQT_APP = QtWidgets.QApplication([''])
CONFIG['PYQT_APP'] = PYQT_APP
CONFIG['SHOW_PYQT_APP'] = True

# VisPy application
CONFIG['VISPY_APP'] = visapp.application.Application()


def use_app(backend_name):
    """Use a specific backend."""
    CONFIG['VISPY_APP'] = visapp.application.Application(backend_name)


# MPL render :
CONFIG['MPL_RENDER'] = False

# Input command line arguments
VISBRAIN_HELP = """
Visbrain command line arguments:

  --visbrain-log=(profiler|debug|info|warning|error|critical)
    Sets the verbosity of logging output. The default is 'info'.

  --visbrain-search=[search string]
    Search string in logs.

  --visbrain-show=(True|False)
    Control if GUI have to be displayed.

  --visbrain-help
    Display help Visbrain command line help.

"""


def init_config(argv):
    """Initialize visbrain configuration."""
    global CONFIG

    argnames = ['visbrain-log=', 'visbrain-show=', 'visbrain-help',
                'visbrain-search=']
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
            if o == '--visbrain-search':
                set_log_level(match=a)

init_config(sys.argv[1:])  # noqa
