"""Temporaly patch for VisPy markers."""
import logging
import vispy

logger = logging.getLogger('visbrain')

vert_markers_patch = """
uniform float u_antialias;
uniform float u_px_scale;
uniform float u_scale;

attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_edgewidth;
attribute float a_size;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_antialias;

void main (void) {
    if (a_size != 0.)
    {
    $v_size = a_size * u_px_scale * u_scale;
    v_edgewidth = a_edgewidth * float(u_px_scale);
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = $transform(vec4(a_position,1.0));
    float edgewidth = max(v_edgewidth, 1.0);
    gl_PointSize = ($v_size) + 4.*(edgewidth + 1.5*v_antialias);
    }
}
"""

vispy.visuals.markers.vert = vert_markers_patch
logger.debug("Remove markers patch in visuals and SourceObj")
