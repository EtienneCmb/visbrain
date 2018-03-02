"""Test functions in write_image."""
import numpy as np
import pytest

from visbrain.utils import generate_eeg
from visbrain.io import (write_fig_hyp, write_fig_spindles,  # noqa
                         write_fig_canvas, write_fig_pyqt)
from visbrain.tests._tests_visbrain import _TestVisbrain


class TestWriteImage(_TestVisbrain):
    """Test functions in write_image.py."""

    @pytest.mark.xfail(reason="Failed if display not correctly configured",
                       run=True, strict=False)
    def test_write_fig_hyp(self):
        """Test function write_fig_hyp."""
        hypno = np.repeat(np.arange(6), 100) - 1.
        sf = 1.
        file = self.to_tmp_dir('hypno_write_fig_hyp.png')
        file_color = self.to_tmp_dir('hypno_write_fig_hyp_color.png')
        write_fig_hyp(hypno, sf, file=file)
        write_fig_hyp(hypno, sf, file=file_color, ascolor=True)

    @pytest.mark.xfail(reason="Failed if display not correctly configured",
                       run=True, strict=False)
    def test_write_fig_spindles(self):
        """Test function write_fig_spindles."""
        sf, n_pts = 100., 10014
        hypno = np.repeat(np.arange(6), 1669) - 1.
        sig = np.squeeze(generate_eeg(sf=sf, n_pts=n_pts, random_state=1)[0])
        file = self.to_tmp_dir('write_fig_spindles.png')
        file_hyp = self.to_tmp_dir('write_fig_spindles_hypno.png')
        write_fig_spindles(sig, sf, file=file, thr=.1)
        write_fig_spindles(sig, sf, hypno=hypno, file=file_hyp, thr=.1)

    @pytest.mark.skip('Should be tested inside modules or objects.')
    def test_write_fig_canvas(self):
        """Test function write_fig_canvas."""
        pass

    @pytest.mark.skip('Should be tested inside modules.')
    def test_write_fig_pyqt(self):
        """Test function write_fig_pyqt."""
        pass
