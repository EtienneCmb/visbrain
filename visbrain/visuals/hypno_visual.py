"""Display signals into a grid..

A large portion of this code was taken from the example developped by the vispy
team :
https://github.com/vispy/vispy/blob/master/examples/demo/gloo/realtime_signals.py
"""
import numpy as np

from vispy import gloo, visuals
from vispy.visuals.shaders import Function
from vispy.scene.visuals import create_visual_node

from visbrain.utils import vispy_array, wrap_properties, color2vb, transient
# from visbrain.io import is_opengl_installed


__all__ = ('Hypnogram')


STAGES = ['art', 'wake', 'rem', 'n1', 'n2', 'n3']

vec2to4 = Function("""
    vec4 vec2to4(vec2 inp) {
        return vec4(inp, 0, 1);
    }
""")

vertex_shader = """
#version 120
varying vec4 pos;
varying vec4 v_color;
float pos_y;

void main() {

    // Position conversion :
    pos = $to_vec4($position);
    if (pos.y == $u_art){ // ART
        pos.y = $u_art_visual;
        v_color = $u_art_color;
    }
    else if (pos.y == $u_wake){ // WAKE
        pos.y = $u_wake_visual;
        v_color = $u_wake_color;
    }
    else if (pos.y == $u_rem){ // REM
        pos.y = $u_rem_visual;
        v_color = $u_rem_color;
    }
    else if (pos.y == $u_n1){ // N1
        pos.y = $u_n1_visual;
        v_color = $u_n1_color;
    }
    else if (pos.y == $u_n2){ // N2
        pos.y = $u_n2_visual;
        v_color = $u_n2_color;
    }
    else if (pos.y == $u_n3){ // N3
        pos.y = $u_n3_visual;
        v_color = $u_n3_color;
    }

    // Color conversion :
    if ($transient != 10.){
        v_color = vec4(.95, .95, .95, 1.);
    }

    // Uniform color :
    if ($u_unicolor == 1){
        v_color = vec4(0., 0., 0., 1.);
    }

    gl_Position = $transform(pos);
}
"""

fragment_shader = """
#version 120
varying vec4 v_color;

void main() {
    gl_FragColor = v_color;
}
"""


class HypogramVisual(visuals.Visual):
    """Visual class for grid of signals.

    Parameters
    ----------
    data : array_like
        Array of data of shape (n_pts,).
    time : array_like | None
        Array of time points of shape (n_pts,)
    art, wake, rem, n1, n2, n3 :
        Stage identification inside the data array.
    art_visual, wake_visual, rem_visual, n1_visual, n2_visual, n3_visual :
        Stage order when plotting.
    art_color, wake_color, rem_color, n1_color, n2_color, n3_color :
        Stage color.
    line_width : float | 2.
        Line with of the hypnogram.
    antialias : bool | False
        Use anti-aliasing line.
    unicolor : bool | False
        Use a uni black color for the hypnogram.
    """

    def __len__(self):
        """Return the number of time points."""
        return self._n

    def __init__(self, data, time=None, art=-1, wake=0, n1=1, n2=2, n3=3,
                 rem=4, art_visual=1, wake_visual=0, rem_visual=-1,
                 n1_visual=-2, n2_visual=-3, n3_visual=-4, art_color='#8bbf56',
                 wake_color='#56bf8b', rem_color='#bf5656', n1_color='#aabcce',
                 n2_color='#405c79', n3_color='#0b1c2c', line_width=2.,
                 antialias=False, unicolor=False):
        """Init."""
        # =========================== VISUALS ===========================
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)
        self._draw_mode = 'line_strip'

        # =========================== BUFFERS ===========================
        pos_2 = np.random.rand(1, 2).astype(np.float32)
        pos_1 = np.random.rand(1).astype(np.float32)
        self._position_vbo = gloo.VertexBuffer(pos_2)
        self._transient_vbo = gloo.VertexBuffer(pos_1)
        self.shared_program.vert['position'] = self._position_vbo
        self.shared_program.vert['transient'] = self._transient_vbo
        self._program.vert['to_vec4'] = vec2to4
        self.line_width = line_width
        self.antialias = antialias
        self.unicolor = unicolor
        # Stage :
        self.art = art
        self.wake = wake
        self.rem = rem
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        # Stage visual :
        self.art_visual = art_visual
        self.wake_visual = wake_visual
        self.rem_visual = rem_visual
        self.n1_visual = n1_visual
        self.n2_visual = n2_visual
        self.n3_visual = n3_visual
        # Stage color :
        self.art_color = art_color
        self.wake_color = wake_color
        self.rem_color = rem_color
        self.n1_color = n1_color
        self.n2_color = n2_color
        self.n3_color = n3_color

        # Set data :
        self.set_data(data, time)
        self.freeze()

    def set_data(self, data, time=None):
        """Set data to the grid of signals.

        Parameters
        ----------
        data : array_like
            Array of data of shape (n_pts,).
        time : array_like | None
            Array of time points of shape (n_pts,)
        """
        data = np.asarray(data)
        assert data.ndim == 1
        self._n = len(data)
        time = np.arange(len(data)) if time is None else np.asarray(time)
        assert len(time) == len(self)

        # Transient detection :
        self.transient = data

        #
        self._pos = vispy_array(np.c_[time, data])
        self._position_vbo.set_data(self._pos)

    def set_stage(self, stage, idx_start, idx_end):
        """Set stage.

        Parameters
        ----------
        stage : str, int
            Stage to define. Should either be a string (e.g 'art', 'rem'...) or
            an integer.
        idx_start : int
            Index where the stage begin.
        idx_end : int
            Index where the stage finish.
        """
        if isinstance(stage, str):
            assert stage in STAGES
            stage = eval('self.%s' % stage)
        self._pos[idx_start:idx_end, 1] = stage
        self.transient = self._pos[:, 1]

    def _prepare_transforms(self, view):
        """Call for the first rendering."""
        tr = view.transforms
        view_vert = view.view_program.vert
        view_vert['transform'] = tr.get_transform()

    def _prepare_draw(self, view=None):
        """Function called everytime there's a camera update."""
        try:
            import OpenGL.GL as GL
            GL.glLineWidth(self._line_width)
            if self._antialias:
                GL.glEnable(GL.GL_LINE_SMOOTH)
            else:
                GL.glDisable(GL.GL_LINE_SMOOTH)
        except:
            pass

    def min_visual(self):
        return min(self.art_visual, self.wake_visual, self.rem_visual,
                   self.n1_visual, self.n2_visual, self.n3_visual)

    def max_visual(self):
        return max(self.art_visual, self.wake_visual, self.rem_visual,
                   self.n1_visual, self.n2_visual, self.n3_visual)

    # ========================================================================
    # ========================================================================
    # PROPERTIES
    # ========================================================================
    # ========================================================================
    # ----------- TIME -----------
    @property
    def time(self):
        """Get the time value."""
        return self._pos[:, 0]

    # ----------- DATA -----------
    @property
    def data(self):
        """Get the data value."""
        return self._pos[:, 1]

    # ----------- ART -----------
    @property
    def art(self):
        """Get the art value."""
        return self._art

    @art.setter
    @wrap_properties
    def art(self, value):
        """Set art value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_art'] = value
        self._art = value

    # ----------- WAKE -----------
    @property
    def wake(self):
        """Get the wake value."""
        return self._wake

    @wake.setter
    @wrap_properties
    def wake(self, value):
        """Set wake value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_wake'] = value
        self._wake = value

    # ----------- REM -----------
    @property
    def rem(self):
        """Get the rem value."""
        return self._rem

    @rem.setter
    @wrap_properties
    def rem(self, value):
        """Set rem value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_rem'] = value
        self._rem = value

    # ----------- N1 -----------
    @property
    def n1(self):
        """Get the n1 value."""
        return self._n1

    @n1.setter
    @wrap_properties
    def n1(self, value):
        """Set n1 value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_n1'] = value
        self._n1 = value

    # ----------- N2 -----------
    @property
    def n2(self):
        """Get the n2 value."""
        return self._n2

    @n2.setter
    @wrap_properties
    def n2(self, value):
        """Set n2 value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_n2'] = value
        self._n2 = value

    # ----------- N3 -----------
    @property
    def n3(self):
        """Get the n3 value."""
        return self._n3

    @n3.setter
    @wrap_properties
    def n3(self, value):
        """Set n3 value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_n3'] = value
        self._n3 = value

    # ----------- ART_VISUAL -----------
    @property
    def art_visual(self):
        """Get the art_visual value."""
        return self._art_visual

    @art_visual.setter
    @wrap_properties
    def art_visual(self, value):
        """Set art_visual value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_art_visual'] = value
        self._art_visual = value

    # ----------- WAKE_VISUAL -----------
    @property
    def wake_visual(self):
        """Get the wake_visual value."""
        return self._wake_visual

    @wake_visual.setter
    @wrap_properties
    def wake_visual(self, value):
        """Set wake_visual value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_wake_visual'] = value
        self._wake_visual = value

    # ----------- REM_VISUAL -----------
    @property
    def rem_visual(self):
        """Get the rem_visual value."""
        return self._rem_visual

    @rem_visual.setter
    @wrap_properties
    def rem_visual(self, value):
        """Set rem_visual value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_rem_visual'] = value
        self._rem_visual = value

    # ----------- N1_VISUAL -----------
    @property
    def n1_visual(self):
        """Get the n1_visual value."""
        return self._n1_visual

    @n1_visual.setter
    @wrap_properties
    def n1_visual(self, value):
        """Set n1_visual value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_n1_visual'] = value
        self._n1_visual = value

    # ----------- N2_VISUAL -----------
    @property
    def n2_visual(self):
        """Get the n2_visual value."""
        return self._n2_visual

    @n2_visual.setter
    @wrap_properties
    def n2_visual(self, value):
        """Set n2_visual value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_n2_visual'] = value
        self._n2_visual = value

    # ----------- N3_VISUAL -----------
    @property
    def n3_visual(self):
        """Get the n3_visual value."""
        return self._n3_visual

    @n3_visual.setter
    @wrap_properties
    def n3_visual(self, value):
        """Set n3_visual value."""
        assert isinstance(value, (int, float))
        self.shared_program.vert['u_n3_visual'] = value
        self._n3_visual = value

    # ----------- ART_COLOR -----------
    @property
    def art_color(self):
        """Get the art_color value."""
        return self._art_color

    @art_color.setter
    @wrap_properties
    def art_color(self, value):
        """Set art_color value."""
        color = np.squeeze(color2vb(value))
        self.shared_program.vert['u_art_color'] = color
        self._art_color = color

    # ----------- WAKE_COLOR -----------
    @property
    def wake_color(self):
        """Get the wake_color value."""
        return self._wake_color

    @wake_color.setter
    @wrap_properties
    def wake_color(self, value):
        """Set wake_color value."""
        color = np.squeeze(color2vb(value))
        self.shared_program.vert['u_wake_color'] = color
        self._wake_color = color

    # ----------- REM_COLOR -----------
    @property
    def rem_color(self):
        """Get the rem_color value."""
        return self._rem_color

    @rem_color.setter
    @wrap_properties
    def rem_color(self, value):
        """Set rem_color value."""
        color = np.squeeze(color2vb(value))
        self.shared_program.vert['u_rem_color'] = color
        self._rem_color = color

    # ----------- N1_COLOR -----------
    @property
    def n1_color(self):
        """Get the n1_color value."""
        return self._n1_color

    @n1_color.setter
    @wrap_properties
    def n1_color(self, value):
        """Set n1_color value."""
        color = np.squeeze(color2vb(value))
        self.shared_program.vert['u_n1_color'] = color
        self._n1_color = color

    # ----------- N2_COLOR -----------
    @property
    def n2_color(self):
        """Get the n2_color value."""
        return self._n2_color

    @n2_color.setter
    @wrap_properties
    def n2_color(self, value):
        """Set n2_color value."""
        color = np.squeeze(color2vb(value))
        self.shared_program.vert['u_n2_color'] = color
        self._n2_color = color

    # ----------- N3_COLOR -----------
    @property
    def n3_color(self):
        """Get the n3_color value."""
        return self._n3_color

    @n3_color.setter
    @wrap_properties
    def n3_color(self, value):
        """Set n3_color value."""
        color = np.squeeze(color2vb(value))
        self.shared_program.vert['u_n3_color'] = color
        self._n3_color = color

    # ----------- TRANSIENT -----------
    @property
    def transient(self):
        """Get the transient value."""
        return self._transient

    @transient.setter
    def transient(self, value):
        """Set transient value."""
        assert isinstance(value, np.ndarray) and len(value) == len(self)
        self._transient = np.full((len(self),), 10., dtype=np.float32)
        idx = transient(value)[0]
        idx_double = np.r_[idx, idx + 1]
        self._transient[idx_double] = value[idx_double]
        self._transient_vbo.set_data(self._transient)

    # ----------- LINE_WIDTH -----------
    @property
    def line_width(self):
        """Get the line_width value."""
        return self._line_width

    @line_width.setter
    @wrap_properties
    def line_width(self, value):
        """Set line_width value."""
        assert isinstance(value, (int, float))
        self._line_width = value

    # ----------- ANTIALIAS -----------
    @property
    def antialias(self):
        """Get the antialias value."""
        return self._antialias

    @antialias.setter
    def antialias(self, value):
        """Set antialias value."""
        assert isinstance(value, bool)
        self._antialias = value

    # ----------- UNICOLOR -----------
    @property
    def unicolor(self):
        """Get the unicolor value."""
        return self._unicolor

    @unicolor.setter
    def unicolor(self, value):
        """Set unicolor value."""
        assert isinstance(value, bool)
        self.shared_program.vert['u_unicolor'] = int(value)
        self._unicolor = value

Hypnogram = create_visual_node(HypogramVisual)  # noqa
