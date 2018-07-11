"""Visual class for 3-D pictures.

Authors: Etienne Combrisson <e.combrisson@gmail.com>

License: BSD (3-clause)
"""
import numpy as np

from vispy import gloo, visuals, scene

from ..utils import cmap_to_glsl, vispy_array

__all__ = ('PicMesh')

VERT_SHADER = """
#version 120

varying vec4 v_color;
varying float v_data;

void main() {
    v_data = $a_data;
    v_color = $color;
    gl_Position = $transform(vec4($a_position, 1.));
}
"""

FRAG_SHADER = """
#version 120

varying vec4 v_color;

void main() {
    gl_FragColor = vec4(v_color.rgb, $u_alpha);
}
"""


class PicVisual(visuals.Visual):
    """Create a VisPy compatible object for multiple small pictures."""

    def __len__(self):
        """Return the number of sources."""
        return self.n

    def __init__(self, data, pos, width=1., height=1., dxyz=(0., 0., 0.,),
                 select=None, alpha=1., **kwargs):
        """Init."""
        # self.unfreeze()
        self.w = width
        self.h = height
        self._pos = pos
        self._dxyz = np.array(dxyz)
        self.camera = []

        visuals.Visual.__init__(self, VERT_SHADER, FRAG_SHADER)

        # Select pictures :
        if isinstance(select, (list, np.ndarray)):
            data = data[select, ...]
            pos = pos[select, ...]

        # Check data and get vertices and faces :
        self._check_data(data, pos)

        # Get vertices and faces :
        a_position = self._data_to_pos(pos)
        faces, grid = self._get_index()

        # Define index and position buffers :
        self._index_buffer = gloo.IndexBuffer(faces)
        self._pos_buffer = gloo.VertexBuffer(a_position)
        self.shared_program.vert['a_position'] = self._pos_buffer

        # Re-order data :
        self._data = data.ravel()[np.argsort(grid.ravel())]
        self._data_buffer = gloo.VertexBuffer(vispy_array(self._data))
        self.shared_program.vert['a_data'] = self._data_buffer
        # Define the color buffer :
        self.shared_program.frag['u_alpha'] = alpha
        self.alpha = alpha
        self.set_data(**kwargs)

        # Define drawing mode :
        self._draw_mode = 'triangles'

    def _prepare_transforms(self, view):
        """Prepare transformation."""
        tr = view.transforms
        transform = tr.get_transform()

        view_vert = view.view_program.vert
        view_vert['transform'] = transform

    def _check_data(self, data, pos):
        """Check data and position.

        Parameters
        ----------
        data : array_like
            Array of data of shape (n_sources, n_rows, n_cols). If data has
            4 dims, the last one is considered as RGBA.

        pos : array_like
            Position of each center of shape (n_centers, 3).
        """
        # Check position :
        if pos.ndim != 2:
            raise ValueError("The pos variable must be (n_sources, 3)")
        self.n = pos.shape[0]
        # Check data :
        if (data.shape[0] != len(self)) or (data.ndim < 3):
            raise ValueError("The data variable must be (n_sources, n_rows, "
                             "ncols)")
        self.nrows = data.shape[1]
        self.ncols = data.shape[2]

    def _data_to_pos(self, pos):
        """Convert pos into a compatible grid of positions.

        Parameters
        ----------
        pos : array_like
            Position of each center of shape (n_centers, 3).

        Returns
        -------
        grid : array_like
            The grid of positions of shape (n_centers * n_rows * n_cols, 3).
        """
        grid = np.zeros((self.n, self.ncols, self.nrows, 3), dtype=np.float32)
        # Build (starting, ending) indices :
        xg, yg = np.mgrid[-self.w / 2:self.w / 2:self.ncols * 1j,
                          -self.h / 2:self.h / 2:self.nrows * 1j]
        xg = np.flipud(xg)
        for k in range(self.n):
            grid[k, :, :, 0] = pos[k, 0] + xg + self._dxyz[0]
            grid[k, :, :, 1] = pos[k, 1] + yg + self._dxyz[1]
            grid[k, :, :, 2] = pos[k, 2] + self._dxyz[2]
        return grid.reshape(self.n * self.nrows * self.ncols, 3)

    def _get_index(self):
        """Build the index of triangles.

        Returns
        -------
        index : array_like
            Array of indices for the triangles of shape
            (n_centers * 2 * (n_rows - 1) * (n_cols - 1), 3)
        select : array_like
            Array to select data in the correct order with the same shape as
            the index array.
        """
        # Build the default grid of index :
        nr, nc = self.nrows, self.ncols
        g = np.arange(nr * nc).reshape(nc, nr)
        g = np.fliplr(g.T)  # np.fliplr(np.flipud(g.T))
        # Build indices for one map :
        index = np.zeros((2 * (nr - 1) * (nc - 1), 3))
        q = 0
        for k in range(nc - 1, 0, -1):
            for i in range(nr - 1, 0, -1):
                index[q, :] = [g[i, k], g[i - 1, k], g[i, k - 1]]
                index[q + 1, :] = [g[i - 1, k], g[i, k - 1], g[i - 1, k - 1]]
                q += 2
        # Repeat indices for each map :
        select = np.zeros((self.n, nr, nc), dtype=int)
        l = index.shape[0]  # noqa
        idx = np.zeros((self.n * l, 3), dtype=np.uint32)
        for k in range(self.n):
            idx[k * l:(k + 1) * l, :] = index + k * (nr * nc)
            select[k, ...] = g + k * (nr * nc)
        return idx, select

    def set_data(self, width=None, height=None, dxyz=None, **kwargs):
        """Convert data into a compatible colormap.

        Parameters
        ----------
        kwargs : dict | {}
            Optional args passed to the array2colormap function.

        Returns
        -------
        cmap : array_like
            The colormap of shape (n_sources, n_rows, n_cols, RGBA).
        """
        # Update width/heigth :
        needupdate = False
        if width is not None:
            self.w = width
            needupdate = True
        if height is not None:
            self.h = height
            needupdate = True
        if dxyz is not None:
            self._dxyz = np.array(dxyz)
            needupdate = True
        if needupdate:
            a_position = self._data_to_pos(self._pos)
            self._pos_buffer.set_data(a_position)
        # Update color properties :
        _limits = (self._data.min(), self._data.max())
        cmap = cmap_to_glsl(limits=_limits, **kwargs)
        self.shared_program['texture2D_LUT'] = cmap.texture_lut()
        fcn_color = visuals.shaders.Function(cmap.glsl_map)
        self.shared_program.vert['color'] = fcn_color('v_data')
        self.update()

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Set alpha value."""
        self.shared_program.frag['u_alpha'] = value
        self._alpha = value
        self.update()


# Auto-generate a Visual+Node class for use in the scenegraph.
PicMesh = scene.visuals.create_visual_node(PicVisual)
