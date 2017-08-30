import numpy as np
from warnings import warn
import math

from visbrain.utils.cameras import FixedCam
from visbrain.utils.color import (color2vb, array2colormap, dynamic_color,
                                  color2faces, type_coloring, mpl_cmap,
                                  color2tuple, mpl_cmap_index, colorclip)
from visbrain.utils.filtering import (filt, morlet, ndmorlet, morlet_power,
                                      welch_power)
from visbrain.utils.others import (vis_args, check_downsampling, vispy_array,
                                   convert_meshdata, add_brain_template,
                                   remove_brain_template)
from visbrain.utils import (piccrop, picresize)
from visbrain.utils.sigproc import (normalize, movingaverage, derivative, tkeo,
                                    soft_thresh, zerocrossing, power_of_ten)
from visbrain.utils.transform import (vprescale, vprecenter, vpnormalize,
                                      array_to_stt)

###############################################################################
###############################################################################
#                                cameras.py
###############################################################################
###############################################################################


class TestCamera(object):
    """Test function in camera.py."""

    def test_fixed_camera(self):
        """Test fixed_camera function."""
        FixedCam()

###############################################################################
###############################################################################
#                                color.py
###############################################################################
###############################################################################


class TestColor(object):
    """Test function in color.py."""

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

###############################################################################
###############################################################################
#                                filtering.py
###############################################################################
###############################################################################


class TestFiltering(object):
    """Test functions in filtering.py."""

    def _creation(self, mean=False):
        if mean:
            return np.random.rand(2000), 3., 512.
        else:
            return np.random.rand(2000), [2., 4.], 512.

    def test_filt(self):
        """Test filt function."""
        from itertools import product
        x, f, sf = self._creation()
        btype = ['bandpass', 'bandstop', 'highpass', 'lowpass']
        order = [2, 3, 5]
        method = ['butterworth', 'bessel']
        way = ['filtfilt', 'lfilter']
        for k in product(btype, order, method, way):
            filt(sf, f, x, *k)

    def test_morlet(self):
        """Test morlet function."""
        x, f, sf = self._creation(True)
        morlet(x, sf, f)

    def test_ndmorlet(self):
        """Test ndmorlet function."""
        x, f, sf = self._creation(True)
        for k in [None, 'amplitude', 'phase', 'power']:
            ndmorlet(x, sf, f, get=k)

    def test_morlet_power(self):
        """Test morlet_power function."""
        x, _, sf = self._creation(True)
        f = [1., 2., 3., 4.]
        assert morlet_power(x, f, sf, norm=False).sum(0).max() > 1.
        assert math.isclose(morlet_power(x, f, sf, norm=True).sum(0).max(), 1.)

    def test_welch_power(self):
        """Test welch_power function."""
        x, f, sf = self._creation(False)
        welch_power(x, f[0], f[1], 50, 10.)

###############################################################################
###############################################################################
#                                others.py
###############################################################################
###############################################################################


class TestOthers(object):
    """Test functions in others.py."""

    def _creation(self):
        """Create vertices, faces and normals."""
        # Define random
        self.vertices = np.array([[0., 1., 0.],
                                  [0., 2., 0.],
                                  [0., 3., 1.],
                                  [1., 4., 0.]])
        self.normals = np.array([[-1., 1., 2.],
                                 [-1., 1., 2.],
                                 [-2., -3., -1.],
                                 [-4., -5., -4.]])
        self.faces = np.array([[0, 1, 2], [0, 1, 3], [1, 2, 3]])
        self.template = 'TestTemplate.npz'

    def test_vis_args(self):
        """Test vis_args function."""
        kw = {'r_arg1': 0., 'r_arg2': 1., 'r_arg3': 2., 's_arg1': 0.,
              'd_arg1': 0., 'r_arg4': 3., 'r_arg5': 4.}
        to_keep, to_remove = vis_args(kw, 'r_', ignore=['r_arg4', 'r_arg5'])
        assert to_keep == {'arg1': 0.0, 'arg2': 1.0, 'arg3': 2.0}
        assert to_remove == {'s_arg1': 0.0, 'd_arg1': 0.0, 'r_arg4': 3.0,
                             'r_arg5': 4.0}

    def test_check_downsampling(self):
        """Test check_downsampling function."""
        assert check_downsampling(1000., 100.) == 100.

    def test_vispy_array(self):
        """Test vispy_array function."""
        mat = np.random.randint(0, 10, (10, 30))
        mat_convert = vispy_array(mat, np.float64)
        assert mat_convert.flags['C_CONTIGUOUS']
        assert mat_convert.dtype == np.float64

    def test_convert_meshdata(self):
        """Test convert_meshdata function."""
        from vispy.geometry import MeshData
        import vispy.visuals.transforms as vist
        # Force creation of vertices, faces and normals :
        self._creation()
        tup = (self.vertices, self.faces, self.normals)
        # Compare (vertices + faces) Vs. MeshData :
        mesh1 = convert_meshdata(*tup)
        mesh2 = convert_meshdata(meshdata=MeshData(*tup))
        assert np.array_equal(mesh1[0], mesh2[0])
        assert np.array_equal(mesh1[1], mesh2[1])
        assert np.array_equal(mesh1[2], mesh2[2])
        # Invert normals :
        inv1 = convert_meshdata(*tup, invert_normals=True)[-1]
        assert np.array_equal(inv1, -mesh1[-1])
        # Create transformation :
        tr = vist.MatrixTransform()
        tr.rotate(90, (0, 0, 1))
        convert_meshdata(*tup, transform=tr)[-1]

    def test_add_brain_template(self):
        """Test add_brain_template function."""
        # Force creation of vertices, faces and normals :
        self._creation()
        tup = (self.vertices, self.faces, self.normals)
        # Get converted vertices, faces and normals :
        mesh1 = convert_meshdata(*tup)
        add_brain_template(self.template, *mesh1)

    def test_remove_brain_template(self):
        """Test remove_brain_template function."""
        # Force creation of vertices, faces and normals :
        self._creation()
        remove_brain_template(self.template)

###############################################################################
###############################################################################
#                                picture.py
###############################################################################
###############################################################################


class TestPicture(object):
    """Test function in picture.py."""

    def _compare_shapes(self, im, shapes):
        im_shapes = [k.shape for k in im]
        assert np.array_equal(im_shapes, shapes)

    def test_piccrop(self):
        """Test function piccrop."""
        pic = np.array([[0., 0., 0., 0., 0.],
                        [0., 0., 1., 0., 0.],
                        [0., 1., 1., 1., 0.],
                        [0., 0., 1., 0., 0.],
                        [0., 0., 0., 0., 0.]])
        destination = np.array([[0., 1., 0.],
                                [1., 1., 1.],
                                [0., 1., 0.]])
        assert np.array_equal(piccrop(pic, margin=0), destination)

    def test_picresize(self):
        """Test function picresize."""
        shapes = [(10, 20), (30, 40), (50, 60)]
        im = [np.random.rand(*k) for k in shapes]
        s_0 = picresize(im)
        s_0_ex = picresize(im, extend=True)
        s_1 = picresize(im, axis=1)
        s_1_ex = picresize(im, axis=1, extend=True)
        self._compare_shapes(s_0, [(10, 20), (10, 13), (10, 12)])
        self._compare_shapes(s_1, [(10, 20), (15, 20), (16, 20)])
        self._compare_shapes(s_0_ex, [(50, 100), (50, 66), (50, 60)])
        self._compare_shapes(s_1_ex, [(30, 60), (45, 60), (50, 60)])


###############################################################################
###############################################################################
#                                sigproc.py
###############################################################################
###############################################################################


class TestSigproc(object):
    """Test function in sigproc.py."""

    def test_normalize(self):
        """Test normalize function."""
        mat = np.random.rand(10, 20)
        mat_n = normalize(mat, -10., 14.)
        assert (mat_n.min() == -10.) and (mat_n.max() == 14.)

    def test_movingaverage(self):
        """Test function movingaverage."""
        x, window, sf = np.random.rand(2000), 10., 512.
        movingaverage(x, window, sf)

    def test_derivative(self):
        """Test function derivative."""
        x, window, sf = np.random.rand(2000), 10., 512.
        derivative(x, window, sf)

    def test_tkeo(self):
        """Test function tkeo."""
        x = np.random.rand(2000)
        tkeo(x)

    def test_soft_thresh(self):
        """Test function soft_thresh."""
        x = np.random.rand(2000)
        soft_thresh(x, .1)

    def test_zerocrossing(self):
        """Test function zerocrossing."""
        x = np.array([1., -10, -4, 2., 4., -7., -1., 5.])
        assert np.array_equal(zerocrossing(x), [1, 3, 5, 7])

    def test_power_of_ten(self):
        """Test function power_of_ten."""
        assert np.allclose(power_of_ten(-57.), (-57., 0))
        assert np.allclose(power_of_ten(1024.), (1.024, 3))
        assert np.allclose(power_of_ten(-14517.2), (-1.45172, 4))

###############################################################################
###############################################################################
#                                transform.py
###############################################################################
###############################################################################


class TestTransform(object):
    """Test function in transform.py."""

    def test_vprescale(self):
        """Test function vprescale."""
        mat = np.random.rand(10, 3)
        tr = vprescale(mat, dist=10.)
        assert np.abs(tr.map(mat).max()) - 10. < 2.

    def test_vprecenter(self):
        """Test function vprecenter."""
        mat = np.random.rand(10, 3) + 100.
        tr = vprecenter(mat)
        assert np.all(tr.map(mat).mean() < 1.)

    def test_vpnormalize(self):
        """Test function vpnormalize."""
        mat = np.random.rand(10, 3) + 100.
        tr = vpnormalize(mat, dist=5.)
        mat_n = tr.map(mat)
        assert np.all(mat_n.mean() < 1.)
        assert np.abs(mat_n.max() - 2.5) < 2.

    def test_array_to_stt(self):
        """Test function array_to_stt."""
        scale = (4., 5., 3.)
        translate = (10., 25., 7.)
        mat = np.array([[scale[0], 0., 0., translate[0]],
                        [0., scale[1], 0., translate[1]],
                        [0., 0., scale[2], translate[2]],
                        [0., 0., 0., 1.]
                        ])
        assert np.array_equal(array_to_stt(mat).matrix, mat)
