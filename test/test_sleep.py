from __future__ import print_function
from visbrain import Sleep
import os
from distutils.sysconfig import get_python_lib
from warnings import warn


def test_instance_sleep():
    """Test the creation of a Sleep instance."""
    pass
    # s = Sleep()


def test_topo_file():
    """Test if the topo reference file is installed."""
    try:
        vbpath = get_python_lib()
        topopath = vbpath + ",visbrain,utils,topo,eegref.npz"
        file = os.path.join(*topopath.split(","))
        warn('Distant version passed for topo file')
        assert os.path.isfile(file)
    except:
        topopath = ",visbrain,utils,topo,eegref.npz"
        file = os.path.join(*topopath.split(","))
        warn('Local version passed for topo file')
        assert os.path.isfile(file)


def test_ico_file():
    """Test if Sleep icon is installed."""
    try:
        vbpath = get_python_lib()
        topopath = vbpath + ",visbrain,sleep,ico,sleep.svg"
        file = os.path.join(*topopath.split(","))
        warn('Distant version passed for sleep ico file')
        assert os.path.isfile(file)
    except:
        topopath = ",visbrain,sleep,ico,sleep.svg"
        file = os.path.join(*topopath.split(","))
        warn('Local version passed for sleep ico file')
        assert os.path.isfile(file)