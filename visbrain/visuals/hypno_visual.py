"""Display signals into a grid..

A large portion of this code was taken from the example developped by the vispy
team :
https://github.com/vispy/vispy/blob/master/examples/demo/gloo/realtime_signals.py
"""
import numpy as np

from vispy import gloo, visuals
from vispy.visuals.shaders import Function
from vispy.scene.visuals import create_visual_node

from visbrain.io import is_opengl_installed
from visbrain.utils import vispy_array, wrap_properties, color2vb


__all__ = ('Hypnogram')


vec2to4 = Function("""
    vec4 vec2to4(vec2 inp) {
        return vec4(inp, 0, 1);
    }
""")

vertex_shader = """
#version 120
varying vec4 pos;
varying vec4 v_color;

void main() {

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
    """

    def __len__(self):
        """Return the number of time points."""
        return self._n

    def __init__(self, data, time=None, art=-1, wake=0, n1=1, n2=2, n3=3,
                 rem=4, art_visual=1, wake_visual=0, rem_visual=-1,
                 n1_visual=-2, n2_visual=-3, n3_visual=-4, art_color='#8bbf56',
                 wake_color='#56bf8b', rem_color='#bf5656', n1_color='#aabcce',
                 n2_color='#405c79', n3_color='#0b1c2c', line_width=2.):
        """Init."""
        # =========================== VISUALS ===========================
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        self.set_gl_state('translucent', depth_test=True, cull_face=False,
                          blend=True, blend_func=('src_alpha',
                                                  'one_minus_src_alpha'))
        self._draw_mode = 'line_strip'

        # =========================== BUFFERS ===========================
        pos = np.random.rand(1, 2).astype(np.float32)
        self._position = gloo.VertexBuffer(pos)
        self.shared_program.vert['position'] = self._position
        self._program.vert['to_vec4'] = vec2to4
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
        self.set_data(data, time, line_width)
        self.freeze()

    def set_data(self, data, time=None, line_width=None):
        """Set data to the grid of signals.

        Parameters
        ----------
        """
        data = np.asarray(data)
        assert data.ndim == 1
        self._n = len(data)
        time = np.arange(len(data)) if time is None else np.asarray(time)
        assert len(time) == len(self)

        self.line_width = line_width

        #
        data_time = vispy_array(np.c_[time, data])
        self._position.set_data(data_time)

    def _prepare_transforms(self, view):
        """Call for the first rendering."""
        tr = view.transforms
        view_vert = view.view_program.vert
        view_vert['transform'] = tr.get_transform()

    def _prepare_draw(self, view=None):
        """Function called everytime there's a camera update."""
        pass
        # try:
        #     import OpenGL.GL as GL
        #     GL.glLineWidth(self._width)
        #     if self._smooth_line:
        #         GL.glEnable(GL.GL_LINE_SMOOTH)
        #     else:
        #         GL.glDisable(GL.GL_LINE_SMOOTH)
        # except Exception:  # can be other than ImportError sometimes
        #     pass

    # ========================================================================
    # ========================================================================
    # PROPERTIES
    # ========================================================================
    # ========================================================================
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

    # ----------- LINE_WIDTH -----------
    @property
    def line_width(self):
        """Get the line_width value."""
        return self._line_width

    @line_width.setter
    @wrap_properties
    def line_width(self, value):
        """Set line_width value."""
        if is_opengl_installed() and isinstance(value, (int, float)):
            import OpenGL.GL as GL
            GL.glLineWidth(max(value, 1.))
            self._line_width = value


Hypnogram = create_visual_node(HypogramVisual)  # noqa


if __name__ == '__main__':
    from vispy import scene, app
    from visbrain.objects.scene_obj import VisbrainCanvas

    data = np.repeat(np.arange(6), 100) - 1.
    time = np.arange(len(data)) / 1024.
    print(data.min(), data.max())

    rect = (time.min(), -4.5, time.max(), 6)
    cam = scene.cameras.PanZoomCamera(rect=rect)

    vb = VisbrainCanvas(axis=True, show=True, camera=cam)

    h = Hypnogram(data, time=time, parent=vb.wc.scene, line_width=10.)
    # h = scene.visuals.Line(np.c_[time, data])
    # h.parent = vb.parent

    # can.show()
    app.run()
