"""Test functions in events.py."""
import numpy as np

from visbrain.utils.sleep.event import (_events_distance_fill,
                                        _events_to_index, _index_to_events)


class TestEvent(object):
    """Test functions in event.py."""

    @staticmethod
    def _get_index():
        return np.array([0, 1, 2, 3, 4, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19])

    @staticmethod
    def _get_data():
        data = np.random.rand(1000)
        idx_sup_thr = np.arange(1000)
        idx_start = np.array([10, 40, 100])
        idx_stop = np.array([50, 75, 200])
        return data, idx_sup_thr, idx_start, idx_stop

    def test_events_distance_fill(self):
        """Test function events_distance_fill."""
        _events_distance_fill(self._get_index(), 200., 100.)

    def test_event_to_index(self):
        """Test function event_to_index."""
        _events_to_index(self._get_index())

    def test_index_to_event(self):
        """Test function index_to_event."""
        idx = _events_to_index(self._get_index())
        _index_to_events(idx)
