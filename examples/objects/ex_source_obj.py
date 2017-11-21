"""
Source object
=============

This example illustrate the main functionalities and inputs of the source
object i.e :

    * Add sources with text
    * Control the marker symbol and color
    * Mask sources
    * Analyse anatomical locations of sources using either the Brodmann, AAL or
      Talairach atlas
    * Color sources according to a data vector or to an anatomical location
    * Display only sources in the left // right hemisphere
    * Force source to fit to a mesh
    * Display only sources inside // outside a mesh

.. image:: ../../picture/picobjects/ex_source_obj.png
"""
import numpy as np

from vispy.geometry import create_sphere

from visbrain.objects import SourceObj, SceneObj
from visbrain.io import download_file, path_to_visbrain_data

"""
Load the xyz coordinates and corresponding subject name
"""
download_file('xyz_sample.npz')
mat = np.load(path_to_visbrain_data('xyz_sample.npz'))
xyz = mat['xyz']
n_sources = xyz.shape[0]
text = ['S' + str(k) for k in range(n_sources)]

"""Create a scene. By default, we fix the top view of the camera
"""
cam_state = dict(azimuth=0,        # azimuth angle
                 elevation=90,     # elevation angle
                 scale_factor=180  # ~distance to the camera
                 )
sc = SceneObj(camera_state=cam_state, size=(1200, 1000))

"""Create the most basic source object
"""
s_obj_basic = SourceObj('Basic', xyz, text=text, text_bold=True,
                        text_color='yellow')
sc.add_to_subplot(s_obj_basic, row=0, col=0,
                  title='Default configuration with text')

"""Control the color and the symbol
"""
s_obj_col = SourceObj('S2', xyz, color='slategray', symbol='square')
sc.add_to_subplot(s_obj_col, row=0, col=1, title='Change color and symbol')

"""Mask sources that have a x coordinate between [-20, 20] and color it into
orange
"""
mask = np.logical_and(xyz[:, 0] >= -20., xyz[:, 0] <= 20.)
data = np.random.rand(n_sources)
s_obj_mask = SourceObj('S3', xyz, mask=mask, mask_color='orange',
                       color='slateblue', data=data, radius_min=2.,
                       radius_max=20.)
sc.add_to_subplot(s_obj_mask, row=0, col=2,
                  title='Mask sources between [-20., 20.]')

"""Use a random data vector to color sources
"""
data = np.random.rand(n_sources)
s_obj_data = SourceObj('S3', xyz, data=data)
s_obj_data.color_sources(data=data, cmap='plasma')
sc.add_to_subplot(s_obj_data, row=1, col=0, title='Color sources using data')

"""Analyse where sources are located using the Brodmann ROI template and color
sources according to the Brodmann area
"""
s_obj_ba = SourceObj('S4', xyz)
df_brod = s_obj_ba.analyse_sources(roi_obj='brodmann')
s_obj_ba.color_sources(analysis=df_brod, color_by='brodmann')
sc.add_to_subplot(s_obj_ba, row=1, col=1,
                  title='Color sources according to Brodmann area')

"""Analyse where sources are located using the AAL ROI template and color
only the precentral left (green), right (orange), insula right (blue). Others
ROI are turn into white.
"""
s_obj_aal = SourceObj('S5', xyz)
df_aal = s_obj_aal.analyse_sources(roi_obj='aal')
aal_col = {'Precentral (R)': 'green',
           'Precentral (L)': 'orange',
           'Insula (R)': 'blue'}
s_obj_aal.color_sources(analysis=df_aal, color_by='aal', roi_to_color=aal_col,
                        color_others='white')
sc.add_to_subplot(s_obj_aal, row=1, col=2,
                  title='Color only sources in precentral and insula')

"""Display only sources in the left hemisphere
"""
s_obj_left = SourceObj('S_left', xyz, color='#ab4642')
s_obj_left.set_visible_sources('left')
sc.add_to_subplot(s_obj_left, row=2, col=0,
                  title='Display sources in left hemisphere')

"""Create a sphere using VisPy
"""
sphere = create_sphere(rows=100, cols=100, radius=50)
sphere_vertices = sphere.get_vertices()

"""Force sources to fit on the vertices of the sphere. Then, we color sources
according to the hemisphere (left=purple, right=yellow)
"""
s_obj_fit = SourceObj('Fit', xyz, symbol='diamond')
s_obj_fit.fit_to_vertices(sphere_vertices)
df_tal = s_obj_fit.analyse_sources(roi_obj='talairach')
s_obj_fit.color_sources(analysis=df_tal, color_by='hemisphere',
                        roi_to_color={'Left': 'purple', 'Right': 'yellow'})
sc.add_to_subplot(s_obj_fit, row=2, col=1,
                  title="Force sources to fit on a sphere")

"""Use the same sphere to display only sources that are inside
"""
s_obj_inside = SourceObj('In', xyz, symbol='cross', color='firebrick')
s_obj_inside.set_visible_sources('inside', sphere_vertices)
sc.add_to_subplot(s_obj_inside, row=2, col=2,
                  title='Display only sources inside a sphere')

"""If you need, you can link the rotation off all cameras but this can
considerably slow down visualization updates
"""
# sc.link(-1)

"""Display the scene
"""
sc.preview()
