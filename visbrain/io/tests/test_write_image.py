"""Test functions in write_image."""
import numpy as np
import pytest

from visbrain.io import (write_fig_hyp, write_fig_spindles, write_fig_canvas,
                         write_fig_pyqt)
from visbrain.tests._tests_visbrain import _TestVisbrain


class TestWriteImage(_TestVisbrain):
    """Test functions in write_image.py."""

    def test_write_fig_hyp(self):
        """Test function write_fig_hyp."""
        hypno = np.repeat(np.arange(6), 100) - 1.
        sf = 1.
        file = self.to_tmp_dir('hypno_write_fig_hyp.png')
        file_color = self.to_tmp_dir('hypno_write_fig_hyp_color.png')
        write_fig_hyp(hypno.copy(), sf, file=file)
        write_fig_hyp(hypno.copy(), sf, file=file_color, ascolor=True)

    def test_write_fig_spindles(self):
        """Test function write_fig_spindles."""
        pass

    @pytest.mark.skip('Should be tested inside modules or objects.')
    def test_write_fig_canvas(self):
        """Test function write_fig_canvas."""
        pass

    @pytest.mark.skip('Should be tested inside modules.')
    def test_write_fig_pyqt(self):
        """Test function write_fig_pyqt."""
        pass
