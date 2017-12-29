"""Test functions in physio.py."""
import numpy as np

from visbrain.utils.physio import (find_non_eeg, rereferencing, bipolarization,
                                   commonaverage, tal2mni, mni2tal,
                                   generate_eeg)


class TestPhysio(object):
    """Test functions in physio.py."""

    @staticmethod
    def _generate_eeg_dataset(data_type='eeg'):
        """Generate an EEG dataset to test re-referencing functions."""
        data = np.random.rand(4, 100)
        if data_type == 'eeg':
            data = np.random.rand(4, 100)
            channels = ['Cz', 'Pz', 'Fz', 'EOG']
        elif data_type == 'intra':
            channels = ['m1.132', 'm2.134', 'm3.45', 'i1.32']
        return data, channels, [False, False, False, True]

    @staticmethod
    def _generate_coordinates():
        """Generate random xyz coordinates."""
        return np.random.rand(50, 3)

    def test_find_non_eeg(self):
        """Test function find_non_eeg."""
        bool_vec = find_non_eeg(['cz', 'eog', 'emg'])
        assert np.array_equal(bool_vec, (False, True, True))

    def test_rereferencing(self):
        """Test function rereferencing."""
        data, channels, ignore = self._generate_eeg_dataset('eeg')
        data_r, chan_r, consider = rereferencing(data, channels, 1, ignore)
        assert chan_r == ['Cz-Pz', 'Pz', 'Fz-Pz', 'EOG']

    def test_bipolarization(self):
        """Test function bipolarization."""
        data, channels, ignore = self._generate_eeg_dataset('intra')
        data_r, chan_r, consider = bipolarization(data, channels, ignore)
        assert chan_r == ['m1', 'm2-m1', 'm3-m2', 'i1']

    def test_commonaverage(self):
        """Test function commonaverage."""
        data, channels, ignore = self._generate_eeg_dataset('eeg')
        data_r, chan_r, consider = commonaverage(data, channels, ignore)
        assert chan_r == ['Cz-m', 'Pz-m', 'Fz-m', 'EOG']

    def test_tal2mni(self):
        """Test function tal2mni."""
        xyz = self._generate_coordinates()
        tal2mni(xyz)

    def test_mni2tal(self):
        """Test function mni2tal."""
        xyz = self._generate_coordinates()
        mni2tal(xyz)

    def test_generate_eeg(self):
        """Test function generate_eeg."""
        generate_eeg(n_pts=1000)
