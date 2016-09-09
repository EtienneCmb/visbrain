import sys
import numpy as np
from itertools import product
from collections import Counter

from vispy import app, gloo, visuals, scene
from visbrain.utils import array2colormap, normalize




vertex_shader = """
varying vec4 v_color;
void main()
{
    v_color = $a_color;
    gl_Position = $transform(vec4($a_position, 1));
}
"""

fragment_shader = """
varying vec4 v_color;
void main() {
    gl_FragColor = v_color;
}
"""


class ConnectVisual(visuals.Visual):
    """Template
    """

    def __init__(self, pos, connect, select=None, colorby='strength', dynamic=False,
                 cmap='viridis'):

        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        # Save variables :
        self.pos = pos
        self.connect = connect
        self.select = select
        self.colorby = colorby
        self.dynamic = dynamic
        self.cmap = cmap

        # Create elements :
        self._run()

        # bind data
        self._draw_mode = 'lines'
        self.set_gl_state('translucent', depth_test=True, cull_face=False, blend=True, 
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def __iter__(self):
        for k, i, j in zip(*self._loopIndex):
            yield k, i, j


    def _prepare_transforms(self, view):
        """ This method is called when the user or the scenegraph has assigned
        new transforms to this visual """
        tr = view.transforms
        view_vert = view.view_program.vert
        view_frag = view.view_program.frag
        view_vert['transform'] = tr.get_transform()


    def _prepare_inputs(self):
        """Prepare inputs
        """
        self._check_position(self.pos)
        self._check_data(self.connect, self.select)
        self._check_color(self.colorby, self.cmap, self.dynamic)


    def _check_position(self, pos):
        """Check if position is type float32
        """
        if pos.shape[1] != 3:
            raise ValueError('Position must be an Nx3 matrix')
        self.pos = pos.astype(np.float32)


    def _check_data(self, connect, select):
        """
        """
        # Check connect :
        if connect.shape != tuple([self.pos.shape[0]]*2):
            raise ValueError("The c_connect matrix must be squared")
        else:
            self.connect = connect.astype(np.float32)

        # Check select :
        if select is None:
            # Upper triangle matrix
            select = np.tri(self.pos.shape[0], k=-1, dtype=int).T
        elif select.shape != tuple([self.pos.shape[0]]*2):
            raise ValueError("The c_select matrix must be squared")
        else:
            self.select = select.astype(int)


    def _check_color(self, colorby, cmap, dynamic):
        """
        """
        # Check colorby :
        if self.colorby not in ['count', 'strength']:
            raise ValueError("The colorby parameter must be 'count' or 'strength'")
        # Test colormap :
        array2colormap(np.array([0, 1]), cmap=cmap)
        # Test dynamic :
        if not isinstance(dynamic, bool):
            raise ValueError("dynamic bust be an instance of type bool")


    def _non_zero_select(self):
        """Find non zeros indices and connection values
        """
        self._nnz_x, self._nnz_y = np.nonzero(self.select)
        self._indices = np.c_[self._nnz_x, self._nnz_y].flatten()
        self._Nindices = np.arange(len(self._indices))


    def set_position(self, pos):
        """
        """
        # Check pos :
        self._check_position(pos)
        # Set and update pos :
        self.a_position = np.zeros((2*len(self._nnz_x), 3), dtype=np.float32)
        for j, k, l in self:
            self.a_position[j, :] = self.pos[k, :]
        self.update_position()


    def set_data(self, connect, select=None):
        """
        """
        # Check data :
        self._check_data(connect, select)
        # Find non-zero elements :
        self._non_zero_select()
        # Update data :
        self.set_color(colorby=self.colorby, cmap=self.cmap, dynamic=self.dynamic)
        # Update position :
        self.set_position(self.pos)



    def set_color(self, colorby='strength', cmap='viridis', dynamic=False):
        """
        """
        # Check color elements :
        self._check_color(colorby, cmap, dynamic)

        # Colorby strength of connection :
        if colorby == 'strength':
            # Get non-zeros-values :
            nnz_values = self.connect[self._nnz_x, self._nnz_y]
            # Concatenate in alternance all non-zero values :
            all_nnz = np.c_[nnz_values, nnz_values].flatten()
            # Get looping indices :
            self._loopIndex = (self._Nindices, self._indices, self._Nindices)

        # Colorby count on each node :
        elif colorby == 'count':
            # Count the number of occurence for each node :
            node_count = Counter(np.ravel([self._nnz_x, self._nnz_y]))
            all_nnz = np.array([node_count[k] for k in self._indices])
            # Get looping indices :
            self._loopIndex = (self._Nindices, self._indices, self._indices)

        # Get associated colormap :
        colormap = array2colormap(all_nnz, cmap=cmap)

        # Dynamic alpha :
        if dynamic:
            colormap[:, 3] = normalize(all_nnz, tomax=1)

        # Build a_color and send to buffer :
        self.a_color = np.zeros((2*len(self._nnz_x), 4), dtype=np.float32)
        for j, k, l in self:
            self.a_color[j, :] = colormap[l, :]
        self.update_color()


    def update_color(self):
        """
        """
        self.shared_program.vert['a_color'] = gloo.VertexBuffer(self.a_color.astype(np.float32))

    def update_position(self):
        """
        """
        self.shared_program.vert['a_position'] = gloo.VertexBuffer(self.a_position.astype(np.float32))


    def set_opacity(self, alpha=1.0):
        """
        """
        N = self.a_color.shape[0]
        if isinstance(alpha, (int, float)):
            alpha_vec = np.full((N,), alpha)
        elif isinstance(alpha, np.ndarray) and (len(alpha) != N):
            raise ValueError("The length of alpha must be "+str(N))
        else:
            alpha_vec = alpha.ravel()
        self.a_color[:, 3] = alpha_vec
        self.update_color()


    def get_position(self):
        """
        """
        return self.shared_program.vert['a_position']


    def get_color(self):
        """
        """
        return self.shared_program.vert['a_color']

    def _run(self):
        """
        """
        # Set position/data/color :
        self.set_data(self.connect, self.select)
        self.set_position(self.pos)



















# build your visuals, that's all
Connect3D = scene.visuals.create_visual_node(ConnectVisual)

# The real-things : plot using scene
# build canvas
canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='w')
canvas.context.set_line_width(5)

# Add a ViewBox to let the user zoom/rotate
view = canvas.central_widget.add_view()
view.camera = 'turntable'
view.camera.fov = 50
view.camera.distance = 5

# data
N = 50
pos = np.random.rand(N, 3)
connect = np.random.uniform(-10, 10, size=(N, N))
# connect[(connect < 8)] = 0
# print(np.nonzero(connect))
# print(connect)
# pos = np.array([[-1, 0, 0], [1, 0, 0], [1, 1, 0], [-1, 1, 0]], dtype=np.float32)
# connect = np.array([[0, 12, 7, 0], [0, 0, 4, 0], [0, 0, 0, 7], [0, 0, 0, 0]])

# plot ! note the parent parameter
p1 = Connect3D(pos, connect, select=connect.copy(), dynamic=True, parent=view.scene,
               colorby='count', cmap='viridis')

@canvas.events.mouse_double_click.connect
def on_mouse_double_click(event):
    # pos = np.random.rand(N, 3).astype(np.float32)
    # connect = np.random.uniform(-10, 10, size=(N, N))
    # connect[(connect < 5)] = 0
    # p1.set_data(connect=connect, select=connect.copy())
    # p1.set_position(pos)
    p1.set_opacity(np.array([0,1]))
    canvas.update()

# run
if __name__ == '__main__':
    if sys.flags.interactive != 1:
        app.run()