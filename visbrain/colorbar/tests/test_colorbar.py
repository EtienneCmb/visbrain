"""Test Colorbar module and related methods."""
import pytest

from visbrain import Colorbar
from visbrain.tests._tests_visbrain import _TestVisbrain


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
cb = Colorbar(**kw)


class TestColorbar(_TestVisbrain):
    """Test brain.py."""

    ###########################################################################
    #                                 GUI
    ###########################################################################
    @pytest.mark.skip('Not configured')
    def test_save_config(self):
        """Test function save_config."""
        cb._fcn_saveCbarConfig(filename=self.to_tmp_dir('cb_config.txt'))

    @pytest.mark.skip('Not configured')
    def test_load_config(self):
        """Test function load_config."""
        cb._fcn_loadCbarConfig(filename=self.to_tmp_dir('cb_config.txt'))

    @pytest.mark.skip('Not configured')
    def test_screenshot(self):
        """Test function screenshot."""
        pass
