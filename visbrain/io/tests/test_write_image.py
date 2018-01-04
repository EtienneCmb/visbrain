"""Test functions in write_image."""
import numpy as np
import pytest

from visbrain.io import (write_fig_hyp, write_fig_spindles, write_fig_canvas,
                         write_fig_pyqt)


class TestWriteImage(object):
    """Test functions in write_image.py."""

    def test_write_fig_hyp(self):
        """Test function write_fig_hyp."""
        pass

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
