"""Dialog window for saving and loading files.

* dialog_save : Open a window to save a file
* dialog_load : Open a window to load a file
"""
from PyQt5.QtWidgets import QFileDialog, QColorDialog
import os

from .rw_utils import safety_save

__all__ = ['dialog_save', 'dialog_load', 'dialog_color']


def dialog_save(self, name='Save file', default='file',
                allext=['All files (*.*)']):
    """Open a window to save a file.

    Parameters
    ----------
    self : class
        Class containing PyQt5 elemnets.
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
    # Open the window :
    file, ext = QFileDialog.getSaveFileName(self, name, default, allext)
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
        Class containing PyQt5 elemnets.
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
    # Open the window :
    file, _ = QFileDialog.getOpenFileName(self, name, default, allext)
    return str(file)


def dialog_color():
    """Open a QColorDialog window."""
    return QColorDialog.getColor().name()
