from __future__ import print_function
from visbrain import Brain
import os
from distutils.sysconfig import get_python_lib


def test_brain_templates():
    """Test if templates are installed."""
    vbpath = get_python_lib()
    brainpath = vbpath + ",visbrain,brain,base,templates"
    for k in ['B1.npz', 'B2.npz', 'B3.npz', 'roi.npz']:
        s = brainpath + ',' + k
        assert os.path.isfile(os.path.join(*s.split(",")))


def test_brain_rotate():
    """Test brain rotation."""
    # Define a Brain instance :
    vb = Brain()
    # Predefined rotation :
    vb.rotate(fixed='sagittal_1')
    # Custom rotation :
    vb.rotate(custom=(90.0, 0.0))
