"""
"""

import numpy as np

from vispy import app, gloo, visuals
from vispy.scene.visuals import create_visual_node

from ...utils import ndsubplot, array2colormap, color2vb

from warnings import warn


__all__ = ['NdpltMesh']


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
    v_ab = vec4(a, b);
}
"""

fragment_shader = """
#version 120
varying vec4 v_color;
varying vec3 v_index;
varying vec2 v_position;
varying vec4 v_ab;
void main() {
    gl_FragColor = v_color;

    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        discard;
}
"""


class NdpltVisual(visuals.Visual):
    """Visual class of nd-signals visualization.

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

            If the data is a row vector,the axis parameter is not active. If
            the data is a 2D matrix, you have to specify the meaning of each
            axis (ex: data.shape=(20, 1000) and axis=(1, 0) mean that the
            second axis as the time dimension. Then, the 20 plots will be
            organized in a 10x2 grid). Finally, if the data is a 3D array,
            specify where are the time axis, the number of rows and columns.
            (ex: data.shape=(20, 1000, 10) and axis=(2, 0, 1) the program will
            display a grid of 10 rows x 20 columns, each plot having 1000
            points).

        color: string/tuple/array, optional, (def: None)
            Choose how to color signals. Use None (or 'rnd', 'random') to
            generate random colors. Use 'uniform' (see the unicolor parameter)
            to define the same color for all signals. Use 'dyn_time' to have a
            dynamic color according to the time index. This is particulary
            convenient to inspect real time signals (see play parameter). Use
            'dyn_minmax' to a color code acording to the dynamic of the signal.
            This option can be used to detect extrema and can be futher
            controled using colormap parameters (cmap, clim, vmin, vmax, under
            and over).

        space: int, optional, (def: 2)
            The space between each plot. I recommand using a space >= 2.

        ax_name: list, optional, (def: None)
            Set the name of each axis. Must be a list of strings with the same
            length as the axis parameter.

        play: bool, optional, (def: False)
            Play the data. For a better interpretation, you should use the
            'dyn_time' option of the color parameter.

        force_col: int, optional, (def: None)
            Force the number of columns in the plot. In case of a 2D matrix,
            the program try to find the best grid organization. But if it
            failed, use this parameter to fix your own number of columns and
            the program will found the corresponding number of rows.

        rnd_dyn: tuple, optional, (def: (.3, .9))
            Define the dynamic of random color. This parameter is active only
            if the color parameter is turned to None (or 'rnd' / 'random').

        demean: bool, optional, (def: True)
            Remove the mean of your signals. If you set it to False, you risk
            to have signals off-camera.

        cmap: string, optional, (def: inferno)
            Matplotlib colormap (parameter active for 'dyn_minmax' and
            'dyn_time' color).

        clim: tuple/list, optional, (def: None)
            Limit of the colormap. The clim parameter must be a tuple / list
            of two float number each one describing respectively the (min, max)
            of the colormap. Every values under clim[0] or over clim[1] will
            peaked (parameter active for 'dyn_minmax' and 'dyn_time' color).

        alpha: float, optional, (def: 1.0)
            The opacity to use. The alpha parameter must be between 0 and 1
            (parameter active for 'dyn_minmax' and 'dyn_time' color).

        vmin: float, optional, (def: None)
            Threshold from which every color will have the color defined using
            the under parameter bellow (parameter active for 'dyn_minmax' and
            'dyn_time' color).

        under: tuple/string, optional, (def: 'gray')
            Matplotlib color for values under vmin (parameter active for
            'dyn_minmax' and 'dyn_time' color).

        vmax: float, optional, (def: None)
            Threshold from which every color will have the color defined using
            the over parameter bellow (parameter active for 'dyn_minmax' and
            'dyn_time' color).

        over: tuple/string, optional, (def: 'red')
            Matplotlib color for values over vmax (parameter active for
            'dyn_minmax' and 'dyn_time' color).

        laps: int, optional, (def: 10)
            Number of points to update every 1/sampling_frequency.

        scale: tuple, optional, (def: (1., 1.))
            Scale each signal along (x, y) dimensions. The scale parameter must
            be a tuple of two floats.

        unicolor: string/tuple, optional, (def: 'gray')
            The color to use in case of uniform color (see color parameter
            above)
    """

    def __len__(self):
        """Return the number of time points."""
        return self.n

    def __init__(self, data, sf, axis=None, color=None, space=2, ax_name=None,
                 play=False, force_col=None, rnd_dyn=(.3, .9), demean=True,
                 cmap='viridis', clim=None, vmin=None, under='gray', vmax=None,
                 over='red', laps=1, scale=(1., 1.), unicolor='gray'):
        """Init."""
        # --------------------------------------------------------------------
        # Get inputs :
        self._data = data
        self._sf = np.float32(sf)
        self._color = color
        self._ax_name = ax_name
        self._play = play
        self._axis = axis
        self._space = space
        self._force_col = force_col
        self._rnd_dyn = rnd_dyn
        self._demean = demean
        self._cmap, self._clim, self._vmin, self._vmax = cmap, clim, vmin, vmax
        self._under, self._over = under, over
        self._laps = laps
        self._uscale = scale
        self._unicolor = unicolor

        # Define attributes :
        self._dim = [0, 0]
        self.nrows = 0
        self.ncols = 0
        self.camera = []

        # --------------------------------------------------------------------
        # Initialize the vispy.Visual class with the vertex / fragment buffer :
        # and OpenGL state :
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        self.set_gl_state('translucent', depth_test=True, cull_face=False,
                          blend=True, blend_func=('src_alpha',
                                                  'one_minus_src_alpha'))
        self._draw_mode = 'line_strip'

        # --------------------------------------------------------------------
        # Check data // color // other parameters :
        self._check_data()
        self._check_color()
        self._check_others()
        # --------------------------------------------------------------------
        # Link the time the the on_time function :
        self._timer = app.Timer(1/self._sf, connect=self.on_timer, start=play)

        self.freeze()

    # ========================================================================
    # ========================================================================
    # SET DATA
    # ========================================================================
    # ========================================================================
    def set_data(self, data, axis=None, ax_name=None, force_col=None,
                 demean=True):
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

        ax_name: list, optional, (def: None)
            Set the name of each axis. Must be a list of strings with the same
            length as the axis parameter.

        force_col: int, optional, (def: None)
            Force the number of columns in the plot. In case of a 2D matrix,
            the program try to find the best grid organization. But if it
            failed, use this parameter to fix your own number of columns and
            the program will found the corresponding number of rows.

        demean: bool, optional, (def: True)
            Remove the mean of your signals. If you set it to False, you risk
            to have signals off-camera.
        """
        # Get inputs arguments :
        self._data, self._demean = data, demean
        self._axis, self._ax_name = axis, ax_name
        self._force_col = force_col
        # Check data :
        self._check()

    def set_color(self, color=None, rnd_dyn=(0.3, 0.9), cmap='viridis',
                  clim=None, vmin=None, under=None, vmax=None, over=None,
                  unicolor='gray'):
        """Set new color parameter to the data.

        Kargs:
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

            rnd_dyn: tuple, optional, (def: (.3, .9))
                Define the dynamic of random color. This parameter is active
                only if the color parameter is turned to None (or 'rnd' /
                'random').

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

            unicolor: tuple/string, optional, (def: 'gray')
                The color to use in case of uniform color.
        """
        # Get inputs arguments :
        self._color, self._rnd_dyn, self._unicolor = color, rnd_dyn, unicolor
        self._cmap, self._clim, self._vmin, self._vmax = cmap, clim, vmin, vmax
        self._under, self._over = under, over
        # Check color :
        self._check_color()

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

    def set_space(self, space=2):
        """Set space between plots.

        Kargs:
            space: int, optional, (def: 2)
                The space between each plot. I recommand using a space >= 2.
        """
        if isinstance(space, (int, float)):
            # Set space as a float :
            self._space = float(space)
            self.shared_program.vert['u_space'] = self._space
            # Update camera rectangle :
            # self._update_camrect()

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
    # CHECK DATA
    # ========================================================================
    # ========================================================================
    def _check(self):
        """Check data, color and other inputs."""
        # Check data, color and other parameters :
        self._check_data()
        self._check_color()
        self._check_others()

    def _check_axis(self):
        """Check axis and axis names parameters."""
        # ---------------------------------------------------------------------
        # Get the number of dimensions :
        ndim = self._data.ndim

        # ---------------------------------------------------------------------
        # Define the maximum number of dimensions :
        if ndim > 3:
            L = 3
        else:
            L = ndim

        # ---------------------------------------------------------------------
        # Manage the axis parameter :
        if self._axis is None:
            self._axis = tuple(range(L))
            self._ax_name = ['Time'] + [''] * (L-1)
        else:
            # Force to be a tuple :
            self._axis = tuple(self._axis)
            # Check length :
            if len(self._axis) is not L:
                raise ValueError("The length of the axis parameter must "
                                 "be "+str(L))

        # ---------------------------------------------------------------------
        # Manage the ax_name parameter :
        if self._ax_name is None:
            self._ax_name = ['Time'] + [''] * (L-1)
        elif len(self._ax_name) is not len(self._axis):
            warn("The length of the ax_name parameter must be the same as the "
                 "length of the axis paramater ("+str(len(self._axis))+")")
            self._ax_name = ['Time'] + [''] * (L-1)
        else:
            # Check if all are strings:
            self._ax_name = list(self._ax_name)
            if not all([type(k) is str for k in self._ax_name]):
                warn("The ax_names must be composed of strings")
            self._ax_name = ['Time'] + [''] * (L-1)

    def _check_data(self):
        """Check data shape and type.

        The data array must be a 2d array organize as follow :
        data.shape = (N_rows x N_cols, N_time)
        """
        # ---------------------------------------------------------------------
        # Check axis parameter :
        self._check_axis()

        # Get the number of dimensions :
        ndim = self._data.ndim

        # ---------------------------------------------------------------------
        # Transform 1D data :
        if ndim == 1:  # Raw vector
            # Fix 1 row / 1 column :
            self.dim = (1, 1)
            # Make it (1, n_times) :
            self._data = self._data[np.newaxis, ...]

        # ---------------------------------------------------------------------
        # Transform 2D data :
        elif ndim == 2:  # Matrix
            # Transpose if time is on axis 0:
            if self._axis[0] == 0:
                # Make copy to be sure to transpose in memory :
                self._data = np.transpose(self._data, (1, 0)).copy()
                self._axis = [1, 0]
            # Get optimal subplot number :
            self.dim = ndsubplot(self._data.shape[0],
                                 force_col=self._force_col)

        # ---------------------------------------------------------------------
        # Transform >= 3D data :
        elif ndim >= 3:  # ndarray
            # For ndarray with ndim > 3, select certain axis :
            if ndim > 3:
                # Build a list of slices :
                sl = [slice(1)] * ndim
                for k in self._axis:
                    sl[k] = slice(None)
                # Keep only self._axis dimensions :
                self._data = np.squeeze(self._data[sl])
                # Now, update the axis by ranking values :
                self._axis = list(np.argsort(self._axis).argsort())
                # Order reduced array axis :
                self._axis = [self._axis.index(k) for k in range(3)]
            # Convert axis into a list (because we index index() method):
            axlst = list(self._axis)
            # Find index for transposing (n_rows, n_cols, n_time) :
            rshidx = [axlst.index(k) for k in [1, 2, 0]]
            # Transpose dimensions the data :
            self._data = np.transpose(self._data, rshidx).copy()
            sh = self._data.shape
            # Finally, make the data (n_rows x n_cols, n_time) :
            self._data = np.reshape(self._data, (sh[0]*sh[1], sh[2]))
            self.dim = (sh[0], sh[1])

        # Remove the mean signal :
        if self._demean:
            # Get the mean and remove it:
            self._data -= np.mean(self._data, axis=1, keepdims=True)

        # Normalize the data for the visualization :
        self._data /= self._data.max()

        # Get the number of time points :
        self.n = self._data.shape[1]

        # Complete data (in case of missing row/col) :
        # print('=================> COMPLETE DATA <=================')
        # print(self._data.shape, self.dim, self._nrows, self._ncols, self._n)
        # print('===================================================')

        # Build the index array :
        nrows, ncols, n, m = self.nrows, self.ncols, self.n, self.m
        self._index = np.c_[np.repeat(np.repeat(np.arange(ncols), nrows), n),
                            np.repeat(np.tile(np.arange(nrows), ncols), n),
                            np.tile(np.arange(n), m)].astype(np.float32)

        # Define the time vector :
        self._time = np.arange(n, dtype=np.float32) / self._sf

        # Send to buffer :
        self._buffer_data()

    def _check_color(self):
        """Check the color.

        The color array must be a 2D array organize as follow :
        color.shape = (N_rows x N_cols x N_time, 3)
        n = N_time, m = N_rows x N_cols
        """
        # ---------------------------------------------------------------------
        # Random color :
        if self._color in [None, 'rnd', 'random']:
            # Create a (m, 3) color array :
            singcol = np.random.uniform(size=(self.m, 3), low=self._rnd_dyn[0],
                                        high=self._rnd_dyn[1]).astype(
                                        np.float32)
            # Repeat the array n_times to have a (m*n_times, 3) array :
            self._a_color = np.repeat(singcol, self.n, axis=0)

        # ---------------------------------------------------------------------
        # Dynamic minmax color :
        elif self._color == 'dyn_minmax':
            # Get colormap as (n, 3):
            self._a_color = array2colormap(self._data.ravel(), cmap=self._cmap,
                                           clim=self._clim, vmin=self._vmin,
                                           vmax=self._vmax, under=self._under,
                                           over=self._over)[:, 0:3]

        # ---------------------------------------------------------------------
        # Dynamic time color :
        elif self._color == 'dyn_time':
            # Repeat the time vector nrows x ncols times:
            timerep = np.tile(self._time[np.newaxis, ...], (self.m, 1))
            # Get the colormap :
            self._a_color = array2colormap(timerep.ravel(), cmap=self._cmap,
                                           clim=self._clim, vmin=self._vmin,
                                           vmax=self._vmax, under=self._under,
                                           over=self._over)[:, 0:3]

        # ---------------------------------------------------------------------
        # Uniform color :
        elif self._color == 'uniform':
            # Create a (m, 3) color array :
            singcol = color2vb(self._unicolor, length=self._m)[:, 0:3]
            # Repeat the array n_times to have a (m*n_times, 3) array :
            self._a_color = np.repeat(singcol, self.n, axis=0)

        # ---------------------------------------------------------------------
        # Not found color :
        else:
            raise ValueError("The color parameter is not recognized.")

        # Get a (m, n, 3) color array copy :
        self._colsh = self._a_color.reshape(self.m, self.n, 3)

        # Run buffer color :
        self._buffer_color()

    def _check_others(self):
        """Check other parameters to pass to the buffer."""
        # Check other parameters :
        pass

        # Buffer for other args :
        self._buffer_args()

    def _update_camrect(self):
        """Update camera rectangle."""
        self.camera.rect.pos = (-1, -1)
        self.camera.rect.size = (self._space, self._space)

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
        # Update "laps" points of the data :
        dataC = self._data.copy()
        self._data[:, :-laps] = self._data[:, laps:]
        self._data[:, -laps:] = dataC[:, 0:laps]

        # ---------------------------------------------------------------------
        # Update "laps" points of the color :
        colorC = self._colsh.copy()
        self._colsh[:, :-laps, :] = self._colsh[:, laps:, :]
        self._colsh[:, -laps:, :] = colorC[:, 0:laps, :]
        self._a_color = self._colsh

        # ---------------------------------------------------------------------
        # Update time vector :
        timeC = self._time.copy()
        self._time[:-laps] = self._time[laps:]
        self._time[-laps:] = timeC[0:laps]

        # ---------------------------------------------------------------------
        # Buffer updates :
        self._buffer_data()
        self._buffer_color()
        self.update()

    # ========================================================================
    # ========================================================================
    # BUFFER
    # ========================================================================
    # ========================================================================
    def _buffer(self):
        """Set & Update all buffers."""
        self._buffer_data()
        self._buffer_color()
        self._buffer_args()

    def _buffer_data(self):
        """Set & Update data buffer."""
        self._dbuffer = gloo.VertexBuffer(self._data)
        self._ibuffer = gloo.VertexBuffer(self._index)
        self.shared_program.vert['a_position'] = self._dbuffer
        self.shared_program.vert['a_index'] = self._ibuffer

    def _buffer_color(self):
        """Set & Update color buffer."""
        self._cbuffer = gloo.VertexBuffer(self._a_color)
        self.shared_program.vert['a_color'] = self._cbuffer

    def _buffer_args(self):
        """Set & Update other args buffer."""
        self.shared_program.vert['u_scale'] = self._uscale
        self.shared_program.vert['u_size'] = self.dim
        self.shared_program.vert['u_n'] = self._n
        self.shared_program.vert['u_space'] = self._space

    # ========================================================================
    # ========================================================================
    # PROPERTIES
    # ========================================================================
    # ========================================================================
    @property
    def nrows(self):
        """Get the number of rows."""
        return self._nrows

    @nrows.setter
    def nrows(self, value):
        """Set nrows value."""
        self._nrows = value
        self._dim[0] = value

    @property
    def ncols(self):
        """Get the number of columns."""
        return self._ncols

    @ncols.setter
    def ncols(self, value):
        """Set ncols value."""
        self._ncols = value
        self._dim[1] = value

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

    @property
    def m(self):
        """Get n_rows * n_cols."""
        return self._nrows * self._ncols

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


NdpltMesh = create_visual_node(NdpltVisual)
