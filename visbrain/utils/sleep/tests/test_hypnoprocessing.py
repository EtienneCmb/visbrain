"""Test functions in hypnoprocessing.py."""
import numpy as np

from visbrain.utils.sleep.hypnoprocessing import (transient, sleepstats)


class TestHypnoprocessing(object):
    """Test functions in hypnoprocessing.py."""

    def test_transient(self):
        """Test function transient."""
        data = np.array([0, 0, 0, 1, 1, 2, 2, 2, 3, 4, 4, 5])
        time = np.arange(len(data)) / 2.
        index = np.array([[0, 2], [3, 4], [5, 7], [8, 8], [9, 10], [11, 11]])
        tr, idx, stages = transient(data)
        assert np.array_equal(tr, [2, 4, 7, 8, 10])
        assert np.array_equal(index, idx)
        assert np.array_equal(stages, [0, 1, 2, 3, 4, 5])
        _, idx_time, _ = transient(data, time)
        assert np.array_equal(index / 2., idx_time)

    def test_sleepstats(self):
        """Test function sleepstats."""
        hypno = np.random.randint(-1, 3, (2000,))
        sleepstats(hypno, 100.)
