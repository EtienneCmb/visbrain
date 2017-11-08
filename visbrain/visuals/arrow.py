"""Base class for 3-D updated arrows."""
from __future__ import division

import numpy as np

from vispy import gloo
from vispy.visuals import Visual
from vispy.visuals.line import LineVisual
from vispy.scene.visuals import create_visual_node
from vispy.color import Color, ColorArray, get_colormap
from vispy.ext.six import string_types
from vispy.visuals.shaders import Function


vert = """
#include "math/constants.glsl"

// Uniforms
// ------------------------------------
uniform float antialias;

// Attributes
// ------------------------------------
attribute vec3  v1;
attribute vec3  v2;
attribute float size;
attribute vec4  color;
attribute float linewidth;

// Varyings
// ------------------------------------
varying float v_size;
varying float v_point_size;
varying vec4  v_color;
varying vec3  v_orientation;
varying float v_antialias;
varying float v_linewidth;

// Main (hooked)
// ------------------------------------
void main (void)
{
    v_size        = size;
    v_point_size  = M_SQRT2 * size + 2.0 * (linewidth + 2.0*antialias);
    v_antialias   = antialias;
    v_color       = color;
    v_linewidth   = linewidth;

    vec3 body = $transform(vec4(v2 - v1, 0.)).xyz;
    v_orientation = (body / length(body));

    gl_Position = $transform(vec4(v2, 1));
    gl_PointSize = v_point_size;
}
"""

frag = """
#include "math/constants.glsl"
#include "arrowheads/arrowheads.glsl"
#include "antialias/antialias.glsl"

// Varyings
// ------------------------------------
varying float v_size;
varying float v_point_size;
varying vec4  v_color;
varying vec3  v_orientation;
varying float v_antialias;
varying float v_linewidth;

void main()
{
    // 1. Move the origin to the center of the point
    // 2. Rotate the canvas for drawing the arrow
    // 3. Scale the coordinates with v_point_size
    vec2 P = gl_PointCoord.xy - vec2(0.5, 0.5);
    P = vec2(v_orientation.x*P.x - v_orientation.y*P.y,
             v_orientation.y*P.x + v_orientation.x*P.y) * v_point_size;

    float distance = arrow_$arrow_type(P, v_size, v_linewidth, v_antialias);
    gl_FragColor = $fill_type(distance, v_linewidth, v_antialias, v_color,
                              v_color);
}
"""


ARROW_TYPES = [
    'stealth',
    'curved',
    'angle_30',
    'angle_60',
    'angle_90',
    'triangle_30',
    'triangle_60',
    'triangle_90',
    'inhibitor_round'
]


class _ArrowHeadVisual(Visual):
    """Arrow head visual.

    ArrowHeadVisual: several shapes to put on the end of a line.
    This visual differs from MarkersVisual in the sense that this visual
    calculates the orientation of the visual on the GPU, by calculating the
    tangent of the line between two given vertices.
    This is not really a visual you would use on your own,
    use :class:`ArrowVisual` instead.

    Parameters
    ----------
    parent : ArrowVisual
        This actual ArrowVisual this arrow head is part of.
    """

    _arrow_vtype = np.dtype([
        ('v1', np.float32, 3),
        ('v2', np.float32, 3),
        ('size', np.float32, 1),
        ('color', np.float32, 4),
        ('linewidth', np.float32, 1)
    ])

    def __init__(self, parent):
        Visual.__init__(self, vert, frag)
        self._parent = parent
        self.set_gl_state(depth_test=False, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'points'

        self._arrow_vbo = gloo.VertexBuffer(
            np.array([], dtype=self._arrow_vtype))

    def _prepare_transforms(self, view):
        xform = view.transforms.get_transform()
        view.view_program.vert['transform'] = xform

    def _prepare_draw(self, view=None):
        if self._parent._arrows_changed:
            self._prepare_vertex_data()
        self.shared_program.bind(self._arrow_vbo)
        self.shared_program['antialias'] = 1.0
        self.shared_program.frag['arrow_type'] = self._parent.arrow_type
        self.shared_program.frag['fill_type'] = 'filled'

    def _prepare_vertex_data(self):
        arrows = self._parent.arrows

        if arrows is None or arrows.size == 0:
            self._arrow_vbo = gloo.VertexBuffer(
                np.array([], dtype=self._arrow_vtype))
            return

        v = np.zeros(len(arrows), dtype=self._arrow_vtype)
        v['v1'] = arrows[:, 0:3]
        v['v2'] = arrows[:, 3:6]
        v['size'][:] = self._parent.arrow_size
        v['color'][:] = self._interpret_color(self._parent.arrow_color)
        v['linewidth'][:] = self._parent.width
        self._arrow_vbo = gloo.VertexBuffer(v)

    @staticmethod
    def _interpret_color(color):
        if isinstance(color, string_types):
            try:
                colormap = get_colormap(color)
                color = Function(colormap.glsl_map)
            except KeyError:
                color = Color(color).rgba
        elif isinstance(color, Function):
            color = Function(color)
        else:
            color = ColorArray(color).rgba
            if len(color) == 1:
                color = color[0]
        return color


class ArrowVisual(LineVisual):
    """Arrow visual.

    A special line visual which can also draw optional arrow heads at the
    specified vertices.
    You add an arrow head by specifying two vertices `v1` and `v2` which
    represent the arrow body. This visual will draw an arrow head using `v2`
    as center point, and the orientation of the arrow head is automatically
    determined by calculating the direction vector between `v1` and `v2`.

    Parameters
    ----------
    pos : array
        Array of shape (..., 2) or (..., 3) specifying vertex coordinates.
    color : Color, tuple, or array
        The color to use when drawing the line. If an array is given, it
        must be of shape (..., 4) and provide one rgba color per vertex.
        Can also be a colormap name, or appropriate `Function`.
    width:
        The width of the line in px. Line widths > 1px are only
        guaranteed to work when using 'agg' method.
    connect : str or array
        Determines which vertices are connected by lines.
            * "strip" causes the line to be drawn with each vertex
              connected to the next.
            * "segments" causes each pair of vertices to draw an
              independent line segment
            * numpy arrays specify the exact set of segment pairs to
              connect.
    method : str
        Mode to use for drawing.
            * "agg" uses anti-grain geometry to draw nicely antialiased lines
              with proper joins and endcaps.
            * "gl" uses OpenGL's built-in line rendering. This is much faster,
              but produces much lower-quality results and is not guaranteed to
              obey the requested line width or join/endcap styles.
    antialias : bool
        Enables or disables antialiasing.
        For method='gl', this specifies whether to use GL's line smoothing,
        which may be unavailable or inconsistent on some platforms.
    arrows : array
        A Nx4 matrix where each row contains the x and y coordinate of the
        first and second vertex of the arrow body. Remember that the second
        vertex is used as center point for the arrow head, and the first
        vertex is only used for determining the arrow head orientation.
    arrow_type : string
        Specify the arrow head type, the currently available arrow head types
        are:
            * stealth
            * curved
            * triangle_30
            * triangle_60
            * triangle_90
            * angle_30
            * angle_60
            * angle_90
            * inhibitor_round
    arrow_size : float
        Specify the arrow size
    """

    def __init__(self, pos=None, color=(.5, .5, .5, 1.), width=1.,
                 connect='strip', method='gl', antialias=False, arrows=None,
                 arrow_type='stealth', arrow_size=None,
                 arrow_color=(.5, .5, .5, 1.)):
        """Init."""
        # Do not use the self._changed dictionary as it gets overwritten by
        # the LineVisual constructor.
        self._arrows_changed = False

        self._arrow_type = None
        self._arrow_size = None
        self._arrows = None

        self.arrow_type = arrow_type
        self.arrow_size = arrow_size
        self.arrow_color = arrow_color

        self.arrow_head = _ArrowHeadVisual(self)

        # TODO: `LineVisual.__init__` also calls its own `set_data` method,
        # which triggers an *update* event. This results in a redraw. After
        # that we call our own `set_data` method, which triggers another
        # redraw. This should be fixed.
        LineVisual.__init__(self, pos, color, width, connect, method,
                            antialias)
        self.set_gl_state('translucent', depth_test=True)
        ArrowVisual.set_data(self, arrows=arrows)

        # Add marker visual for the arrow head
        self.add_subvisual(self.arrow_head)

    def set_data(self, pos=None, color=None, width=None, connect=None,
                 arrows=None):
        """Set the data used for this visual.

        Parameters
        ----------
        pos : array
            Array of shape (..., 2) or (..., 3) specifying vertex coordinates.
        color : Color, tuple, or array
            The color to use when drawing the line. If an array is given, it
            must be of shape (..., 4) and provide one rgba color per vertex.
            Can also be a colormap name, or appropriate `Function`.
        width:
            The width of the line in px. Line widths > 1px are only
            guaranteed to work when using 'agg' method.
        connect : str or array
            Determines which vertices are connected by lines.
                * "strip" causes the line to be drawn with each vertex
                  connected to the next.
                * "segments" causes each pair of vertices to draw an
                  independent line segment
                * numpy arrays specify the exact set of segment pairs to
                  connect.
        arrows : array
            A Nx4 matrix where each row contains the x and y coordinate of the
            first and second vertex of the arrow body. Remember that the second
            vertex is used as center point for the arrow head, and the first
            vertex is only used for determining the arrow head orientation.
        """
        if arrows is not None:
            self._arrows = arrows
            self._arrows_changed = True

        LineVisual.set_data(self, pos, color, width, connect)

    @property
    def arrow_type(self):
        """Get the arrow type."""
        return self._arrow_type

    @arrow_type.setter
    def arrow_type(self, value):
        if value not in ARROW_TYPES:
            raise ValueError(
                "Invalid arrow type '{}'. Should be one of {}".format(
                    value, ", ".join(ARROW_TYPES)
                )
            )

        if value == self._arrow_type:
            return

        self._arrow_type = value
        self._arrows_changed = True

    @property
    def arrow_size(self):
        """Get the arrow size."""
        return self._arrow_size

    @arrow_size.setter
    def arrow_size(self, value):
        if value is None:
            self._arrow_size = 5.0
        else:
            if value <= 0.0:
                raise ValueError("Arrow size should be greater than zero.")

            self._arrow_size = value

        self._arrows_changed = True

    @property
    def arrows(self):
        """Get the arrows coordinates."""
        return self._arrows

Arrow = create_visual_node(ArrowVisual)  # noqa
