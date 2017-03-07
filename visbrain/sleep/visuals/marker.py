
import numpy as np
from warnings import warn

from vispy import gloo
from vispy.scene import visuals
from vispy.visuals import Visual

# from ...utils import color2vb
from visbrain.utils import color2vb

__all__ = ['Markers']

VERT_SHADER = """
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;
void main (void) {
    v_radius = $a_size;
    v_linewidth = 1.0;
    v_antialias = 1.0;
    v_fg_color  = vec4(0.0,0.0,0.0,0.5);
    v_bg_color  = $a_color;
    gl_Position = vec4($a_position, 0.0, 1.0);
    gl_PointSize = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
}
"""

FRAG_SHADER = """
#version 120
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;
void main()
{
    float size = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;
    float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
    float d = abs(r - v_radius) - t;
    if( d < 0.0 )
        gl_FragColor = v_fg_color;
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > v_radius)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""


class MarkerVisual(Visual):
    """
    """

    def __init__(self, pos, color='white', size=5.):
        """Init."""
        # Initialize the vispy.Visual class with the vertex / fragment buffer :
        Visual.__init__(self, VERT_SHADER, FRAG_SHADER)

        # Check position :
        if (pos.ndim is not 2) or (pos.shape[1] is not 2):
            raise ValueError("po must be a (n, 2) array")
        # Check color :
        if not isinstance(color, np.ndarray):
            v_color = color2vb(color, length=pos.shape[0], alpha=0.5)
        elif isinstance(color, np.ndarray) and (color.shape[0] is not
                                                pos.shape[0]):
            raise ValueError("The length of the color array must have the same"
                             " length as pos.")
        print(v_color.shape)

        # Color conversion :
        v_color = np.ascontiguousarray(v_color).astype(np.float32)
        v_position = np.ascontiguousarray(pos).astype(np.float32)
        v_size = np.ascontiguousarray([size] * pos.shape[0]).astype(np.float32)

        # Set uniform and attribute
        self._colBuffer = gloo.VertexBuffer(v_color)
        self._posBuffer = gloo.VertexBuffer(v_position)
        self._sizeBuffer = gloo.VertexBuffer(v_size)
        self.set_gl_state('translucent', depth_test=False, cull_face=False)

        self.shared_program.vert['a_position'] = self._posBuffer
        self.shared_program.vert['a_color'] = self._colBuffer
        self.shared_program.vert['a_size'] = self._sizeBuffer

        self._draw_mode = 'points'

        self.freeze()

    def set_data(pos, color='white'):
        """
        """
        pass

    def _prepare_transforms(self, view):
        """This is call for the first rendering."""


Markers = visuals.create_visual_node(MarkerVisual)

# if __name__ == '__main__':
#     from vispy.scene import SceneCanvas
#     from vispy import app
#     import sys

#     canvas = SceneCanvas(keys='interactive', title='plot3d', show=True)
#     wc = canvas.central_widget.add_view()
#     pos = np.random.rand(100, 2)
#     m = Markers(pos, parent=wc.scene)
#     print(dir(m))

#     if sys.flags.interactive != 1:
#         app.run()