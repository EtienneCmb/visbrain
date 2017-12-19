"""Base class for testing visbrain objects."""
import pytest
import vispy

from visbrain.tests._tests_visbrain import _TestVisbrain


class _TestObjects(_TestVisbrain):
    """Test visbrain objects."""

    PARENT = vispy.scene.Node(name='TestNode')
    TRANSFORM = vispy.visuals.transforms.STTransform(scale=[1., 2., 3.],
                                                     translate=[4., 5., 6.])

    def test_get_camera(self):
        """Test if the camera is defined."""
        self.OBJ._get_camera()

    def test_object_name(self):
        """Test if the object name is correct."""
        assert isinstance(self.OBJ.name, str)

    def test_visible_obj(self):
        """Test setting the object visible or hide."""
        for k in [False, True]:
            self.OBJ.visible_obj = k
            assert self.OBJ.visible_obj == k

    def test_preview(self):
        """Test function preview."""
        self.OBJ.preview(show=False, axis=True, xyz=True, bgcolor='black')

    def test_transform(self):
        """Test setting transformation."""
        self.OBJ.transform = self.TRANSFORM

    def test_repr(self):
        """Test string representation."""
        assert isinstance(repr(self.OBJ), str)

    def test_str(self):
        """Test string representation."""
        assert str(self.OBJ) == self.OBJ.name

    def test_describe_tree(self):
        assert isinstance(self.OBJ.describe_tree(), str)

    @pytest.mark.xfail(reason="Failed if display not correctly configured",
                       run=True, strict=False)
    def test_screenshot(self):
        """Test screenshot rendering."""
        basename = self.to_tmp_dir(repr(self.OBJ))
        self.OBJ.screenshot(basename + '.png')

    def test_parent(self):
        """Test setting parent."""
        self.parent_testing(self.OBJ, self.PARENT)
