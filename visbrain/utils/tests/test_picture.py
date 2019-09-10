"""Test functions in physio.py."""
import numpy as np

from visbrain.utils.picture import (piccrop, picresize)


class TestPicture(object):
    """Test functions in picture.py."""

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
        self._compare_shapes(s_1, [(10, 20), (15, 20), (17, 20)])
        self._compare_shapes(s_0_ex, [(50, 100), (50, 67), (50, 60)])
        self._compare_shapes(s_1_ex, [(30, 60), (45, 60), (50, 60)])
