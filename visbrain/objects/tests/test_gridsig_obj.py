"""Test GridSignalsObj."""
import numpy as np
from itertools import product

from vispy import scene

import mne

from visbrain.objects.gridsig_obj import GridSignalsObj
from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.utils.cameras import ScrollCamera


data = np.random.rand(4, 5, 10)
g_obj = GridSignalsObj('grid', data)


class TestGridSignalsObj(_TestObjects):
    """Test the grid of signals object."""

    OBJ = g_obj

    @staticmethod
    def _get_data(data_as='np', nd=1):
        assert data_as in ['np', 'raw', 'epoch']
        if (data_as == 'np') and (nd == 1):
            return np.random.rand(100)
        elif (data_as == 'np') and (nd == 2):
            return np.random.rand(2, 50)
        elif (data_as == 'np') and (nd == 3):
            return np.random.rand(2, 5, 10)
        elif data_as in ['raw', 'epoch']:
            n_c = 5
            _data = np.random.rand(n_c, 100)
            channels = ['chan %i' % i for i in range(n_c)]
            info = mne.create_info(channels, 128.)
            raw = mne.io.RawArray(_data, info)
            if data_as == 'raw':
                return raw
            elif data_as == 'epoch':
                start = np.linspace(0, 80, 10).astype(int)
                end = np.linspace(10, 90, 10).astype(int)
                events = np.c_[start, end, np.arange(len(start))]
                return mne.Epochs(raw, events)

    def test_nump_definition(self):
        """Test function definition."""
        GridSignalsObj('1d', self._get_data(nd=1))
        GridSignalsObj('2d', self._get_data(nd=2))
        GridSignalsObj('3d', self._get_data(nd=3))

    def test_mne_definition(self):
        """Test the compatibility with MNE-Python."""
        GridSignalsObj('raw', self._get_data('raw'))
        GridSignalsObj('epoch', self._get_data('epoch'))

    def test_plt_type(self):
        """Test the plotting types grid, row or col."""
        data_3d = self._get_data(nd=3)
        grid = GridSignalsObj('grid', data_3d, plt_as='grid')
        row = GridSignalsObj('grid', data_3d, plt_as='row')
        col = GridSignalsObj('grid', data_3d, plt_as='col')

        # Test camera
        cam_grid = grid._get_camera()
        assert isinstance(cam_grid, scene.cameras.PanZoomCamera)
        cam_row = row._get_camera()
        assert isinstance(cam_row, ScrollCamera)
        cam_col = col._get_camera()
        assert isinstance(cam_col, ScrollCamera)

    def test_titles(self):
        """Test titles."""
        data_3d = self._get_data(nd=3)
        n_chan, n_trials, _ = data_3d.shape
        chan = ['chan %i' % i for i in range(n_chan)]
        trials = ['trial %i' % i for i in range(n_trials)]
        titles = ['%s - %s' % (k, i) for k, i in product(chan, trials)]
        GridSignalsObj('titles', data_3d, title=titles, title_size=3.,
                       title_bold=False, color='blue', title_visible=False,
                       n_signals=2, plt_as='col', lw=7.)
