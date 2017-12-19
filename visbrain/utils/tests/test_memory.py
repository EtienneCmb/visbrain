"""Test functions in memory.py."""
import numpy as np
from visbrain.utils.memory import arrays_share_data, id, code_timer


class TestMemory(object):
    """Test functions in memory.py."""

    def test_id(self):
        """Test function id."""
        a = b = np.arange(10)
        assert id(b) == id(a)

    def test_arrays_share_data(self):
        """Test function arrays_share_data."""
        a = b = np.arange(10)
        assert arrays_share_data(a, b)

    def test_code_timer(self):
        """Test function code_timer."""
        start = code_timer(verbose=False)
        code_timer(start, unit='ms')
        code_timer(start, unit='us')
