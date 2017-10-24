"""Test visbrain objects."""
import os
import numpy as np
import vispy

from visbrain.objects.visbrain_obj import VisbrainObject, CombineObjects
from visbrain.objects.scene_obj import VisbrainCanvas, SceneObj
from visbrain.objects.source_obj import SourceObj, CombineSources
from visbrain.objects.connect_obj import ConnectObj, CombineConnect
from visbrain.objects.picture_obj import PictureObj, CombinePictures
from visbrain.objects.ts_obj import TimeSeriesObj, CombineTimeSeries
from visbrain.objects.brain_obj import BrainObj

from visbrain.utils import remove_brain_template, get_data_path


###############################################################################
#                                  VISBRAIN
###############################################################################
test_node = vispy.scene.Node(name='TestNode')
camera = vispy.scene.cameras.TurntableCamera()

vb_obj = VisbrainObject('VB1', parent=test_node)
vb_obj2 = VisbrainObject('VB2', parent=test_node)
vb_comb = CombineObjects(VisbrainObject, [vb_obj, vb_obj2])

vb_can_w = VisbrainCanvas()
vb_can = VisbrainCanvas(axis=True, title='tit', xlabel='xlab', ylabel='ylab',
                        name='Can1', add_cbar=True)

sc_obj = SceneObj(bgcolor='#ab4642', show=False)

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
#                               CONNECTIVITY
###############################################################################
nodes = np.random.uniform(-20, 20, (n_sources, 3))
edges = np.random.rand(n_sources, n_sources)
select = np.logical_and(edges >= .1, edges >= .3)

c_obj = ConnectObj('C1', nodes, edges, select=select, line_width=4.1,
                   color_by='count', alpha=.7, dynamic=(.1, .7), cmap='magma',
                   clim=(0, 4), vmin=1, vmax=3, under='orange', over='blue')

nodes = np.random.uniform(-20, 20, (2 * n_sources, 3))
edges = 20 * np.random.rand(2 * n_sources, 2 * n_sources) - 10.
edges[edges <= -5.] = -5.
edges[edges >= 7] = 7.
edges = np.ma.masked_array(edges, ~np.logical_and(edges >= -6., edges <= 8.))
custom_colors = {-5.: 'red', 7.: 'orange'}
c_obj2 = ConnectObj('C2', nodes, edges, custom_colors=custom_colors, alpha=.7)

c_comb = CombineConnect([c_obj, c_obj2])

###############################################################################
#                               PICTURES
###############################################################################
pic_data = 100 * np.random.rand(n_sources, 10, 20)
pic_xyz = np.random.uniform(-20, 20, (n_sources, 3))
pic_select = np.random.randint(0, n_sources, (int(n_sources / 2),))

p_obj = PictureObj('P1', pic_data, pic_xyz, select=pic_select, width=8.,
                   height=5., alpha=.7, cmap='inferno', clim=(1., 90.),
                   vmin=5.1, vmax=84.1, under='orange', over='blue')

p_comb = CombinePictures([p_obj, p_obj])


###############################################################################
#                               TIME-SERIES
###############################################################################
ts_data = 100 * np.random.rand(n_sources, 100)
ts_xyz = np.random.uniform(-20, 20, (n_sources, 3))
ts_select = np.random.randint(0, n_sources, (int(n_sources / 2),))

ts_obj = TimeSeriesObj('TS1', ts_data, ts_xyz, select=ts_select, )


###############################################################################
#                               BRAIN
###############################################################################
b_obj = BrainObj('B1')

###############################################################################
#                                  MESH
###############################################################################
n_vertices, n_faces = 100, 50
vertices_x3 = s_xyz.max() * np.random.rand(n_vertices, 3, 3)
vertices = s_xyz.max() * np.random.rand(n_vertices, 3)
faces = np.random.randint(0, n_vertices, (n_faces, 3))


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
#                               VISBRAIN OBJECT
###############################################################################
###############################################################################


class TestVisbrainObj(ObjectMethods):
    """Test visbrain object."""

    def test_definition(self):
        """Test object definition."""
        VisbrainObject('VB1', parent=test_node)

    def test_builtin_methods(self):
        """Test builtin methods."""
        assert str(vb_obj) == 'VB1'
        repr(vb_obj)

    def test_attributes(self):
        """Test attributes."""
        self._assert_and_test('vb_obj', 'parent', test_node)
        self._assert_and_test('vb_obj', 'visible_obj', False)
        assert vb_obj.name == 'VB1'


class TestCombineVisbrain(ObjectMethods):
    """Test combine visbrain objects."""

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

    def test_methods(self):
        """Test function methods."""
        # vb_comb.update()  # no upate() in VisbrainObj
        assert vb_comb.get_list_of_objects() == ['VB1', 'VB2']
        vb_comb.select('VB2')
        assert vb_comb.get_selected_object() == 'VB2'
        vb_comb.append(vb_obj)
        assert len(vb_comb) == 3

    def test_attributes(self):
        """Test function attributes."""
        self._assert_and_test('vb_comb', 'parent', test_node)
        self._assert_and_test('vb_comb', 'visible_obj', True)


class TestVisbrainCanvas(ObjectMethods):
    """Test the definition of a visbrain canvas."""

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
        for k in ['vb_can']:  # , 'vb_can_w']:
            self._assert_and_test(k, 'visible', False)
            self._assert_and_test(k, 'axis', False)
            self._assert_and_test(k, 'xlabel', 'new_xlab')
            self._assert_and_test(k, 'ylabel', 'new_xlab')
            self._assert_and_test(k, 'title', 'new_title')
            self._assert_and_test(k, 'camera', camera)
            self._assert_and_test(k, 'axis_color', [0.] * 4)
            self._assert_and_test(k, 'title_font_size', 4.)
            self._assert_and_test(k, 'axis_font_size', 4.)
            self._assert_and_test(k, 'tick_font_size', 4.)
            self._assert_and_test(k, 'bgcolor', [1.] * 4)


class TestSceneObj(ObjectMethods):
    """Test the creation of a scene for objects."""

    def test_definition(self):
        """Test function definition."""
        SceneObj(bgcolor='red', show=False)

    def test_add_subplot(self):
        """Test function add_subplot."""
        sc_obj.add_to_subplot(s_obj, 0, 0)
        sc_obj.add_to_subplot(s_comb, 0, 1)
        sc_obj.add_to_subplot(c_obj, 1, 0)
        sc_obj.add_to_subplot(c_comb, 1, 1)

###############################################################################
###############################################################################
#                                  SOURCES
###############################################################################
###############################################################################


class TestSourceObj(ObjectMethods):
    """Test source object."""

    def test_definition(self):
        """Test function definition."""
        SourceObj('S', s_xyz)

    def test_preview(self):
        """Test function preview."""
        s_obj.preview(show=False, axis=False)

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

    def test_get_camera(self):
        """Test function source_camera."""
        s_obj._get_camera()

    def test_builtin_methods(self):
        """Test function source_builtin_methods."""
        assert len(s_obj) == n_sources
        _xyz = s_obj.xyz
        for i, k in enumerate(s_obj):  # loop over visible sources
            assert np.array_equal(k, _xyz[[i], :])
        assert len(s_obj + s_obj) == 2 * n_sources
        repr(s_obj)
        assert str(s_obj) == 'S1'

    def test_analyse(self):
        """Test function source_analyse."""
        s_obj.analyse_sources()
        s_obj.analyse_sources(roi_obj=['brodmann', 'all', 'talairach'])

    def test_analyse_color(self):
        """Test function source_analyse_color."""
        df = s_obj.analyse_sources()
        s_obj.color_sources(df, 'brodmann')  # random color
        s_obj.color_sources(df, 'matter',  # predefined colors
                            roi_to_color={'White': 'red', 'Gray': 'green'})

    def test_select(self):
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
        # Simple vertices :
        s_obj.project_modulation(vertices, 20.)
        s_obj.project_repartition(vertices, 20., contribute=True)
        s_obj.get_masked_index(vertices, 20.)
        # Indexed faces :
        s_obj.project_modulation(vertices_x3, 20.)
        s_obj.project_repartition(vertices_x3, 20., contribute=True)
        s_obj.get_masked_index(vertices_x3, 20.)


class TestCombineSources(ObjectMethods):
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


###############################################################################
###############################################################################
#                              CONNECTIVITY
###############################################################################
###############################################################################


class TestConnectObj(ObjectMethods):
    """Test connectivity object."""

    def test_definition(self):
        """Test function definition."""
        ConnectObj('C1', nodes, edges)
        ConnectObj('C1', nodes, edges, dynamic=(.1, .4))
        ConnectObj('C2', nodes, edges, custom_colors=custom_colors)

    def test_preview(self):
        """Test function preview."""
        c_obj.preview(show=False, axis=False)

    def test_builtin_methods(self):
        """Test function connect_builtin_methods."""
        custom_colors[None] = 'blue'
        ConnectObj('C2', nodes, edges, custom_colors=custom_colors)
        assert len(c_obj) == n_sources

    def test_get_camera(self):
        """Test function connect_camera."""
        c_obj._get_camera()

    def test_attributes(self):
        """Test function connect_attributes."""
        self._assert_and_test('c_obj', 'line_width', 4.4)
        self._assert_and_test('c_obj', 'color_by', 'strength')
        self._assert_and_test('c_obj', 'dynamic', (.2, .4))
        self._assert_and_test('c_obj', 'alpha', 0.7)


class TestCombineConnect(ObjectMethods):
    """Test combine conectivity objects."""

    def test_definition(self):
        """Test object definition."""
        CombineConnect(c_obj)
        CombineConnect([c_obj, c_obj2])


###############################################################################
###############################################################################
#                                  PICTURES
###############################################################################
###############################################################################


class TestPictureObj(ObjectMethods):
    """Test picture object."""

    def test_definition(self):
        """Test function definition."""
        PictureObj('P1', pic_data, pic_xyz, select=pic_select)

    def test_preview(self):
        """Test function preview."""
        p_obj.preview(show=False, axis=False)

    def test_builtin_methods(self):
        """Test function connect_builtin_methods."""
        assert len(p_obj) == n_sources

    def test_get_camera(self):
        """Test function connect_camera."""
        p_obj._get_camera()

    def test_attributes(self):
        """Test function connect_attributes."""
        self._assert_and_test('p_obj', 'width', 4.4)
        self._assert_and_test('p_obj', 'height', 1.4)
        self._assert_and_test('p_obj', 'translate', (1., 2., 3.))
        self._assert_and_test('p_obj', 'alpha', 0.4)


class TestCombinePictures(ObjectMethods):
    """Test combine picture objects."""

    def test_definition(self):
        """Test object definition."""
        CombinePictures([p_obj, p_obj])
        CombinePictures(p_obj)


###############################################################################
###############################################################################
#                              TIME-SERIES
###############################################################################
###############################################################################

class TestTimeSeriesObj(ObjectMethods):
    """Test time-series."""

    def test_definition(self):
        """Test function definition."""
        TimeSeriesObj('TS1', ts_data, ts_xyz)

    def test_preview(self):
        """Test function preview."""
        ts_obj.preview(show=False, axis=False)

    def test_builtin_methods(self):
        """Test function builtin_methods."""
        assert len(ts_obj) == n_sources

    def test_get_camera(self):
        """Test function connect_camera."""
        ts_obj._get_camera()

    def test_attributes(self):
        """Test function attributes."""
        self._assert_and_test('ts_obj', 'width', 4.)
        self._assert_and_test('ts_obj', 'amplitude', 4.)
        self._assert_and_test('ts_obj', 'color', [0.] * 4)
        self._assert_and_test('ts_obj', 'alpha', .7)
        self._assert_and_test('ts_obj', 'translate', (1., 2., 3.))
        self._assert_and_test('ts_obj', 'line_width', 1.4)


class TestCombineTimeSeries(ObjectMethods):
    """Test combine time-series."""

    def test_definition(self):
        """Test function definition."""
        CombineTimeSeries(ts_obj)
        CombineTimeSeries([ts_obj, ts_obj])


###############################################################################
###############################################################################
#                              BRAIN
###############################################################################
###############################################################################


class TestBrainObj(ObjectMethods):
    """Test brain object."""

    def test_definition(self):
        """Test function definition."""
        BrainObj('B1')
        # Test default templates :
        for k, i in zip(['B1', 'B2', 'B3'], ['left', 'both', 'right']):
            b_obj.set_data(name=k, hemisphere=i)
        # Test downloadable templates :
        for k in ['Inflated', 'WhiteMatter', 'Sphere']:
            b_obj.set_data(k)
        # Test custom (vertices, faces) :
        b_obj.set_data(name='UserBrain', vertices=vertices, faces=faces)

    def test_preview(self):
        """Test function preview."""
        b_obj.preview(show=False, axis=False)

    def test_get_camera(self):
        """Test function get_camera."""
        b_obj._get_camera()
        b_obj.reset_camera()

    def test_rotation(self):
        """Test function rotation."""
        # Test fixed rotations :
        f_rot = ['sagittal_0', 'left', 'sagittal_1', 'right', 'coronal_0',
                 'front', 'coronal_1', 'back', 'axial_0', 'top', 'axial_1',
                 'bottom']
        for k in f_rot:
            b_obj.rotate(k)
        # Test custom rotation :
        for k in [(0, 90), (170, 21), (45, 65)]:
            b_obj.rotate(custom=k)

    def test_attributes(self):
        """Test function attributes."""
        self._assert_and_test('b_obj', 'translucent', True)
        self._assert_and_test('b_obj', 'alpha', .4)
        assert b_obj.camera is not None
        assert isinstance(b_obj.vertices, np.ndarray)
