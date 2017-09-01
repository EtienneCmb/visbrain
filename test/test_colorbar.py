"""Test Colorbar module and related methods."""
import os
import shutil
from warnings import warn

from PyQt5 import QtWidgets

from visbrain import Colorbar


# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))

# ---------------- Variables  ----------------
kw = {}
kw['cmap'] = 'Spectral_r'
kw['clim'] = (-10., 10.)
kw['vmin'] = -1.2
kw['under'] = (.1, .1, .1)
kw['vmax'] = 7.52
kw['over'] = 'darkred'
kw['cblabel'] = 'Test Colorbar module'
kw['cbtxtsz'] = 2.
kw['cbtxtsh'] = 1.2
kw['txtcolor'] = 'orange'
kw['txtsz'] = 4.
kw['txtsh'] = 0.5
kw['border'] = False
kw['limtxt'] = True
kw['bgcolor'] = '#ab4642'
kw['ndigits'] = 4

# ---------------- Application  ----------------
app = QtWidgets.QApplication([])
cb = Colorbar(**kw)


class TestColorbar(object):
    """Test brain.py."""

    ###########################################################################
    #                                 SETTINGS
    ###########################################################################
    def test_create_tmp_folder(self):
        """Create tmp folder."""
        if not os.path.exists(path_to_tmp):
            os.makedirs(path_to_tmp)

    @staticmethod
    def _path_to_tmp(name):
        return os.path.join(*(path_to_tmp, name))

    ###########################################################################
    #                                 GUI
    ###########################################################################
    def test_save_config(self):
        """Test function save_config."""
        cb._fcn_saveCbarConfig(filename=self._path_to_tmp('cb_config.txt'))

    def test_load_config(self):
        """Test function load_config."""
        cb._fcn_loadCbarConfig(filename=self._path_to_tmp('cb_config.txt'))

    def test_screenshot(self):
        """Test function screenshot."""
        warn("gui_screenshot not tested in Colorbar()")

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)
