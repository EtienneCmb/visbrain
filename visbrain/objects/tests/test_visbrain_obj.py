"""Test VisbrainObject and CombineObjects classes."""
import pytest
import vispy

from visbrain.objects import VisbrainObject, CombineObjects
from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.tests._tests_visbrain import _TestVisbrain


test_node = vispy.scene.Node(name='TestNode')
vb_obj = VisbrainObject('VB1', parent=test_node)
vb_obj2 = VisbrainObject('VB2', parent=test_node)
vb_comb = CombineObjects(VisbrainObject, [vb_obj, vb_obj2])


class TestVisbrainObj(_TestObjects):
    """Test visbrain object."""

    OBJ = vb_obj

    def test_definition(self):
        """Test object definition."""
        VisbrainObject('VB1', parent=test_node)

    def test_get_camera(self):
        """Test if a NotImplemented error is raised."""
        with pytest.raises(NotImplementedError):
            vb_obj._get_camera()

    def test_preview(self):
        """Test if a NotImplemented error is raised."""
        with pytest.raises(NotImplementedError):
            vb_obj.preview(show=False, axis=True, xyz=True)

    def test_update_cbar(self):
        """Test if a NotImplementedError is raised."""
        with pytest.raises(NotImplementedError):
            vb_obj._update_cbar()

    def test_update_cbar_minmax(self):
        """Test if a NotImplementedError is raised."""
        with pytest.raises(NotImplementedError):
            vb_obj._update_cbar_minmax()

    def test_builtin_methods(self):
        """Test builtin methods."""
        assert str(vb_obj) == 'VB1'
        repr(vb_obj)


class TestCombineVisbrain(_TestVisbrain):
    """Test combine visbrain objects."""

    OBJ = vb_comb

    def test_definition(self):
        """Test object definition."""
        CombineObjects(VisbrainObject, None)
        CombineObjects(VisbrainObject, [vb_obj, vb_obj2])

    def test_builtin_methods(self):
        """Test function builtin_methods."""
        assert vb_comb['VB1'] == vb_comb[0]
        vb_comb['VB2'].parent = test_node
        assert len(vb_comb) == 2
        for k, i in zip(vb_comb, ['VB1', 'VB2']):
            assert str(k) == i
        assert str(vb_comb) == 'VB1 + VB2'
        repr(vb_comb)

    def test_get_list_of_objects(self):
        """Test function get_list_of_objects."""
        assert vb_comb.get_list_of_objects() == ['VB1', 'VB2']

    def test_select(self):
        """Test function select."""
        vb_comb.select('VB2')

    def test_get_selected_object(self):
        """Test function get_selected_object."""
        assert vb_comb.get_selected_object() == 'VB2'

    def test_append(self):
        """Test function methods."""
        # vb_comb.update()  # no upate() in VisbrainObj
        vb_comb.append(vb_obj)
        assert len(vb_comb) == 3

    def test_attributes(self):
        """Test function attributes."""
        self.parent_testing(vb_comb, test_node)
        self.assert_and_test('visible_obj', True)
