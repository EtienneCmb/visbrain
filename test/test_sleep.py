from visbrain import Sleep
import os
from distutils.sysconfig import get_python_lib


def test_instance_sleep():
    """Test the creation of a Sleep instance."""
    pass
    # s = Sleep()


def test_topo_file():
    """Test if the topo reference file is installed."""
    vbpath = get_python_lib() + '/visbrain/utils/topo/'
    assert os.path.isfile(os.path.join(vbpath, 'eegref.npz'))


def test_ico_file():
    """Test if Sleep icon is installed."""
    vbpath = get_python_lib() + '/visbrain/sleep/ico/'
    assert os.path.isfile(os.path.join(vbpath, 'sleep.svg'))
