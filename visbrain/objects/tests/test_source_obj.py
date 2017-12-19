"""Test SourceObj."""
import numpy as np

from visbrain.objects import SourceObj, CombineSources, BrainObj, RoiObj
from visbrain.objects.tests._testing_objects import _TestObjects


# Source's data :
n_sources = 20
s_xyz = np.random.uniform(-20, 20, (n_sources, 3))
s_data = np.random.rand(n_sources)
s_color = np.random.uniform(.1, .9, (n_sources, 4))
s_mask = s_data >= .7
s_text = ['S%s' % str(k) for k in range(n_sources)]

# Vertices (for projection)
n_vertices, n_faces = 100, 50
vertices_x3 = s_xyz.max() * np.random.rand(n_vertices, 3, 3)
vertices = s_xyz.max() * np.random.rand(n_vertices, 3)
b_obj = BrainObj('B3')
roi_obj = RoiObj('talairach')

s_obj = SourceObj('S1', s_xyz, data=s_data, color=s_color, alpha=.7,
                  symbol='x', radius_min=10.7, radius_max=25.8,
                  edge_width=1.4, edge_color='green', system='tal',
                  mask=s_mask, mask_color='#ab4642', text=s_text,
                  text_color='blue', text_bold=True,
                  text_translate=(.1, .02, .08), visible=True)
s_obj2 = SourceObj('S2', np.random.uniform(-20, 20, (n_sources * 2, 3)))

s_comb = CombineSources([s_obj, s_obj2])


class TestSourceObj(_TestObjects):
    """Test source object."""

    OBJ = s_obj

    def test_definition(self):
        """Test function definition."""
        SourceObj('S', s_xyz)

    def test_attributes(self):
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
        self.assert_and_test('radius_min', 12.)
        self.assert_and_test('radius_min', 22.)
        self.assert_and_test('symbol', 'disc')
        self.assert_and_test('edge_width', .1)
        edge_color = np.array([.7] * 4).astype(np.float32)
        self.assert_and_test('edge_color', edge_color)
        self.assert_and_test('alpha', .4)
        new_color = np.random.uniform(.1, .9, (n_sources, 4))
        self.assert_and_test('color', new_color)
        new_mask = s_data >= .4
        self.assert_and_test('mask', new_mask)
        assert isinstance(s_obj.is_masked, bool)
        mask_color = np.array([0.] * 4).astype(np.float32)
        self.assert_and_test('mask_color', mask_color)
        self.assert_and_test('visible', new_mask)
        np.testing.assert_array_equal(s_obj.hide, np.invert(new_mask))
        self.assert_and_test('text_size', 10.)
        text_color = np.array([.5] * 4).astype(np.float32)
        self.assert_and_test('text_color', text_color)
        self.assert_and_test('text_translate', [.1, .4, .5])
        assert s_obj.name == 'S1'
        self.assert_and_test('visible_obj', False)

    def test_builtin_methods(self):
        """Test function source_builtin_methods."""
        assert len(s_obj) == n_sources
        _xyz = s_obj.xyz
        for i, k in enumerate(s_obj):  # loop over visible sources
            assert np.array_equal(k, _xyz[[i], :])
        assert len(s_obj + s_obj) == 2 * n_sources
        repr(s_obj)
        assert str(s_obj) == 'S1'

    def test_analyse_sources(self):
        """Test function source_analyse."""
        s_obj.analyse_sources()
        s_obj.analyse_sources(roi_obj)
        s_obj.analyse_sources('brodmann', keep_only=['BA4', 'BA6', 'BA8'])
        s_obj.analyse_sources(roi_obj=['brodmann', 'all', 'talairach'])

    def test_color_sources(self):
        """Test function source_analyse_color."""
        df = s_obj.analyse_sources()
        s_obj.color_sources(data=s_data)                       # data
        s_obj.color_sources(analysis=df, color_by='brodmann')  # random
        s_obj.color_sources(analysis=df, color_by='matter',    # predefined
                            roi_to_color={'White': 'red', 'Gray': 'green'},
                            hide_others=True)

    def test_set_visible_sources(self):
        """Test function select_sources."""
        to_test = ['inside', 'outside', 'close', 'none', 'left', 'right',
                   'all', None, False, True]
        for k in to_test:
            s_obj.set_visible_sources(select=k, v=vertices_x3)
            s_obj.set_visible_sources(select=k, v=vertices)

    def test_fit_to_vertices(self):
        """Test function source_fit_to_vertices."""
        s_obj.fit_to_vertices(vertices_x3)

    def test_projection(self):
        """Test function source_projection."""
        s_obj.visible = True
        s_obj.project_sources(b_obj, project='modulation')
        s_obj.project_sources(b_obj, project='repartition', contribute=True)


class TestCombineSources(object):
    """Test CombineSources."""

    def test_definition(self):
        """Test function definition."""
        CombineSources(s_obj)

    def test_builtin_methods(self):
        """Test function combine_sources_builtin_methods."""
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

    def test_attributes(self):
        """Test function combine_sources_attributes."""
        s_comb.visible_obj = False
        assert not s_comb.visible_obj
        n_visibles = np.sum(s_comb.visible_and_not_masked)
        assert s_comb._xyz.shape[0] == 3 * n_sources
        assert len(s_comb._data) == 3 * n_sources
        assert len(s_comb._text) == 3 * n_sources
        assert len(s_comb.mask) == 3 * n_sources
        assert s_comb.xyz.shape[0] == n_visibles
        assert len(s_comb.data) == n_visibles
        assert len(s_comb.text) == n_visibles
        assert isinstance(s_comb.is_masked, bool)

    def test_fit_to_vertices(self):
        """Test function combine_sources_fit_to_vertices."""
        s_comb.fit_to_vertices(vertices)
        s_comb.fit_to_vertices(vertices_x3)

    def test_analyse(self):
        """Test function combine_sources_analyse."""
        assert len(s_comb.analyse_sources()) == 3 * n_sources

    def test_set_visible_sources(self):
        """Test function combine_sources_set_visible_sources."""
        s_comb.set_visible_sources('all')
