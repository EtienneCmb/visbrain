"""Test functions in others.py."""
from visbrain.utils.others import (get_dsf, set_if_not_none)


class TestOthers(object):
    """Test functions in others.py."""

    def test_get_dsf(self):
        """Test function get_dsf."""
        assert get_dsf(100, 1000.) == (10, 100.)
        assert get_dsf(100, None) == (1, 100.)

    def test_set_if_not_none(self):
        """Test function set_if_not_none."""
        a = 5.
        assert set_if_not_none(a, None) == 5.
        assert set_if_not_none(a, 10., False) == 5.
        assert set_if_not_none(a, 10.) == 10.
