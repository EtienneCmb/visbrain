import numpy as np
from warnings import warn

from visbrain.utils.color import (color2vb, array2colormap, dynamic_color,
                                  color2faces, type_coloring, mpl_cmap,
                                  color2tuple, mpl_cmap_index, colorclip)


###############################################################################
###############################################################################
#                                color.py
###############################################################################
###############################################################################

def test_utils_color2vb():
    """Test color2vb function."""
    assert np.array_equal(color2vb(), np.array([[1., 1., 1., 1.]]))
    color2vb('green')
    color2vb([0.5789, 1., 0.4235], alpha=.4)
    assert color2vb((0., 1., 0.), length=10).shape == (10, 4)
    assert color2vb(np.array([0., 1., 0., .5])).ravel()[-1] == .5


def test_utils_color2tuple():
    """Test color2tuple function."""
    g1 = np.array([[0., 1., 0., 1.]])
    g2 = np.array([[0.5789, 1., 0.4235, .4]])
    assert len(color2tuple(g1)) == 3
    assert len(color2tuple(g2, rmalpha=False)) == 4
    assert np.asarray(color2tuple(g1, astype=np.float64)).dtype == 'float64'
    assert len(str(color2tuple(g2, astype=float, roundto=4)[0])) == 6


def test_utils_array2colormap():
    """Test array2colormap function."""
    vec = np.random.randn(10)
    mat = np.random.randn(10, 30)
    array2colormap(vec, cmap='Reds')
    array2colormap(mat, clim=(-1., 1.), cmap='viridis')
    array2colormap(mat, clim=(-1., 1.), vmin=.1, under='gray', vmax=.7,
                   over='red', cmap='Spectral_r')
    array2colormap(vec, faces_render=True)


def test_utils_dynamic_color():
    """Test dynamic_color function."""
    color = np.array([[1., 0., 0., 1.],
                     [1., 0., 0., 1.],
                     [1., 0., 0., 1.],
                     [1., 0., 0., 1.],
                     [1., 0., 0., 1.]])
    x = np.random.rand(color.shape[0])
    dynamic_color(color, x, dynamic=(0., 1.))
    dynamic_color(color, x, dynamic=(1., 0.))


def test_utils_color2faces():
    """Test color2faces function."""
    color = (1., 0., 0., 1.)
    assert color2faces(color, 10).shape == (10, 3, 4)


def test_utils_colorclip():
    """Test colorclip function."""
    x = np.arange(0, 10, 1.).reshape(5, 2)
    assert colorclip(x, 2, 'under').min() == 2
    assert colorclip(x, 5, 'over').max() == 5


def test_utils_type_coloring():
    """Test type_coloring function."""
    reps = 20
    assert type_coloring(color='rnd', n=reps).shape == (reps, 3)
    assert type_coloring(color='dynamic', n=reps, cmap='Spectral_r', vmin=1.,
                         under='gray', vmax=8.,
                         over='#ab4642').shape == (reps, 3)
    uni = type_coloring(color='uniform', unicolor='red', n=reps)
    assert np.array_equal(uni, np.tile((1., 0., 0.), (reps, 1)))


def test_utils_mpl_cmap():
    """Test mpl_cmap function."""
    mpl_cmap(False)
    mpl_cmap(True)


def test_utils_mpl_cmap_index():
    """Test mpl_cmap_index function."""
    mpl = mpl_cmap(True)
    r = mpl_cmap_index('viridis')
    r2 = mpl_cmap_index('viridis_r')
    r3 = mpl_cmap_index('viridis_r', mpl)
    assert isinstance(r[0], np.int64) and not r[1]
    assert isinstance(r2[0], np.int64) and r2[1]
    assert r2 == r3