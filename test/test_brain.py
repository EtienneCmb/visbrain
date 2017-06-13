import visbrain
from visbrain import Brain
import os


def test_instance_brain():
    """Test the creation of a Brain instance"""
    pass
    # Brain()


def test_brain_templates():
    """Test is templates are installed."""
    vbpath = visbrain.__file__.split('__init__')[0] + 'brain/base/templates/'
    for k in ['B1.npz', 'B2.npz', 'B3.npz', 'roi.npz']:
        assert os.path.isfile(os.path.join(vbpath, k))
