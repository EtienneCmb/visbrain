"""Display signals into a grid..

A large portion of this code was taken from the example developped by the vispy
team :
https://github.com/vispy/vispy/blob/master/examples/demo/gloo/realtime_signals.py
"""
import numpy as np
from itertools import product

from vispy import gloo, visuals
from vispy.scene.visuals import create_visual_node, Text

from visbrain.utils import color2vb, vispy_array, PrepareData, ndsubplot


__all__ = ('GridSignal')


vertex_shader = """
#version 120
varying vec3 v_index;
// Varying variables used for clipping in the fragment shader.
varying vec2 v_position;
varying vec4 v_ab;
varying vec3 a_pos;
void main() {
    float nrows = $u_size.x;
    float ncols = $u_size.y;

    // Compute the x coordinate from the time index.
    float x = -1 + 2*$a_index.z / ($u_n-1);

    // Turn position into a vec3 :
    a_pos = vec3($a_position, 1, 1);
    vec2 position = vec2(x - (1 - 1 / $u_scale.x), a_pos);

    // Find the affine transformation for the subplots.
    vec2 a = vec2(1./ncols, 1./nrows)*.98;
    vec2 b = vec2(-1 + $u_space*($a_index.x+.5) / ncols,
                  -1 + $u_space*($a_index.y+.5) / nrows);

    // Apply the static subplot transformation + scaling.
    gl_Position = $transform(vec4(a*$u_scale*position+b, 0.0, 1.0));

    // For clipping test in the fragment shader.
    v_index = $a_index;
    v_position = gl_Position.xy;
}
"""

fragment_shader = """
#version 120
varying vec4 u_color;
varying vec3 v_index;
varying vec2 v_position;
void main() {
    gl_FragColor = vec4($u_color);

    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        discard;
}
"""


class GridSignalVisual(visuals.Visual):
    """Visual class for grid of signals.

    Parameters
    ----------
    data : array_like
        Array of data. Could be 1-D, 2-D or 3-D.
    axis : int | -1
        Time axis location.
    sf : float | 1.
        The sampling frequency (used for filtering).
    random : array_like/string/tuple | 'random'
        Use 'random' for random colors or a color name for uniform color.
    space : float | 2.
        Space between subplots.
    scale : tuple | (1., 1.)
        Tuple describing the scaling along the x and y-axis.
    font_size : float | 10.
        Title font size.
    width : float | 1.
        Line width.
    method : {'gl', 'agg'}
        Plotting method. 'gl' is faster but 'agg' should be antialiased.
    force_shape : tuple | None
        Force the shape of data. Should be a tuple of two ints.
    plt_as : {'grid', 'row', 'col'}
        Plotting type.
    """

    def __len__(self):
        """Return the number of time points."""
        return self._n

    def __init__(self, data, axis=-1, sf=1., color='white', title=None,
                 title_color='white', title_bold=False, space=2.,
                 scale=(1., 1.), font_size=10., width=1., method='gl',
                 force_shape=None, plt_as='grid'):
        """Init."""
        # =========================== CHECKING ===========================
        assert isinstance(data, np.ndarray) and (data.ndim <= 3)
        assert isinstance(axis, int)
        assert isinstance(sf, (int, float))
        assert isinstance(space, (int, float))
        assert isinstance(scale, (tuple, list)) and len(scale) == 2

        # =========================== VISUALS ===========================
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        self.set_gl_state('translucent', depth_test=True, cull_face=False,
                          blend=True, blend_func=('src_alpha',
                                                  'one_minus_src_alpha'))
        self._draw_mode = 'line_strip'
        self._txt = Text(bold=title_bold, font_size=font_size,
                         color=title_color)

        # =========================== DATA ===========================
        # Keep some inputs :
        self._sh = data.shape
        self._n = self._sh[axis]
        self._axis = axis
        self._sf = sf
        self._color = color
        self.scale = scale
        self.space = space
        self._prep = PrepareData(axis=-1)
        self.width = width
        self.method = method
        assert plt_as in ['grid', 'row', 'col'], ("`plt_as` should either be "
                                                  "'grid', 'row' or 'col'")
        self._plt_as = plt_as

        # =========================== BUFFERS ===========================
        # Create buffers (for data, index and color)
        rnd_1 = np.zeros((3,), dtype=np.float32)
        rnd_3 = np.zeros((1, 3), dtype=np.float32)
        self._dbuffer = gloo.VertexBuffer(rnd_1)
        self._ibuffer = gloo.VertexBuffer(rnd_3)
        # Send to the program :
        self.shared_program.vert['a_position'] = self._dbuffer
        self.shared_program.vert['a_index'] = self._ibuffer
        self.shared_program.vert['u_size'] = (1, 1)
        self.shared_program.vert['u_n'] = len(self)

        # Set data :
        self.set_data(data, axis, color, title, force_shape, plt_as)
        self.freeze()

    def set_data(self, data=None, axis=None, color=None, title=None,
                 force_shape=None, plt_as='grid'):
        """Set data to the grid of signals.

        Parameters
        ----------
        data : None
            Array of data. Could be 1-D, 2-D or 3-D.
        axis : int | None
            Time axis location.
        random : array_like/string/tuple | 'random'
            Use 'random' for random colors or a color name for uniform color.
        """
        # ====================== CHECKING ======================
        # Axis :
        axis = axis if isinstance(axis, int) else self._axis
        axis = len(self._sh) - 1 if axis == -1 else axis
        # Data :
        if isinstance(data, np.ndarray):
            # -------------- (n_rows, n_cols, n_time) --------------
            if data.ndim == 1:  # 1-D array
                data = data.reshape(1, 1, -1)
                g_size = (1, 1)
            elif data.ndim == 2:  # 2-D array
                if axis == 0:  # data need to be transposed
                    data = np.swapaxes(data, 0, 1)
                    axis = 1
                g_size = (data.shape[0], 1)  # (n_row, 1)
                data = data[np.newaxis, ...]
            elif data.ndim == 3:  # 3-D array
                if axis != data.ndim - 1:  # data need to be transposed
                    data = np.swapaxes(data, axis, -1)
                    axis = data.ndim - 1
                g_size = (data.shape[0], data.shape[1])

            # -------------- Signals index --------------
            m = np.prod(list(data.shape)[0:-1])
            sig_index = np.arange(m).reshape(*g_size)

            # -------------- Plot type --------------
            if plt_as == 'row':
                force_shape = (1, g_size[0] * g_size[1])
            elif plt_as == 'col':
                force_shape = (g_size[0] * g_size[1], 1)

            # -------------- Optimal 2-D --------------
            self._data = data
            self._ori_shape = list(data.shape)[0:-1]
            if force_shape is None:
                n_rows, n_cols = ndsubplot(m)
            elif len(g_size) == 2:
                n_rows, n_cols = force_shape
            data = data.reshape(n_rows, n_cols, len(self))
            sig_index = sig_index.reshape(n_rows, n_cols)
            g_size = (n_rows, n_cols)
            self._opt_shape = list(data.shape)[0:-1]
            self._sig_index = sig_index

            # -------------- (n_rows * n_cols, n_time) --------------
            data = np.reshape(data, (m, len(self)), order='F')

            # -------------- Prepare --------------
            # Force demean / detrend of _prep :
            self._prep.demean, self._prep.detrend = False, False
            data = self._prep._prepare_data(self._sf, data, 0)
            # Demean and normalize :
            kw = {'axis': -1, 'keepdims': True}
            dmax = np.abs(data).max(**kw)
            dmax[dmax == 0.] = 1.
            data -= data.mean(**kw)
            data /= dmax
            # data /= data.max()
            self._dbuffer.set_data(vispy_array(data))
            self.g_size = g_size

        # ====================== INDEX ======================
        n, m = len(self), np.prod(g_size)
        self._sig_index = self._sig_index.reshape(n_rows, n_cols)
        idg = np.c_[np.repeat(np.repeat(np.arange(n_cols), n_rows), n),
                    np.repeat(np.tile(np.arange(n_rows), n_cols), n)[::-1],
                    np.tile(np.arange(n), m)].astype(np.float32)
        self._ibuffer.set_data(vispy_array(idg))

        # ====================== COLOR ======================
        if color is not None:
            color_1d = color2vb(color)
            self.shared_program.frag['u_color'] = color_1d.ravel()

        # ====================== TITLES ======================
        # Titles checking :
        if title is None or (len(title) != m):
            st, it = '({}, {})', product(range(n_rows), range(n_cols))
            title = [st.format(i, k) for i, k in it]
        # Set text and font size :
        if not self._txt.text:
            self._txt.text = title
        # Get titles position :
        x_factor, y_factor = 1. / n_cols, 1. / n_rows
        r_x = np.linspace(-1. + x_factor, 1. - x_factor, n_cols)
        r_x = np.tile(r_x, n_rows)
        r_y = np.linspace(-1. + y_factor, 1. - y_factor, n_rows)[::-1]
        r_y += y_factor
        r_y = np.repeat(r_y, n_cols)
        pos = np.c_[r_x, r_y, np.full_like(r_x, -10.)]
        self._txt.pos = pos.astype(np.float32)

    def clean(self):
        """Clean buffers."""
        self._dbuffer.delete()
        self._ibuffer.delete()

    def _convert_row_cols(self, row, col):
        """Convert row and col according to the optimal grid."""
        try:
            index = self._sig_index[row, col]
            idx = np.where(self._sig_index.reshape(*self._ori_shape) == index)
            return idx[0][0], idx[1][0]
        except:
            return row, col

    def _prepare_transforms(self, view):
        """Call for the first rendering."""
        tr = view.transforms
        view_vert = view.view_program.vert
        view_vert['transform'] = tr.get_transform()

    def _prepare_draw(self, view=None):
        """Function called everytime there's a camera update."""
        try:
            import OpenGL.GL as GL
            GL.glLineWidth(self._width)
            if self._smooth_line:
                GL.glEnable(GL.GL_LINE_SMOOTH)
            else:
                GL.glDisable(GL.GL_LINE_SMOOTH)
        except Exception:  # can be other than ImportError sometimes
            pass

    # ========================================================================
    # ========================================================================
    # PROPERTIES
    # ========================================================================
    # ========================================================================
    # ----------- SCALE -----------
    @property
    def scale(self):
        """Get the scale value."""
        return self._scale

    @scale.setter
    def scale(self, value):
        """Set scale value."""
        if isinstance(value, tuple):
            self._uscale = value
            self._scale = value
            self.shared_program.vert['u_scale'] = value
            self.update()

    # ----------- SPACE -----------
    @property
    def space(self):
        """Get the space value."""
        return self._space

    @space.setter
    def space(self, value):
        """Set space value."""
        if isinstance(value, float):
            self._space = value
            self.shared_program.vert['u_space'] = value
            self.update()

    # ----------- RECT -----------
    @property
    def rect(self):
        return (-1.05, -1.1, self._space + .1, self._space + .2)

    # ----------- FONT_SIZE -----------
    @property
    def font_size(self):
        """Get the font_size value."""
        return self._txt.font_size

    @font_size.setter
    def font_size(self, value):
        """Set font_size value."""
        self._txt.font_size = value

    # ----------- TCOLOR -----------
    @property
    def tcolor(self):
        """Get the tcolor value."""
        return self._txt.color

    @tcolor.setter
    def tcolor(self, value):
        """Set tcolor value."""
        self._txt.color = color2vb(value)

    # ----------- TVISIBLE -----------
    @property
    def tvisible(self):
        """Get the tvisible value."""
        return self._txt.visible

    @tvisible.setter
    def tvisible(self, value):
        """Set tvisible value."""
        self._txt.visible = value

    # ----------- G_SIZE -----------
    @property
    def g_size(self):
        """Get the g_size value."""
        return self._g_size

    @g_size.setter
    def g_size(self, value):
        """Set g_size value."""
        self._g_size = value
        self.shared_program.vert['u_size'] = value
        self.update()

    # ----------- WIDTH -----------
    @property
    def width(self):
        """Get the width value."""
        return self._width

    @width.setter
    def width(self, value):
        """Set width value."""
        self._width = value
        self.update()

    # ----------- METHOD -----------
    @property
    def method(self):
        """Get the method value."""
        return self._method

    @method.setter
    def method(self, value):
        """Set method value."""
        self._method = value
        self._smooth_line = value == 'agg'
        self.update()


GridSignal = create_visual_node(GridSignalVisual)
