"""Test visbrain objects."""
import numpy as np
import vispy

from visbrain.objects import SourceObj, CombineSources


test_node = vispy.scene.Node(name='TestNode')

###############################################################################
#                                  SOURCES
###############################################################################
n_sources = 20
s_xyz = np.random.uniform(-20, 20, (n_sources, 3))
s_data = np.random.rand(n_sources)
s_color = np.random.uniform(.1, .9, (n_sources, 4))
s_mask = s_data >= .7
s_text = ['S%s' % str(k) for k in range(n_sources)]

s_obj = SourceObj('S1', s_xyz, data=s_data, color=s_color, alpha=.7,
                  symbol='x', radius_min=10.7, radius_max=25.8,
                  edge_width=1.4, edge_color='green', system='tal',
                  mask=s_mask, mask_color='#ab4642', text=s_text,
                  text_color='blue', text_bold=True,
                  text_translate=(.1, .02, .08), visible=True)
s_obj2 = SourceObj('S2', np.random.uniform(-20, 20, (n_sources * 2, 3)))

s_comb = CombineSources([s_obj, s_obj2])

###############################################################################
#                                  MESH
###############################################################################
vertices = s_xyz.max() * np.random.rand(100, 3, 3)


class ObjectMethods(object):
    """Method to test visbrain objects."""

    @staticmethod
    def _assert_and_test(obj, attr, to_set, to_test='NoAttr'):
        """Assert to obj and test."""
        # Set attribute :
        value = exec("{}.{}".format(obj, attr))
        value = to_set
        # Test either to_set or to_test :
        value_to_test = to_set if to_test == 'NoAttr' else to_test
        # Test according to data type :
        if isinstance(value_to_test, np.ndarray):
            assert np.array_equal(value, value_to_test)
        else:
            assert value == value_to_test

###############################################################################
###############################################################################
#                                  SOURCES
###############################################################################
###############################################################################


class TestSourceObj(ObjectMethods):
    """Test source object."""

    @staticmethod
    def _assert_and_test(obj, attr, to_set, to_test='NoAttr'):
        """Assert to obj and test."""
        # Set attribute :
        value = exec("{}.{}".format(obj, attr))
        value = to_set
        # Test either to_set or to_test :
        value_to_test = to_set if to_test == 'NoAttr' else to_test
        # Test according to data type :
        if isinstance(value_to_test, np.ndarray):
            assert np.array_equal(value, value_to_test)
        else:
            assert value == value_to_test

    def test_source_attributes(self):
        """Test function source_attributes."""
        # Attributes without mask :
        assert s_obj._xyz.shape == (n_sources, 3)
        assert s_obj._data.shape == s_data.shape
        assert len(s_obj._text) == len(s_text)
        # Attribute with mask :
        n_mask = np.sum(s_obj.visible_and_not_masked)
        assert len(s_obj.visible_and_not_masked) == len(s_data)
        assert s_obj.xyz.shape == (n_mask, 3)
        assert len(s_obj.data) == n_mask
        assert len(s_obj.text) == n_mask
        # Assert :
        self._assert_and_test('s_obj', 'radius_min', 12.)
        self._assert_and_test('s_obj', 'radius_min', 22.)
        self._assert_and_test('s_obj', 'symbol', 'disc')
        self._assert_and_test('s_obj', 'edge_width', .1)
        self._assert_and_test('s_obj', 'edge_color', [.7] * 4)
        self._assert_and_test('s_obj', 'alpha', .4)
        new_color = np.random.uniform(.1, .9, (n_sources, 4))
        self._assert_and_test('s_obj', 'color', new_color)
        new_mask = s_data >= .4
        self._assert_and_test('s_obj', 'mask', new_mask)
        assert isinstance(s_obj.is_masked, bool)
        self._assert_and_test('s_obj', 'mask_color', [0.] * 4)
        self._assert_and_test('s_obj', 'visible', new_mask)
        self._assert_and_test('s_obj', 'hide', np.invert(new_mask))
        self._assert_and_test('s_obj', 'text_size', 10.)
        self._assert_and_test('s_obj', 'text_color', [.5] * 4)
        self._assert_and_test('s_obj', 'text_translate', [.1, .4, .5])
        self._assert_and_test('s_obj', 'parent', test_node)
        self._assert_and_test('s_obj', 'name', 'S1')
        self._assert_and_test('s_obj', 'visible_obj', False)

    def test_source_builtin_methods(self):
        """Test function source_builtin_methods."""
        SourceObj('S', s_xyz)
        assert len(s_obj) == n_sources
        _xyz = s_obj.xyz
        for i, k in enumerate(s_obj):  # loop over visible sources
            assert np.array_equal(k, _xyz[[i], :])
        assert len(s_obj + s_obj) == 2 * n_sources
        repr(s_obj)
        assert str(s_obj) == 'S1'

    def test_source_analyse(self):
        """Test function source_analyse."""
        s_obj.analyse_sources()
        s_obj.analyse_sources(roi_obj=['brodmann', 'all', 'talairach'])

    def test_source_analyse_color(self):
        """Test function source_analyse_color."""
        df = s_obj.analyse_sources()
        s_obj.color_sources(df, 'brodmann')  # random color
        s_obj.color_sources(df, 'matter',  # predefined colors
                            roi_to_color={'White': 'red', 'Gray': 'green'})

    def test_source_select(self):
        """Test function select_sources."""
        to_test = ['inside', 'outside', 'close', 'none', 'left', 'right',
                   'all', None, False, True]
        for k in to_test:
            s_obj.set_visible_sources(select=k, v=vertices)

    def test_source_fit_to_vertices(self):
        """Test function source_fit_to_vertices."""
        s_obj.fit_to_vertices(vertices)

    def test_source_projection(self):
        """Test function source_projection."""
        s_obj.visible = True
        s_obj.project_modulation(vertices, 20.)
        s_obj.project_repartition(vertices, 20., contribute=True)
        s_obj.get_masked_index(vertices, 20.)


class TestCombineSources(ObjectMethods):
    """Test CombineSources."""

    def test_combine_sources_builtin_methods(self):
        """Test function combine_sources_builtin_methods."""
        CombineSources(s_obj)
        s2 = CombineSources([s_obj, s_obj2])
        s2.append(s_obj)
        assert str(s_comb['S2']) == str(s_comb[1])
        assert len(s_comb) == 2
        assert str(s_comb) == 'S1 + S2'
        repr(s_comb)
        for k, i in zip(s_comb, ['S1', 'S2']):
            assert str(k) == i
        s_comb.update()
        assert s_comb.get_list_of_objects() == ['S1', 'S2']
        s_comb.select('S2')
        assert s_comb.get_selected_object() == 'S2'

    def test_combine_sources_attributs(self):
        """Test function combine_sources_attributs."""
        self._assert_and_test('s_comb', 'parent', test_node)
        self._assert_and_test('s_comb', 'visible_obj', False)
        n_visibles = np.sum(s_comb.visible_and_not_masked)
        assert s_comb._xyz.shape[0] == 3 * n_sources
        assert len(s_comb._data) == 3 * n_sources
        assert len(s_comb._text) == 3 * n_sources
        assert len(s_comb.mask) == 3 * n_sources
        assert s_comb.xyz.shape[0] == n_visibles
        assert len(s_comb.data) == n_visibles
        assert len(s_comb.text) == n_visibles
        assert isinstance(s_comb.is_masked, bool)

    def test_combine_sources_fit_to_vertices(self):
        """Test function combine_sources_fit_to_vertices."""
        s_comb.fit_to_vertices(vertices)

    def test_combine_sources_analyse(self):
        """Test function combine_sources_analyse."""
        assert len(s_comb.analyse_sources()) == 3 * n_sources

    def test_combine_sources_set_visible_sources(self):
        """Test function combine_sources_set_visible_sources."""
        s_comb.set_visible_sources('all')
