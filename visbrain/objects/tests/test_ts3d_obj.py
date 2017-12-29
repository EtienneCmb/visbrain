"""Test TimeSeries3DObj."""
import numpy as np

from visbrain.objects.ts3d_obj import TimeSeries3DObj, CombineTimeSeries
from visbrain.objects.tests._testing_objects import _TestObjects

n_sources = 20
ts_data = 100 * np.random.rand(n_sources, 100)
ts_xyz = np.random.uniform(-20, 20, (n_sources, 3))
ts_select = np.random.randint(0, n_sources, (int(n_sources / 2),))

ts_obj = TimeSeries3DObj('TS1', ts_data, ts_xyz, select=ts_select, )


class TestTimeSeriesObj(_TestObjects):
    """Test time-series."""

    OBJ = ts_obj

    def test_definition(self):
        """Test function definition."""
        TimeSeries3DObj('TS1', ts_data, ts_xyz)

    def test_builtin_methods(self):
        """Test function builtin_methods."""
        assert len(ts_obj) == n_sources

    def test_attributes(self):
        """Test function attributes."""
        self.assert_and_test('width', 4.)
        self.assert_and_test('amplitude', 4.)
        color = np.array([0.] * 4)
        self.assert_and_test('color', color)
        self.assert_and_test('alpha', .7)
        self.assert_and_test('translate', (1., 2., 3.))
        self.assert_and_test('line_width', 1.4)


class TestCombineTimeSeries(object):
    """Test combine time-series."""

    def test_definition(self):
        """Test function definition."""
        CombineTimeSeries(ts_obj)
        CombineTimeSeries([ts_obj, ts_obj])
