"""Ndplot management.

A large portion of this code was taken from the example developped by the vispy
team :
https://github.com/vispy/vispy/blob/master/examples/demo/gloo/realtime_signals.py
"""

import numpy as np

from vispy import app, gloo, visuals
from vispy.scene.visuals import create_visual_node

from ..utils import ndsubplot, array2colormap, color2vb, id

from warnings import warn


__all__ = ('GridSignalMesh')


vertex_shader = """
#version 120
varying vec3 v_index;
varying vec4 v_color;
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
    vec2 a = vec2(1./ncols, 1./nrows)*.9;
    vec2 b = vec2(-1 + $u_space*($a_index.x+.5) / ncols,
                  -1 + $u_space*($a_index.y+.5) / nrows);
    // Apply the static subplot transformation + scaling.
    gl_Position = $transform(vec4(a*$u_scale*position+b, 0.0, 1.0));
    v_color = vec4($a_color, 1.);
    v_index = $a_index;
    // For clipping test in the fragment shader.
    v_position = gl_Position.xy;
}
"""

fragment_shader = """
#version 120
varying vec4 v_color;
varying vec3 v_index;
varying vec2 v_position;
void main() {
    gl_FragColor = v_color;

    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        discard;
}
"""


class GridSignalVisual(visuals.Visual):
    """Visual class of nd-signals visualization."""

    def __len__(self):
        """Return the number of time points."""
        return self.n

    def __getitem__(self, name):
        """Get an input item."""
        return self._kwargs[name]

    def __setitem__(self, name, value):
        """Set a input item."""
        self._kwargs[name] = value

    def __init__(self, *args, **kwargs):
        """Init."""
        # Define attributes :
        self._dim = [0, 0]
        self.nrows = 0
        self.ncols = 0
        self._minmax = (0., 1.)
        self.camera = []
        self._kwargs = {}

        # --------------------------------------------------------------------
        # Initialize the vispy.Visual class with the vertex / fragment buffer :
        # and OpenGL state :
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        self.set_gl_state('translucent', depth_test=True, cull_face=False,
                          blend=True, blend_func=('src_alpha',
                                                  'one_minus_src_alpha'))
        self.scale = (1., 1.)
        self.space = 1.
        self._draw_mode = 'line_strip'

        # --------------------------------------------------------------------
        # Set data :
        self.set_data(*args, **kwargs)

        # --------------------------------------------------------------------
        # Link the time the the on_time function :
        self._timer = app.Timer(1/self._sf, connect=self.on_timer,
                                start=False)

        self.freeze()

    # ========================================================================
    # ========================================================================
    # SET DATA
    # ========================================================================
    # ========================================================================
    def set_data(self, data, sf, axis=None, color='random', space=2.,
                 play=False, force_col=None, rnd_dyn=(.3, .9), demean=True,
                 cmap='viridis', clim=None, vmin=None, under='gray', vmax=None,
                 over='red', laps=1, scale=(1., 1.), unicolor='gray',
                 norm=True, **kwargs):
        """Set some new data to the already existing plot.

        Args:
            data: ndarray
                The data to plot. This class can handle 1D, 2D or 3D data.

            sf: float
                The sampling frequency

        Kargs:
            axis: tuple, optional, (def: None)
                Specify how the axis of your data have to be interpreted:

                    * 0: specify where is the time axis
                    * 1: specify where is the number of rows
                    * 2: specify where is the number of columns.

                If the data is a row vector,the axis parameter is not active.
                If the data is a 2D matrix, you have to specify the meaning of
                each axis (ex: data.shape=(20, 1000) and axis=(1, 0) mean that
                the second axis as the time dimension. Then, the 20 plots will
                be organized in a 10x2 grid). Finally, if the data is a 3D
                array, specify where are the time axis, the number of rows and
                columns. (ex: data.shape=(20, 1000, 10) and axis=(2, 0, 1) the
                program will display a grid of 10 rows x 20 columns, each plot
                having 1000 points).

            color: string/tuple/array, optional, (def: None)
                Choose how to color signals. Use None (or 'rnd', 'random') to
                generate random colors. Use 'uniform' (see the unicolor
                parameter) to define the same color for all signals. Use
                'dyn_time' to have a dynamic color according to the time index.
                This is particulary convenient to inspect real time signals
                (see play parameter). Use 'dyn_minmax' to a color code acording
                to the dynamic of the signal. This option can be used to detect
                extrema and can be futher controled using colormap parameters
                (cmap, clim, vmin, vmax, under and over).

            space: int, optional, (def: 2)
                The space between each plot. I recommand using a space >= 2.

            play: bool, optional, (def: False)
                Play the data. For a better interpretation, you should use the
                'dyn_time' option of the color parameter.

            force_col: int, optional, (def: None)
                Force the number of columns in the plot. In case of a 2D
                matrix, the program try to find the best grid organization.
                But if it failed, use this parameter to fix your own number of
                columns and the program will found the corresponding number of
                rows.

            rnd_dyn: tuple, optional, (def: (.3, .9))
                Define the dynamic of random color. This parameter is active
                only if the color parameter is turned to None (or 'rnd' /
                'random').

            demean: bool, optional, (def: True)
                Remove the mean of your signals. If you set it to False, you
                risk to have signals off-camera.

            cmap: string, optional, (def: inferno)
                Matplotlib colormap (parameter active for 'dyn_minmax' and
                'dyn_time' color).

            clim: tuple/list, optional, (def: None)
                Limit of the colormap. The clim parameter must be a tuple /
                list of two float number each one describing respectively the
                (min, max) of the colormap. Every values under clim[0] or over
                clim[1] will peaked (parameter active for 'dyn_minmax' and
                'dyn_time' color).

            alpha: float, optional, (def: 1.0)
                The opacity to use. The alpha parameter must be between 0 and 1
                (parameter active for 'dyn_minmax' and 'dyn_time' color).

            vmin: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the under parameter bellow (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            under: tuple/string, optional, (def: 'gray')
                Matplotlib color for values under vmin (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            vmax: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the over parameter bellow (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            over: tuple/string, optional, (def: 'red')
                Matplotlib color for values over vmax (parameter active for
                'dyn_minmax' and 'dyn_time' color).

            laps: int, optional, (def: 10)
                Number of points to update every 1/sampling_frequency.

            scale: tuple, optional, (def: (1., 1.))
                Scale each signal along (x, y) dimensions. The scale parameter
                must be a tuple of two floats.

            unicolor: string/tuple, optional, (def: 'gray')
                The color to use in case of uniform color (see color parameter
                above)

            norm: bool, optional, (def: True)
                Normalize data.
        """
        #######################################################################
        # INPUTS
        #######################################################################
        self._sf = sf
        self._color, self._rnd_dyn, self._unicolor = color, rnd_dyn, unicolor
        self._axis, self._space, self._force_col = axis, space, force_col
        self._cmap, self._clim, self._vmin, self._vmax = cmap, clim, vmin, vmax
        self._under, self._over = under, over
        self._play, self._demean, self._laps = play, demean, laps
        self._uscale, self._norm = scale, norm

        #######################################################################
        # CHECK AXIS
        #######################################################################
        # =====================================================
        # Get the number of dimensions :
        ndim, sh = data.ndim, data.shape

        # =====================================================
        # Define the maximum number of dimensions :
        L = 3 if ndim > 3 else ndim

        # =====================================================
        # Manage the axis parameter :
        if axis is None:
            axis = tuple(range(L))
        else:
            # Force to be a tuple :
            axis = tuple(axis)
            # Check length :
            if len(axis) is not L:
                raise ValueError("The length of the axis parameter must "
                                 "be "+str(L))
        # Make a copy of axis :
        self._selectedaxis = axis

        #######################################################################
        # CHECK DATA
        # The data array must be a 2d array organize as follow :
        # data.shape = (N_rows x N_cols, N_time)
        #######################################################################
        # =====================================================
        # Transform data type :
        # ----------------------------------
        # 1D data :
        if ndim == 1:  # Raw vector
            # Fix 1 row / 1 column :
            self.dim = (1, 1)
            # Make it (1, n_times) :
            data = data[np.newaxis, ...]

        # ----------------------------------
        # 2D data :
        elif ndim == 2:  # Matrix
            # Transpose if time is on axis 0:
            if axis[0] == 0:
                # Make copy to be sure to transpose in memory :
                data = np.transpose(data, (1, 0)).copy()
                axis = [1, 0]
            # Get optimal subplot number :
            self.dim = ndsubplot(data.shape[0], force_col=force_col)

        # ----------------------------------
        # > 3D data :
        elif ndim >= 3:  # ndarray
            # For ndarray with ndim > 3, select certain axis :
            if ndim > 3:
                # Build a list of slices :
                sl = [slice(1)] * ndim
                for k in axis:
                    sl[k] = slice(None)
                # Keep only axis dimensions :
                data = np.squeeze(data[sl])
                # Now, update the axis by ranking values :
                axis = list(np.argsort(axis).argsort())
                # Order reduced array axis :
            # Find index for transposing (n_rows, n_cols, n_time) :
            rshidx = [axis[k] for k in [1, 2, 0]]
            if rshidx != [0, 1, 2]:
                # Transpose dimensions the data. :
                data = np.transpose(data, rshidx).copy()
            sh = data.shape
            # Finally, make the data (n_rows x n_cols, n_time) :
            data = np.reshape(data, (sh[0]*sh[1], sh[2]))
            self.dim = (sh[0], sh[1])

        # =====================================================
        # Data de-mean and normalization :
        # ----------------------------------
        # Remove the mean signal :
        data_mean = np.mean(data, axis=1, keepdims=True) if demean else 0

        # ----------------------------------
        # Normalize the data for the visualization :
        data_max = (data-data_mean).max() if norm else 1

        # =====================================================
        # Update variables :
        # ----------------------------------
        # Get the number of time points :
        self._sh = data.shape
        self.n = self._sh[1]
        nrows, ncols, n, m = self.nrows, self.ncols, self.n, self.m
        self._axis = axis

        # Define the time vector :
        self._time = np.arange(n, dtype=np.float32) / self._sf

        # Build the index array :
        index = np.c_[np.repeat(np.repeat(np.arange(ncols), nrows), n),
                      np.repeat(np.tile(np.arange(nrows), ncols), n),
                      np.tile(np.arange(n), m)].astype(np.float32)

        #######################################################################
        # CHECK COLOR
        # The color array must be a 2D array organize as follow :
        # color.shape = (N_rows x N_cols x N_time, 3)
        # n = N_time, m = N_rows x N_cols
        #######################################################################
        # =====================================================
        # Build the color array :
        # ----------------------------------
        # Random color :
        if color in [None, 'rnd', 'random']:
            # Create a (m, 3) color array :
            singcol = np.random.uniform(size=(m, 3), low=rnd_dyn[0],
                                        high=rnd_dyn[1]).astype(np.float32)
            # Repeat the array n_times to have a (m*n_times, 3) array :
            a_color = np.repeat(singcol, n, axis=0)

        # ----------------------------------
        # Dynamic minmax color :
        elif color == 'dyn_minmax':
            # Get colormap as (n, 3):
            a_color = array2colormap(data.ravel(), cmap=cmap, clim=clim,
                                     vmin=vmin, vmax=vmax, under=under,
                                     over=over)[:, 0:3]
            self.minmax = (data.min(), data.max())

        # ----------------------------------
        # Dynamic time color :
        elif color == 'dyn_time':
            # Repeat the time vector nrows x ncols times:
            timerep = np.tile(self._time[np.newaxis, ...], (m, 1))
            # Get the colormap :
            a_color = array2colormap(timerep.ravel(), cmap=cmap, clim=clim,
                                     vmin=vmin, vmax=vmax, under=under,
                                     over=over)[:, 0:3]
            self.minmax = (self._time.min(), self._time.max())

        # ----------------------------------
        # Uniform color :
        elif color == 'uniform':
            # Create a (m, 3) color array :
            singcol = color2vb(unicolor, length=m)[:, 0:3]
            # Repeat the array n_times to have a (m*n_times, 3) array :
            a_color = np.repeat(singcol, n, axis=0)

        # ----------------------------------
        # Not found color :
        else:
            raise ValueError("The color parameter is not recognized.")

        # Get a (m, n, 3) color array copy :
        # self._colsh = a_color.reshape(self.m, self.n, 3)

        #######################################################################
        # BUFFER
        #######################################################################
        # =====================================================
        # Data buffer :
        self._dbuffer = gloo.VertexBuffer((data-data_mean)/data_max)
        self._ibuffer = gloo.VertexBuffer(index)
        self.shared_program.vert['a_position'] = self._dbuffer
        self.shared_program.vert['a_index'] = self._ibuffer
        # =====================================================
        # Color buffer :
        self._cbuffer = gloo.VertexBuffer(np.ascontiguousarray(a_color))
        self.shared_program.vert['a_color'] = self._cbuffer
        # =====================================================
        # Args buffer :
        self.shared_program.vert['u_scale'] = scale
        self.shared_program.vert['u_size'] = self.dim
        self.shared_program.vert['u_n'] = n
        self.shared_program.vert['u_space'] = space

    def play(self, start=True, laps=10):
        """Play signals in real time.

        Kargs:
            start: bool, optional, (def: False)
                Play the data. For a better interpretation, you should use the
                'dyn_time' option of the color parameter.

            laps: int, optional, (def: 10)
                Number of points to update every 1/sampling_frequency.
        """
        if isinstance(start, bool) and isinstance(laps, int):
            if start:
                self._laps = laps
                self._timer.start()
            else:
                self._timer.stop()
        else:
            raise ValueError("start must be a bool.")

    def time_reset(self):
        """Reset time signals."""
        # Find time 0 :
        ind = self._time.argmin()
        # Reset only if not 0 :
        if ind:
            self._time_laps(ind)

    def set_camera(self, camera):
        """Set a camera to the mesh.

        This is essential to add to the mesh the link between the camera
        rotations (transformation) to the vertex shader.

        Args:
            camera: vispy.camera
                Set a camera to the Mesh for light adaptation
        """
        self.camera = camera
        self.update()

    def clean(self):
        """Clean buffers."""
        self._dbuffer.delete()
        self._ibuffer.delete()
        self._cbuffer.delete()

    # ========================================================================
    # ========================================================================
    # PLOTTING SUB-FUNCTIONS
    # ========================================================================
    # ========================================================================
    def _prepare_transforms(self, view):
        """This is call for the first rendering."""
        tr = view.transforms
        view_vert = view.view_program.vert
        view_vert['transform'] = tr.get_transform()

    # def _prepare_draw(self, view=None):
    #     """Function called everytime there's a camera update."""
    #     pass

    def on_timer(self, event):
        """Add some data at the end of each signal (real-time signals)."""
        self._time_laps(self._laps)

    def _time_laps(self, laps):
        """Introduce a time laps in data / color / time.

        Args:
            laps: int, optional, (def: 10)
                Number of points to update every 1/sampling_frequency.
        """
        # ---------------------------------------------------------------------
        # Set new time laps :
        timeC = self._time.copy()
        self._time[:-laps] = self._time[laps:]
        self._time[-laps:] = timeC[0:laps]
        # Rank values :
        t = self._time.argsort().argsort()
        # Update index :
        cols, rows, n, m = self.ncols, self.nrows, self.n, self.m
        index = np.c_[np.repeat(np.repeat(np.arange(cols), rows), n),
                      np.repeat(np.tile(np.arange(rows), cols), n),
                      np.tile(t, m)].astype(np.float32)
        self._ibuffer.set_data(index)
        self.update()

    def _update_camrect(self):
        """Update camera rectangle."""
        self.camera.rect.pos = (-1, -1)
        self.camera.rect.size = (self._space, self._space)

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

    # ----------- DIM -----------
    @property
    def dim(self):
        """Get the subplot dimension."""
        return tuple(self._dim)

    @dim.setter
    def dim(self, value):
        """Set dim value."""
        self._dim = value
        self._nrows = self._dim[0]
        self._ncols = self._dim[1]
        self._m = self._nrows * self._ncols

    # ----------- NROWS -----------
    @property
    def nrows(self):
        """Get the number of rows."""
        return self._nrows

    @nrows.setter
    def nrows(self, value):
        """Set nrows value."""
        self._nrows = value
        self._dim[0] = value

    # ----------- NCOLS -----------
    @property
    def ncols(self):
        """Get the number of columns."""
        return self._ncols

    @ncols.setter
    def ncols(self, value):
        """Set ncols value."""
        self._ncols = value
        self._dim[1] = value

    # ----------- M -----------
    @property
    def m(self):
        """Get n_rows * n_cols."""
        return self._nrows * self._ncols

    # ----------- N -----------
    @property
    def n(self):
        """Get the number of time points."""
        return self._n

    @n.setter
    def n(self, value):
        """Set n value."""
        if value < 5:
            raise ValueError("The number of time points must be at least >= 5")
        self._n = value

    # ----------- MINMAX -----------
    @property
    def minmax(self):
        """Get the minmax value."""
        return self._minmax

    @minmax.setter
    def minmax(self, value):
        """Set minmax value."""
        self._minmax = value

    # ----------- MINMAX -----------
    @property
    def rect(self):
        return (-1., -1., self._space, self._space)

GridSignalMesh = create_visual_node(GridSignalVisual)
