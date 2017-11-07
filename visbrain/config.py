from PyQt5 import QtWidgets
from vispy import app as visapp

from .utils import Profiler

"""Visbrain profiler (derived from the VisPy profiler)
"""
profiler = Profiler()

"""PyQt application
"""
app = QtWidgets.QApplication.instance()
if app is None:
    app = QtWidgets.QApplication([''])

vispy_app = visapp.application.Application()
