"""Test functions in color.py."""
import numpy as np

from visbrain.utils.color import (color2vb, array2colormap, cmap_to_glsl,
                                  dynamic_color, color2faces, type_coloring,
                                  mpl_cmap, color2tuple, mpl_cmap_index,
                                  colorclip, Colormap)


class TestColor(object):
    """Test functions in color.py."""

    def test_colormap(self):
        """Test function colormap."""
        # ---------------- 1D data vector ----------------
        data_1d = np.arange(511)
        cmap_1d = Colormap(cmap='inferno', vmin=11, under='gray',
                           vmax=500, over='red', translucent=(.1, None))
        assert cmap_1d.to_rgba(data_1d).shape == (511, 4)
        # Properties :
        from vispy.color import Colormap as VispyColormap
        assert isinstance(cmap_1d.data, np.ndarray)
        assert isinstance(cmap_1d.glsl, VispyColormap)
        assert np.array_equal(cmap_1d.data[:, 0], cmap_1d.r)          # red
        assert np.array_equal(cmap_1d.data[:, 1], cmap_1d.g)          # green
        assert np.array_equal(cmap_1d.data[:, 2], cmap_1d.b)          # blue
        assert np.array_equal(cmap_1d.data[:, 3], cmap_1d.alpha)      # alpha
        assert np.array_equal(cmap_1d.data[:, 0:3], cmap_1d.rgb)      # rgb
        assert cmap_1d.rgb.shape == (1024, 3)
        # ---------------- 2D data vector ----------------
        # Alpha completion :
        data_2d_alpha = np.random.uniform(size=(1024, 3))
        cmap_2d_alpha = Colormap(data_2d_alpha)
        assert cmap_2d_alpha.shape == (1024, 4)
        # 2D (1024, 4) colors :
        data_2d_uni = np.random.uniform(size=(1024, 4))
        cmap_2d_uni = Colormap(data_2d_uni)
        assert cmap_2d_uni.shape == (1024, 4)
        # 2D (511, 4) colors that need to be interpolated :
        cmap_2d_interp = np.random.uniform(size=(5, 4))
        cmap_2d_interp = Colormap(cmap=cmap_2d_interp, interpolation='linear')
        assert cmap_2d_interp.shape == (1024, 4)
        # 2D (1, 4) colors that need to be repeated :
        data_2d_single = np.random.uniform(size=(1, 4))
        cmap_2d_single = Colormap(data_2d_single, interpolation='linear')
        assert cmap_2d_single.shape == (1024, 4)
        # 2D (511, 4) colors without interpolation :
        data_2d_norm = np.random.uniform(size=(511, 4))
        cmap_2d_norm = Colormap(data_2d_norm)
        assert cmap_2d_norm.shape == (511, 4)

    def test_color2vb(self):
        """Test color2vb function."""
        assert np.array_equal(color2vb(), np.array([[1., 1., 1., 1.]]))
        color2vb('green')
        color2vb('#ab4642')
        color2vb([0.5789, 1., 0.4235], alpha=.4)
        color2vb((0.5789, 1., 0.4235, .3), alpha=.4)
        assert color2vb((0., 1., 0.), length=10).shape == (10, 4)
        assert color2vb(np.array([0., 1., 0., .5])).ravel()[-1] == .5

    def test_color2tuple(self):
        """Test color2tuple function."""
        g1 = np.array([[0., 1., 0., 1.]])
        g2 = np.array([[0.5789, 1., 0.4235, .4]])
        assert len(color2tuple(g1)) == 3
        assert len(color2tuple(g2, rmalpha=False)) == 4
        assert np.asarray(color2tuple(g1,
                                      astype=np.float64)).dtype == 'float64'
        assert len(str(color2tuple(g2, astype=float, roundto=4)[0])) == 6

    def test_array2colormap(self):
        """Test array2colormap function."""
        vec = np.random.randn(10)
        mat = np.random.randn(10, 30)
        array2colormap(vec, cmap='Reds')
        array2colormap(mat, clim=(-1., 1.), cmap='viridis')
        array2colormap(mat, clim=(-1., 1.), vmin=.1, under='gray', vmax=.7,
                       over='red', cmap='Spectral_r')
        array2colormap(vec, faces_render=True)

    def test_cmap_to_glsl(self):
        """Test function cmap_to_glsl."""
        from vispy.color.colormap import Colormap
        cmap_1 = cmap_to_glsl()
        cmap_2 = cmap_to_glsl(limits=(7, 200))
        assert isinstance(cmap_1, Colormap)
        assert isinstance(cmap_2, Colormap)

    def test_dynamic_color(self):
        """Test dynamic_color function."""
        color = np.array([[1., 0., 0., 1.],
                         [1., 0., 0., 1.],
                         [1., 0., 0., 1.],
                         [1., 0., 0., 1.],
                         [1., 0., 0., 1.]])
        x = np.random.rand(color.shape[0])
        dynamic_color(color, x, dynamic=(0., 1.))
        dynamic_color(color, x, dynamic=(1., 0.))

    def test_color2faces(self):
        """Test color2faces function."""
        color = (1., 0., 0., 1.)
        assert color2faces(color, 10).shape == (10, 3, 4)

    def test_colorclip(self):
        """Test colorclip function."""
        x = np.arange(0, 10, 1.).reshape(5, 2)
        assert colorclip(x, 2, 'under').min() == 2
        assert colorclip(x, 5, 'over').max() == 5

    def test_type_coloring(self):
        """Test type_coloring function."""
        reps = 20
        assert type_coloring(color='rnd', n=reps).shape == (reps, 3)
        assert type_coloring(color='dynamic', n=reps, cmap='Spectral_r',
                             vmin=1., under='gray', vmax=8.,
                             over='#ab4642').shape == (reps, 3)
        uni = type_coloring(color='uniform', unicolor='red', n=reps)
        assert np.array_equal(uni, np.tile((1., 0., 0.), (reps, 1)))

    def test_mpl_cmap(self):
        """Test mpl_cmap function."""
        mpl_cmap(False)
        mpl_cmap(True)

    def test_mpl_cmap_index(self):
        """Test mpl_cmap_index function."""
        mpl = mpl_cmap()
        r = mpl_cmap_index('viridis')
        r2 = mpl_cmap_index('viridis_r')
        r3 = mpl_cmap_index('viridis', mpl)
        assert isinstance(r[0], np.int64) and not r[1]
        assert isinstance(r2[0], np.int64) and r2[1]
        assert r == r3
