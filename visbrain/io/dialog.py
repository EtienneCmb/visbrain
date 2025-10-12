"""Dialog window for saving and loading files.

* dialog_save : Open a window to save a file
* dialog_load : Open a window to load a file
"""
import os

from visbrain.gui.threading import invoke_in_gui_thread
from visbrain.qt import QtWidgets
from .rw_utils import safety_save

__all__ = ['dialog_save', 'dialog_load', 'dialog_color']


def _invoke_dialog(function, *args, **kwargs):
    """Execute ``function`` on the GUI thread when a Qt app is running."""

    if QtWidgets is None:
        return function(*args, **kwargs)

    qapp_cls = getattr(QtWidgets, "QApplication", None)
    instance = getattr(qapp_cls, "instance", None)
    app = instance() if callable(instance) else None
    if app is None:
        return function(*args, **kwargs)

    return invoke_in_gui_thread(function, *args, **kwargs)


def dialog_save(self, name='Save file', default='file',
                allext=['All files (*.*)']):
    """Open a window to save a file.

    Parameters
    ----------
    self : class
        Class containing Qt elements.
    name : string | 'Save file'
        Name of the saving window.
    default : string | 'file'
        Default name of the saved file.
    allext : list | ['All files (*.*)']
        String containing all the extensions. Must be a list where each
        element is a string of type 'Ext (.ext)'

    Returns
    -------
    filename : string
        Filename for saving.
    """
    # Build all extensions :
    if isinstance(allext, (list, tuple)):
        allext = ';;'.join(allext)

    parent = None
    if QtWidgets is not None:
        widget_cls = getattr(QtWidgets, 'QWidget', None)
        if widget_cls is not None and isinstance(self, widget_cls):
            parent = self

    # Open the window :
    file, ext = _invoke_dialog(
        QtWidgets.QFileDialog.getSaveFileName,
        parent,
        name,
        default,
        allext,
    )
    # By default, use the extension in the ruler :
    file = os.path.splitext(str(file))[0]
    ext = os.path.splitext(str(ext))[1][0:-1].lower()
    return safety_save(file + ext)


def dialog_load(self, name='Open file', default='file',
                allext=['All files (*.*)']):
    """Open a window to load a file.

    Parameters
    ----------
    self : class
        Class containing Qt elements.
    name : string | 'Save file'
        Name of the opening window.
    default : string | 'file'
        Default name of the opened file.
    allext : list | ['All files (*.*)']
        String containing all the extensions. Must be a list where each
        element is a string of type 'Ext (.ext)'

    Returns
    -------
    filename : string
        Filename for opening.
    """
    parent = None
    if QtWidgets is not None:
        widget_cls = getattr(QtWidgets, 'QWidget', None)
        if widget_cls is not None and isinstance(self, widget_cls):
            parent = self

    # Open the window :
    file, _ = _invoke_dialog(
        QtWidgets.QFileDialog.getOpenFileName,
        parent,
        name,
        default,
        allext,
    )
    return str(file)


def dialog_color():
    """Open a QColorDialog window."""
    return _invoke_dialog(QtWidgets.QColorDialog.getColor).name()
