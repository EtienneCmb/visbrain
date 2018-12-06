"""
Topoplot object (TopoObj) : complete tutorial
=============================================

This example illustrate the main functionalities and inputs of the topoplot
object i.e :

  * Use channel names or position to identify which channels are used
  * Main color and appearance properties
  * Display levels (either regulary spaced and based on a colormap or custom
    levels with custom colors)
  * Display connectivity
"""
import numpy as np

from visbrain.objects import TopoObj, ColorbarObj, SceneObj
from visbrain.io import download_file

###############################################################################
# Download data
###############################################################################
# First, we download the data. A directory should be created to
# ~/visbrain_data/example_data. This example contains beta power for several
# channels defined by there xy coordinates.

path = download_file('topoplot_data.npz', astype='example_data')
mat = np.load(path)
xy, data = mat['xyz'], mat['data']
channels = [str(k) for k in range(len(data))]
# Plotting properties shared across topoplots and colorbar :
kw_top = dict(margin=15 / 100, chan_offset=(0., 0.1, 0.), chan_size=10)
kw_cbar = dict(cbtxtsz=12, txtsz=10., width=.3, txtcolor='black', cbtxtsh=1.8,
               rect=(0., -2., 1., 4.), border=False)

###############################################################################
# Creation of the scene
###############################################################################
# Create a scene with a white background

sc = SceneObj(bgcolor='white', size=(1600, 900))

###############################################################################
# Topoplot based on channel names
###############################################################################
# First definition using channel names only

# Define some EEG channels and set one data value per channel
ch_names = ['C3', 'C4', 'Cz', 'Fz', 'Pz']
data_names = [10, 20, 30, 10, 10]
# Create the topoplot and the associated colorbar
t_obj = TopoObj('topo', data_names, channels=ch_names, **kw_top)
cb_obj = ColorbarObj(t_obj, cblabel='Colorbar label', **kw_cbar)
# Add both objects to the scene
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj, row=0, col=0, title='Definition using channel names',
                  title_color='black', width_max=400)
sc.add_to_subplot(cb_obj, row=0, col=1, width_max=100)

###############################################################################
# Topoplot based on channel (x, y) coordinates
###############################################################################
# Second definition using channel (x, y) coordinates

# Create the topoplot and the object :
t_obj_1 = TopoObj('topo', data, channels=channels, xyz=xy, cmap='bwr',
                  clim=(2., 3.), **kw_top)
cb_obj_1 = ColorbarObj(t_obj_1, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_1, row=0, col=2, title_color='black', width_max=400,
                  title='Definition using channel coordinates')
sc.add_to_subplot(cb_obj_1, row=0, col=3, width_max=100)

###############################################################################
# Custom extrema colors
###############################################################################
# Here, we use custom colors for extrema i.e every values under `vmin=2.` is
# going to be set to the color 'slateblue' and every values over `vmax=2.8` to
# 'green'

# Define the topoplot object
t_obj_2 = TopoObj('topo', data, xyz=xy, cmap='inferno', vmin=2.,
                  under='slateblue', vmax=2.8, over='olive',
                  **kw_top)
# Get the colorbar based on the color properties of the topoplot :
cb_obj_2 = ColorbarObj(t_obj_2, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_2, row=0, col=4, title='Custom extrema colors',
                  title_color='black', width_max=400)
sc.add_to_subplot(cb_obj_2, row=0, col=5, width_max=100)

###############################################################################
# Connect channels
###############################################################################
# To connect channels together, we need a 2D array of shape
# (n_channels, n_channels) describing connectivity strength between channels.
# Note that the `visbrain.objects.TopoObj.connect` method basically use the
# `visbrain.objects.ConnectObj` object.

# Create the topoplot and colorbar objects
t_obj_3 = TopoObj('topo', data, xyz=xy, cmap='Spectral_r', **kw_top)
cb_obj_3 = ColorbarObj(t_obj_3, cblabel='Beta power', **kw_cbar)
# Create the 2D array of connectivity links :
connect = (data.reshape(-1, 1) + data.reshape(1, -1)) / 2.
# Select only connectivity links with a connectivity strength under 1.97
select = connect < 1.97
# Connect the selected channels :
t_obj_3.connect(connect, select=select, cmap='inferno', antialias=True,
                line_width=4.)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_3, row=1, col=4, title='Display connectivity',
                  title_color='black', width_max=400)
sc.add_to_subplot(cb_obj_3, row=1, col=5, width_max=100)

###############################################################################
# Topoplot with regulary spaced levels
###############################################################################
# Here, we create a topoplot with 10 regulary spaced levels. The color of each
# level is based on the 'bwr' colormap. Note that in order to work properly,
# you need to install `scikit-image <https://scikit-image.org/>`_

# Create the topoplot object :
t_obj_4 = TopoObj('topo', data, xyz=xy, levels=10, level_colors='bwr',
                  **kw_top)
# Get the colorbar based on the color properties of the topoplot :
cb_obj_4 = ColorbarObj(t_obj_4, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_4, row=1, col=0, title='Regulary spaced levels',
                  title_color='black', width_max=400)
sc.add_to_subplot(cb_obj_4, row=1, col=1, width_max=100)

###############################################################################
# Topoplot with custom levels
###############################################################################
# The only difference with the previous plot is that levels are not regulary
# spaced anymore but they are manually defined, just as color.

# First level is going to be red, the second one green and the last one blue
level_colors = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
levels = [2., 2.2, 2.5]
# Create the topoplot object :
t_obj_5 = TopoObj('topo', data, xyz=xy, levels=levels,
                  level_colors=level_colors, chan_mark_symbol='cross',
                  line_width=7., chan_mark_color='gray', cmap='plasma',
                  line_color='#3498db', **kw_top)
# Get the colorbar based on the color properties of the topoplot :
cb_obj_5 = ColorbarObj(t_obj_5, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_5, row=1, col=2, title='Custom levels',
                  title_color='black')
sc.add_to_subplot(cb_obj_5, row=1, col=3, width_max=100)

# Finally, display the scene
sc.preview()
