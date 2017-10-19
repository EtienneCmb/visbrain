"""Test if needed files are successfully installed with visbrain."""
import os

from visbrain.utils import get_data_path


def _test_file(name, path):
    assert os.path.isfile(path)


def test_brain_templates():
    """Test if templates are installed."""
    name = "Brain template ({})"
    for k in ['B1.npz', 'B2.npz', 'B3.npz']:
        _test_file(name.format(k), get_data_path(folder='templates', file=k))


def test_roi_templates():
    """Test if templates are installed."""
    name = "ROI template ({})"
    for k in ['brodmann.npz', 'aal.npz', 'talairach.npz']:
        _test_file(name.format(k), get_data_path(folder='roi', file=k))


def test_icons():
    """Test if Sleep icon is installed."""
    name = "Icons ({})"
    icons = ['brain_icon.svg', 'sleep_icon.svg', 'topo_icon.svg',
             'figure_icon.svg', 'colorbar_icon.svg']
    for k in icons:
        _test_file(name.format(k), get_data_path(folder='icons', file=k))


def test_topo_file():
    """Test if the topo reference file is installed."""
    path = get_data_path(folder='topo', file='eegref.npz')
    _test_file('Topo reference file (eegref.npz)', path)


def test_data_url():
    """Test if the data_url.txt is installed."""
    path = get_data_path(file='data_url.txt')
    _test_file('URL to data (data_url.txt)', path)
