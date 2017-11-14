"""Visbrain configurations."""
import logging

from PyQt5 import QtWidgets
from vispy import app as visapp

from .utils import Profiler

logger = logging.getLogger('visbrain')

"""Visbrain profiler (derived from the VisPy profiler)
"""
PROFILER = Profiler()

"""PyQt application
"""
PYQT_APP = QtWidgets.QApplication.instance()
if PYQT_APP is None:
    PYQT_APP = QtWidgets.QApplication([''])

VISPY_APP = visapp.application.Application()
