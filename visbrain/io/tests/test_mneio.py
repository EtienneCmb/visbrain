"""Test functions in mneio.py."""
import os

from visbrain.io.mneio import mne_switch
from visbrain.io import download_file, path_to_visbrain_data


class TestMneIO(object):
    """Test functions in MNE/IO."""

    def test_mne_switch(self):
        """Test function mne_switch."""
        # Download sleep file :
        sleep_file = path_to_visbrain_data('excerpt2.edf', 'example_data')
        file, ext = os.path.splitext(sleep_file)
        if not os.path.isfile(sleep_file):
            download_file('sleep_edf.zip', unzip=True, astype='example_data')
        to_exclude = ['VAB', 'NAF2P-A1', 'PCPAP', 'POS', 'FP2-A1', 'O2-A1',
                      'CZ2-A1', 'event_pneumo', 'event_pneumo_aut']
        kwargs = dict(exclude=to_exclude, stim_channel=False)
        mne_switch(file, ext, 100., preload=True, **kwargs)
