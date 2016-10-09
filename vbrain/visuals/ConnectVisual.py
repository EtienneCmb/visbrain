import numpy as np
from collections import Counter

from vispy import app, gloo, visuals, scene
from ..utils import array2colormap, normalize


__all__ = ['ConnectVisual']


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

    def __init__(self, pos, connect, select=None, colorby='strength', dynamic=None,
                 cmap='viridis', vmin=None, vmax=None, under=None, over=None):

        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        # Save variables :
        self.pos = pos
        self.connect = connect
        self.select = select
        self.colorby = colorby
        self.dynamic = dynamic
        self._cmap = cmap
        self._vmin, self._vmax = vmin, vmax
        self._under, self._over = under, over

        # Create elements :
        self.set_data(self.connect, self.select)

        # bind data
        self._draw_mode = 'lines'
        # self.set_gl_state('translucent', depth_test=False, cull_face=False)



    def _prepare_transforms(self, view):
        """This method is called when the user or the scenegraph has assigned
        new transforms to this visual
        """
        tr = view.transforms
        view_vert = view.view_program.vert
        view_frag = view.view_program.frag
        view_vert['transform'] = tr.get_transform()


    def _check_position(self, pos):
        """Check if position is type float32
        """
        if pos.shape[1] != 3:
            raise ValueError('Position must be an Nx3 matrix')
        self.pos = pos.astype(np.float32)


    def _check_data(self, connect, select):
        """
        """
        N = self.pos.shape[0]
        # Chech array :
        if (connect.shape != (N, N)) or not isinstance(connect, np.ndarray):
            raise ValueError('c_connect must be an array of shape '+str((N, N)))
        if select is None:
            select = np.ones_like(connect)
        if (select.shape != (N, N) or not isinstance(select, np.ndarray)):
            raise ValueError('c_select must be an array of shape '+str((N, N)))
        # Mask c_connect :
        try:
            connect.mask
        except:
            connect = np.ma.masked_array(connect, mask=True)
        connect.mask[select.nonzero()] = False
        self.connect = connect


    def _check_color(self, colorby, cmap, dynamic):
        """
        """
        # Check colorby :
        if self.colorby not in ['count', 'strength']:
            raise ValueError("The colorby parameter must be 'count' or 'strength'")
        # Test dynamic :
        if (dynamic is not None) and not isinstance(dynamic, tuple):
            raise ValueError("dynamic bust be a tuple")


    def _non_zero_select(self):
        """Find non zeros indices and connection values
        """
        self._nnz_x, self._nnz_y = np.where(~self.connect.mask)
        self._indices = np.c_[self._nnz_x, self._nnz_y].flatten()
        self._Nindices = np.arange(len(self._indices))


    def set_position(self, pos):
        """
        """
        # Check pos :
        self._check_position(pos)
        # Set and update pos :
        self.a_position = np.zeros((2*len(self._nnz_x), 3), dtype=np.float32)
        self.a_position[self._Nindices, :] = self.pos[self._indices, :]
        self.update_position()


    def set_data(self, connect, select=None):
        """
        """
        # Check data :
        self._check_data(connect, select)
        # Find non-zero elements :
        self._non_zero_select()
        # Update data :
        self.set_color(colorby=self.colorby, dynamic=self.dynamic, cmap=self._cmap, vmin=self._vmin,
                       vmax=self._vmax, under=self._under, over=self._over)
        # Update position :
        self.set_position(self.pos)



    def set_color(self, colorby='strength', dynamic=False, cmap='viridis', vmin=None,
                  vmax=None, under=None, over=None):
        """
        """
        # Check color elements :
        self._check_color(colorby, cmap, dynamic)

        # Colorby strength of connection :
        if colorby == 'strength':
            # Get non-zeros-values :
            nnz_values = self.connect.compressed()
            # Concatenate in alternance all non-zero values :
            self._all_nnz = np.c_[nnz_values, nnz_values].flatten()
            # Get looping indices :
            self._loopIndex = self._Nindices

        # Colorby count on each node :
        elif colorby == 'count':
            # Count the number of occurence for each node :
            node_count = Counter(np.ravel([self._nnz_x, self._nnz_y]))
            self._all_nnz = np.array([node_count[k] for k in self._indices])
            # Get looping indices :
            self._loopIndex = self._Nindices

        # Get associated colormap :
        colormap = array2colormap(self._all_nnz, cmap=cmap, vmin=vmin, vmax=vmax, under=under, over=over)

        # Dynamic alpha :
        if (dynamic is not False) and isinstance(dynamic, tuple):
            colormap[:, 3] = normalize(self._all_nnz, tomin=dynamic[0], tomax=dynamic[1])

        # Build a_color and send to buffer :
        self.a_color = np.zeros((2*len(self._nnz_x), 4), dtype=np.float32)
        self.a_color[self._Nindices, :] = colormap[self._loopIndex, :]
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





# build your visuals, that's all
# Connect3D = scene.visuals.create_visual_node(ConnectVisual)

