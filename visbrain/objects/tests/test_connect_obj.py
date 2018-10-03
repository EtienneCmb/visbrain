"""Test ConnectObj."""
import numpy as np

from visbrain.objects.connect_obj import ConnectObj, CombineConnect
from visbrain.objects.tests._testing_objects import _TestObjects


n_sources = 20
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


class TestConnectObj(_TestObjects):
    """Test connectivity object."""

    OBJ = c_obj

    def test_definition(self):
        """Test function definition."""
        ConnectObj('C1', nodes, edges)
        ConnectObj('C1', nodes, edges, dynamic=(.1, .4))
        ConnectObj('C2', nodes, edges, custom_colors=custom_colors)

    def test_get_nb_connections_per_node(self):
        """Test function get_nb_connections_per_node."""
        sort = ['index', 'count']
        order = ['ascending', 'descending']
        for s in sort:
            for o in order:
                c_obj.get_nb_connections_per_node(s, o)

    def test_analyse_connections(self):
        """Test function analyse_connections."""
        c_obj.analyse_connections(get_centroids=True)

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
        self.assert_and_test('line_width', 4.4)
        self.assert_and_test('color_by', 'strength')
        self.assert_and_test('color_by', 'count')
        self.assert_and_test('color_by', 'causal')
        self.assert_and_test('dynamic', (.2, .4))
        self.assert_and_test('alpha', 0.7)


class TestCombineConnect(object):
    """Test combine conectivity objects."""

    def test_definition(self):
        """Test object definition."""
        CombineConnect(c_obj)
        CombineConnect([c_obj, c_obj2])
