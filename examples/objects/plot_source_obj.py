"""
Source object (SourceObj) : complete tutorial
=============================================

This example illustrate the main functionalities and inputs of the source
object i.e :

    * Add sources with text
    * Control the marker symbol and color
    * Mask sources
    * Analyze anatomical locations of sources using region of interest
    * Color sources according to a data vector or to an anatomical location
    * Display only sources in the left // right hemisphere
    * Force source to fit to a mesh
    * Display only sources inside // outside a mesh

The source objects can interact with several other objects :

    * BrainObj : source's activity and repartition can be projected on the
      surface of the brain
    * RoiObj : source's activity and repartition can be projected on the
      surface of region of interest. In addition, ROI objects can also be used
      to get anatomical informations of sources
"""
import numpy as np

from visbrain.objects import SourceObj, SceneObj, ColorbarObj, BrainObj, RoiObj
from visbrain.io import download_file

###############################################################################
# .. warning::
#     To be clear with the vocabulary used, the SourceObj has a different
#     meaning depending on the recording type. For scalp or intracranial EEG,
#     sources reflect electrode, in MEG it could be sensors or source
#     reconstruction.

###############################################################################
# Download data
###############################################################################
# To illustrate the functionalities of the source object, here, we download an
# intracranial dataset consisting of 583 deep recording sites.

# Download the file and get the (x, y, z) MNI coordinates of the 583 recording
# sites
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
xyz = mat['xyz']
n_sources = xyz.shape[0]
text = ['S' + str(k) for k in range(n_sources)]

###############################################################################
# Scene creation
###############################################################################
# As said in other tutorials, the scene is equivalent with Matplotlib subplots.
# So here, we define a scene that is going to centralize objects in subplots

# Define the default camera state used for each subplot
CAM_STATE = dict(azimuth=0,        # azimuth angle
                 elevation=90,     # elevation angle
                 scale_factor=180  # distance to the camera
                 )
S_KW = dict(camera_state=CAM_STATE)
# Create the scene
sc = SceneObj(size=(1600, 1000))
CBAR_STATE = dict(cbtxtsz=12, txtsz=10., width=.5, cbtxtsh=3.,
                  rect=(1., -2., 1., 4.))

###############################################################################
# Basic source object
###############################################################################
# The first example consist of only plotting the source, without any
# modifications of the inputs

# Create the source objects and add this object to the scene
s_obj_basic = SourceObj('Basic', xyz)
sc.add_to_subplot(s_obj_basic, row=0, col=0, title='Default configuration',
                  **S_KW)

###############################################################################
# Text, symbol and color control
###############################################################################
# Now, we attach text to each source (bold and yellow) and use a gray squares
# symbol

# The color definition could either be uniform (e.g 'green', 'blue'...), a list
# of colors or an array of RGB(A) colors
# s_color = 'blue'  # uniform definition
s_color = ["#D72638"] * 100 + ["#3772FF"] * 100 + ["#008148"] * 200 + \
    ["#C17D11"] * 183  # list definition
# Define the source object and add this object to the scene
s_obj_col = SourceObj('S2', xyz, text=text, text_size=4., text_color='yellow',
                      text_bold=True, color=s_color, symbol='square')
sc.add_to_subplot(s_obj_col, row=0, row_span=2, col=1,
                  title='Text, color and symbol', **S_KW)

###############################################################################
# Assigning data to sources and radius control
###############################################################################
# This example illustrate how to assign some data to sources and how to control
# the dynamic of radius sources

# Create some random data of shape (n_sources,)
rnd_data = np.random.uniform(low=-100, high=100, size=(n_sources,))
# Control the radius range of sources
radius_min = 7.
radius_max = 25.
s_color = np.random.uniform(0., 1., (n_sources, 3))  # array definition
# Define the source object and add this object to the scene
s_rad = SourceObj('rad', xyz, color=s_color, data=rnd_data,
                  radius_min=radius_min, radius_max=radius_max)
sc.add_to_subplot(s_rad, row=0, col=2, title='Assigning data to sources ',
                  **S_KW)

###############################################################################
# Mask sources
###############################################################################
# Sometimes, it could be usefull to mask some sources and display those sources
# with a different color (using `mask_color`).

# Define the mask for sources that have a x coordinate between [-20, 20] and
# set the color of those masked sources to orange
mask = np.logical_and(xyz[:, 0] >= -20., xyz[:, 0] <= 20.)
mask_color = 'orange'
s_obj_mask = SourceObj('S3', xyz, mask=mask, mask_color=mask_color,
                       color=s_color, data=rnd_data, radius_min=radius_min,
                       radius_max=radius_max)
sc.add_to_subplot(s_obj_mask, row=0, col=3,
                  title='Masked sources between [-20., 20.]\nare orange',
                  **S_KW)

###############################################################################
# Get anatomical informations of sources
###############################################################################
# The region of interest object (RoiObj) is basically a volume where each voxel
# is known to be part of an anatomical region. Hence, you can define the RoiObj
# and use it to get the anatomical informations of each source

# First, create a basic source object
s_obj_ba = SourceObj('S4', xyz)
# Then, we define a region of interest object (RoiObj). We use brodmann areas
# but you should take a look to the complete tutorial on ROIs because visbrain
# povides several templates (Brodmann, AAL, Talairach and MIST)
roi_obj = RoiObj('brodmann')
# If you want to see labels associated with the brodmann areas, uncomment the
# following line
# print(roi_obj.get_labels())
# Now, analyse sources using the RoiObj. The argument returned by the
# `SourceObj.analyse_sources` method is a Pandas dataframe
df_brod = s_obj_ba.analyse_sources(roi_obj=roi_obj)
# The dataframe contains a column `brodmann` which is the name of the
# associated brodmann area. Hence, we use it to color sources according to the
# name of brodmann area
s_obj_ba.color_sources(analysis=df_brod, color_by='brodmann')
# Finally, add the object to the scene
sc.add_to_subplot(s_obj_ba, row=1, col=0,
                  title='Color sources according to\n Brodmann area', **S_KW)

###############################################################################
# Color sources, using predefined colors, according to the AAL location
###############################################################################
# Similarly to the example above, here, we color sources according to the
# Automated Anatomical Labeling (AAL)

"""Analyse where sources are located using the AAL ROI template and color
only the precentral left (green), right (orange), insula right (blue). Others
ROI are turn into white.
"""
# Create a basic source object
s_obj_aal = SourceObj('S5', xyz)
# Define the RoiObj using AAL and analyse sources locations
roi_obj = RoiObj('aal')
# print(roi_obj.get_labels())
df_aal = s_obj_aal.analyse_sources(roi_obj='aal')
# Then, define one color per ROI and color others in gray
aal_col = {'Precentral (R)': 'green',
           'Precentral (L)': 'orange',
           'Insula (R)': 'blue'}
color_others = 'gray'
# Color sources and add the object to the scene
s_obj_aal.color_sources(analysis=df_aal, color_by='aal', roi_to_color=aal_col,
                        color_others=color_others)
sc.add_to_subplot(s_obj_aal, row=1, col=2,
                  title='Color only sources in\n precentral and insula',
                  **S_KW)

###############################################################################
# Color sources according to data
###############################################################################
# A more simple example, but it's also possible to color your sources
# according to a data vector

# Define the source object
s_obj_data = SourceObj('S3', xyz, data=rnd_data, radius_min=radius_min,
                       radius_max=radius_max)
# Color sources according to a data vector
s_obj_data.color_sources(data=rnd_data, cmap='viridis', clim=(-100, 100),)
# Get the colorbar of the source object
cb_data = ColorbarObj(s_obj_data, cblabel='Random data', border=False,
                      **CBAR_STATE)
# Add the source and colorbar objects to the scene
sc.add_to_subplot(s_obj_data, row=1, col=3, title='Color sources using data',
                  **S_KW)
sc.add_to_subplot(cb_data, row=1, col=4, width_max=60)

###############################################################################
# Project source's activity on the surface of the brain
###############################################################################
# As explained in the BrainObj tutorial, source's activity can be projected on
# the surface of the brain which can be particularly convenient for represent
# source's activity across several intracranially implanted subjects

# Define the source and brain objects
s_proj = SourceObj('proj', xyz, data=rnd_data)
b_proj = BrainObj('B3', translucent=False)
# Project source's activity on the surface of the brain
s_proj.project_sources(b_proj, cmap='inferno')
sc.add_to_subplot(b_proj, row=2, col=0, title="Project source's activity")

###############################################################################
# Project masked source's activity on the surface of the brain
###############################################################################
# This is the exact same example as above, except that we also project masked
# sources

# Define the source and brain objects
s_mask = SourceObj('mask', xyz, data=rnd_data, mask=mask, mask_color='gray')
b_mask = BrainObj('B3', translucent=False)
# Project source's activity on the surface of the brain
s_mask.project_sources(b_mask, cmap='viridis', radius=15.)
sc.add_to_subplot(b_mask, row=2, col=1,
                  title="Project masked source's activity")

###############################################################################
# Project source's activity on the surface of the DMN
###############################################################################
# Here, we first use the MIST ROI to get represent the default mode network and
# then, we project source's activity onto the surface of the DMN

# Define the source and brain objects
s_dmn = SourceObj('dmn', xyz, data=rnd_data, mask=mask, mask_color='gray')
b_mask = BrainObj('B3')
# Define the MIST roi object
roi_dmn = RoiObj('mist_7')
# print(roi_dmn.get_labels())
# Get the index of the DMN and get the mesh
dmn_idx = roi_dmn.where_is('Default mode network')
roi_dmn.select_roi(dmn_idx)
# Project source's activity on the surface of the DMN
s_dmn.project_sources(roi_dmn, cmap='viridis', radius=15.)
sc.add_to_subplot(b_mask, row=2, col=2, use_this_cam=True, row_span=2,
                  title="Project source's activity\non the DMN")
sc.add_to_subplot(roi_dmn, row=2, col=2, row_span=2)

###############################################################################
# Project source's repartition on the surface of the brain
###############################################################################
# Similarly to the example above, we project here the repartition of sources
# which mean the number of contributing sources per vertex

# Define the source and brain objects
s_rep = SourceObj('proj', xyz, data=rnd_data)
b_rep = BrainObj('B3', translucent=False)
# Project source's activity on the surface of the brain
s_rep.project_sources(b_rep, cmap='viridis', project='repartition')
# Get the colorbar of the brain object
cb_rep = ColorbarObj(b_rep, cblabel='Number of sources\nper vertex',
                     border=False, **CBAR_STATE)
sc.add_to_subplot(b_rep, row=2, col=3, title="Project source's repartition")
sc.add_to_subplot(cb_rep, row=2, col=4)

###############################################################################
# Display only sources in the left hemisphere
###############################################################################
# In this little example, we illustrate how to only display sources in the left
# hemisphere

# Define the source object
s_obj_left = SourceObj('S_left', xyz, color='#ab4642')
# Select only sources that belong to the left hemisphere and add the object to
# the scene
s_obj_left.set_visible_sources('left')
sc.add_to_subplot(s_obj_left, row=3, col=0,
                  title='Display sources in left hemisphere', **S_KW)

###############################################################################
# Force sources to fit to the surface of the brain
###############################################################################
# First, we force sources to fit to the white matter of the brain. Then, we use
# the talaich ROI to identify which sources belong to the left or right
# hemisphere and color them accordingly

# Define the Brain and Source objects
s_obj_fit = SourceObj('Fit', xyz, symbol='diamond')
b_obj_fit = BrainObj('white', translucent=True)
# Get the vertices of the brain object and force sources to fit to those
# vertices
b_obj_vert = b_obj_fit.vertices
s_obj_fit.fit_to_vertices(b_obj_vert)
# Analyse source's anatomical location using the Talairach atlas
df_tal = s_obj_fit.analyse_sources(roi_obj='talairach')
# Color sources accordingly to the hemisphere (left='purple', right='yellow')
s_obj_fit.color_sources(analysis=df_tal, color_by='hemisphere',
                        roi_to_color={'Left': 'purple', 'Right': 'yellow'})
# Finally, add those objects to the scene
sc.add_to_subplot(s_obj_fit, row=3, col=1,
                  title="Force sources to fit to the\nsurface of the brain")
sc.add_to_subplot(b_obj_fit, row=3, col=1, use_this_cam=True)

###############################################################################
# Display only sources inside the brain
###############################################################################
# In this little example, we illustrate how to only display sources inside the
# brain

s_obj_inside = SourceObj('In', xyz, symbol='cross', color='firebrick')
s_obj_inside.set_visible_sources('inside', b_obj_vert)
sc.add_to_subplot(s_obj_inside, row=3, col=3,
                  title='Display only sources inside the brain', **S_KW)

###############################################################################
# Take a screenshot of the scene
###############################################################################

# Screenshot of the scene
# sc.screenshot('ex_source_obj.png', transparent=True)

# If you need, you can link the rotation off all cameras but this can
# considerably slow down visualization updates
# sc.link(-1)

# Display the scene
sc.preview()
