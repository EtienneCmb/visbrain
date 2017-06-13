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
    vbpath = get_python_lib()
    topopath = vbpath + ",utils,topo,eegref.npz"
    file = os.path.join(*topopath.split(","))
    print(file)
    assert os.path.isfile(file)


def test_ico_file():
    """Test if Sleep icon is installed."""
    vbpath = get_python_lib()
    topopath = vbpath + ",sleep,ico,sleep.svg"
    file = os.path.join(*topopath.split(","))
    print(file)
    assert os.path.isfile(file)
