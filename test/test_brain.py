from __future__ import print_function
from visbrain import Brain
import os
from distutils.sysconfig import get_python_lib


def test_instance_brain():
    """Test the creation of a Brain instance."""
    pass
    # Brain()


def test_brain_templates():
    """Test if templates are installed."""
    vbpath = os.path.join(get_python_lib(), '/visbrain/brain/base/templates/')
    for k in ['B1.npz', 'B2.npz', 'B3.npz', 'roi.npz']:
        assert os.path.isfile(os.path.join(vbpath, k))
