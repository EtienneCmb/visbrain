"""
Plotting properties
===================

Display topographic plots in a grid using several plotting properties.

.. image:: ../../picture/pictopo/ex_topoplot_plotting_properties.png
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
xyz, data = mat['xyz'], mat['data']
channels = [str(k) for k in range(len(data))]
# Plotting properties shared across topoplots and colorbar :
kw_top = dict(margin=15 / 100, chan_offset=(0., 1.1, 0.), chan_size=1.5)
kw_cbar = dict(cbtxtsz=12, txtsz=10., width=.3, txtcolor='black', cbtxtsh=1.8,
               rect=(0., -2., 1., 4.), border=False)

###############################################################################
# Creation of the scene
###############################################################################
# Create a scene with a white background

sc = SceneObj(bgcolor='white', size=(1200, 900))

###############################################################################
# Topoplot with regulary spaced levels
###############################################################################
# The first topoplot contains 10 regulary spaced levels. The color of each
# level is based on the 'bwr' colormap. Note that in order to
# work, you need to install `scikit-image <https://scikit-image.org/>`_

# Create the topoplot object :
t_obj = TopoObj('topo', data, channels=channels, xyz=xyz, levels=10,
                level_colors='bwr', **kw_top)
# Get the colorbar based on the color properties of the topoplot :
cb_obj = ColorbarObj(t_obj, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj, row=0, col=0, title='Regulary spaced levels',
                  title_color='black', width_max=400)
sc.add_to_subplot(cb_obj, row=0, col=1, width_max=100)

###############################################################################
# Topoplot with custom levels
###############################################################################
# The only difference with the previous plot is that levels are not regulary
# spaced anymore but they are manually defined, just as color.

# First level is going to be red, the second one green and the last one blue
level_colors = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
levels = [2., 2.2, 2.5]
# Create the topoplot object :
t_obj_2 = TopoObj('topo', data, channels=channels, xyz=xyz, levels=levels,
                  level_colors=level_colors, chan_mark_symbol='cross',
                  line_width=7., chan_mark_color='gray', cmap='plasma',
                  line_color='#3498db', **kw_top)
# Get the colorbar based on the color properties of the topoplot :
cb_obj_2 = ColorbarObj(t_obj_2, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_2, row=0, col=2, title='Custom levels',
                  title_color='black')
sc.add_to_subplot(cb_obj_2, row=0, col=3, width_max=100)

###############################################################################
# Fixed colorbar limits
###############################################################################
# Fix the colorbar limits between (2., 2.8)

# Create the topoplot object :
t_obj_3 = TopoObj('topo', data, channels=channels, xyz=xyz, cmap='Spectral_r',
                  clim=(2., 2.8), **kw_top)
# Get the colorbar based on the color properties of the topoplot :
cb_obj_3 = ColorbarObj(t_obj_3, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_3, row=1, col=0, title='Fixed colorbar limits',
                  title_color='black')
sc.add_to_subplot(cb_obj_3, row=1, col=1, width_max=100)


###############################################################################
# Custom colorbar properties
###############################################################################
# In this last topoplot, every values under `vmin=2.` is going to be set to
# the color 'slateblue' and every values over `vmax=2.8` to 'darkred'

t_obj_4 = TopoObj('topo', data, channels=channels, xyz=xyz, cmap='gist_gray',
                  vmin=2., under='slateblue', vmax=2.8, over='darkred',
                  **kw_top)
# Get the colorbar based on the color properties of the topoplot :
cb_obj_4 = ColorbarObj(t_obj_4, cblabel='Beta power', **kw_cbar)
# Add the topoplot and the colorbar to the scene :
sc.add_to_subplot(t_obj_4, row=1, col=2, title='Custom color for extrema',
                  title_color='black', width_max=400)
sc.add_to_subplot(cb_obj_4, row=1, col=3, width_max=100)

#############################################
# Finally, display the scene
sc.preview()
