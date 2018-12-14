"""Test SceneObj and VisbrainCanvas."""
import numpy as np
# import pytest
import vispy

from visbrain.tests._tests_visbrain import _TestVisbrain
from visbrain.objects.scene_obj import VisbrainCanvas, SceneObj
from visbrain.objects import SourceObj, ConnectObj, BrainObj, ImageObj

test_node = vispy.scene.Node(name='TestNode')
camera = vispy.scene.cameras.TurntableCamera()
cam_state = {'elevation': 0., 'azimuth': 90.}

# Visbrain canvas :
vb_can_w = VisbrainCanvas()
vb_can = VisbrainCanvas(axis=True, title='tit', xlabel='xlab', ylabel='ylab',
                        name='Can1', add_cbar=True)

# Scene :
sc_obj_2d_1 = SceneObj(bgcolor=(0., 0., 0.))
sc_obj_3d_1 = SceneObj(bgcolor='#ab4642')
sc_obj_3d_2 = SceneObj(bgcolor='olive')

# Objects :
n_sources = 10
s_1 = 20. * np.random.rand(n_sources, 3)
s_2 = 20. * np.random.rand(n_sources, 3)
b_obj_1 = BrainObj('B1')
b_obj_2 = BrainObj('B2')
s_obj_1 = SourceObj('S1', s_1)
s_obj_2 = SourceObj('S1', s_2)
c_obj_1 = ConnectObj('C1', s_1, np.random.rand(n_sources, n_sources))
c_obj_2 = ConnectObj('C2', s_2, np.random.rand(n_sources, n_sources))
im_obj_1 = ImageObj('IM1', np.random.rand(10, 20))
im_obj_2 = ImageObj('IM2', np.random.rand(10, 20))
im_obj_3 = ImageObj('IM3', np.random.rand(10, 20))


class TestVisbrainCanvas(_TestVisbrain):
    """Test the definition of a visbrain canvas."""

    OBJ = vb_can

    def test_definition(self):
        """Test function definition."""
        VisbrainCanvas()                          # without axis
        VisbrainCanvas(axis=True)                 # with axis
        VisbrainCanvas(axis=True, add_cbar=True)  # with axis + colorbar

    def test_methods(self):
        """Test function methods."""
        assert vb_can
        vb_can.update()
        vb_can.set_default_state()

    def test_attributes(self):
        """Test function attributes."""
        self.assert_and_test('visible', False)
        self.assert_and_test('axis', True)
        self.assert_and_test('xlabel', 'new_xlab')
        self.assert_and_test('ylabel', 'new_xlab')
        self.assert_and_test('title', 'new_title')
        self.assert_and_test('camera', camera)
        self.assert_and_test('axis_color', [0.] * 4)
        self.assert_and_test('title_font_size', 4.)
        self.assert_and_test('axis_font_size', 4.)
        self.assert_and_test('tick_font_size', 4.)
        self.assert_and_test('bgcolor', [1.] * 4)


class TestSceneObj(_TestVisbrain):
    """Test the creation of a scene for objects."""

    OBJ = sc_obj_3d_1

    def test_definition(self):
        """Test function definition."""
        SceneObj(bgcolor='red')

    def test_add_to_the_same_subplot(self):
        """Test function add_subplot."""
        sc_obj_3d_1.add_to_subplot(s_obj_1)
        sc_obj_3d_1.add_to_subplot(b_obj_1, use_this_cam=True)
        sc_obj_3d_1.add_to_subplot(c_obj_1, title='Test Scene', title_size=20.,
                                   title_color='#ab4642', rotate='left')

    def test_add_to_multiple_subplot(self):
        """Test function add_to_multiple_subplot."""
        sc_obj_2d_1.add_to_subplot(im_obj_1, row=0, col=0, row_span=2,
                                   title='Im1')
        sc_obj_2d_1.add_to_subplot(im_obj_2, row=0, col=1, title='Im2')
        sc_obj_2d_1.add_to_subplot(im_obj_3, row=1, col=1, title='Im3')

    def test_link(self):
        """Test function link."""
        sc_obj_3d_2.add_to_subplot(s_obj_2, row=0, col=0)
        sc_obj_3d_2.add_to_subplot(b_obj_2, row=0, col=1)
        sc_obj_3d_2.add_to_subplot(c_obj_2, row=0, col=2)
        sc_obj_3d_2.link(-1)

    # @pytest.mark.xfail(reason="Failed if display not correctly configured",
    #                    run=True, strict=False)
    # def test_screenshot(self):
    #     """Test function screenshot."""
    #     sc_obj_3d_1.screenshot(self.to_tmp_dir('SceneObj_3d1.png'))
    #     sc_obj_3d_2.screenshot(self.to_tmp_dir('SceneObj_3d2.png'))
    #     sc_obj_2d_1.screenshot(self.to_tmp_dir('SceneObj_2d2.png'))
