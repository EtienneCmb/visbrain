import numpy as np
from warnings import warn

from visbrain.utils.color import (color2vb, array2colormap, dynamic_color,
                                  color2faces, type_coloring, mpl_cmap,
                                  color2tuple, mpl_cmap_index)


###############################################################################
#                                COLOR
###############################################################################

def test_visbrain_color():
    """"""
    # _____________________ color2vb _____________________
    assert np.array_equal(color2vb(), np.array([[1., 1., 1., 1.]]))
    g1 = color2vb('green')
    g2 = color2vb([0.5789, 1., 0.4235], alpha=.4)
    assert color2vb((0., 1., 0.), length=10).shape == (10, 4)
    assert color2vb(np.array([0., 1., 0., .5])).ravel()[-1] == .5

    # _____________________ color2tuple _____________________
    assert len(color2tuple(g1)) == 3
    assert len(color2tuple(g2, rmalpha=False)) == 4
    assert np.asarray(color2tuple(g1, astype=np.float64)).dtype == 'float64'
    assert len(str(color2tuple(g2, astype=float, roundto=4)[0])) == 6

    # _____________________ array2colormap _____________________

