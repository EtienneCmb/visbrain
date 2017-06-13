from __future__ import print_function
from visbrain import Sleep
import os
from distutils.sysconfig import get_python_lib


def test_instance_sleep():
    """Test the creation of a Sleep instance."""
    pass
    # s = Sleep()


def test_topo_file():
    """Test if the topo reference file is installed."""
    vbpath = os.path.join(get_python_lib(), '/visbrain/utils/topo/')
    file = os.path.join(vbpath, 'eegref.npz')
    print(file)
    assert os.path.isfile(file)


def test_ico_file():
    """Test if Sleep icon is installed."""
    vbpath = os.path.join(get_python_lib(), '/visbrain/sleep/ico/')
    file = os.path.join(vbpath, 'sleep.svg')
    print(file)
    assert os.path.isfile(file)
