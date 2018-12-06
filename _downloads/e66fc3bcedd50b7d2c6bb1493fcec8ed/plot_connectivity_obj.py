"""
Connectivity object (ConnectObj) : complete tutorial
====================================================

Illustration of the main functionalities and inputs of the connectivity object:

    * Color connectivity links according to connectivity strength
    * Color connectivity links according to the number of connections per node
    * Color connectivity links using custom colors
"""
import numpy as np

from visbrain.objects import ConnectObj, SceneObj, SourceObj, BrainObj
from visbrain.io import download_file

###############################################################################
# Download data and define the scene
###############################################################################
# First, we download a connectivity dataset consisting of the location of each
# node (104) and the connectivity strength between every node (104, 104)

# Download data
arch = np.load(download_file('phase_sync_delta.npz', astype='example_data'))
nodes, edges = arch['nodes'], arch['edges']
# Create the scene with a black background
sc = SceneObj(size=(1500, 600))

###############################################################################
# Color by connectivity strength
###############################################################################
# First, we download a connectivity dataset consisting of the location of each
# node (iEEG site) and the connectivity strength between those nodes. The first
# coloring method illustrated bellow consist in coloring connections based on
# a colormap

# Coloring method
color_by = 'strength'
# Because we don't want to plot every connections, we only keep connections
# above .7
select = edges > .7
# Define the connectivity object
c_default = ConnectObj('default', nodes, edges, select=select, line_width=2.,
                       cmap='Spectral_r', color_by=color_by)
# Then, we define the sources
s_obj = SourceObj('sources', nodes, color='#ab4642', radius_min=15.)
sc.add_to_subplot(c_default, title='Color by connectivity strength')
# And add connect, source and brain objects to the scene
sc.add_to_subplot(s_obj)
sc.add_to_subplot(BrainObj('B3'), use_this_cam=True)

###############################################################################
# Color by number of connections per node
###############################################################################
# The next coloring method consist in set a color according to the number of
# connections per node. Here, we also illustrate that colors can also by
# `dynamic` (i.e stronger connections are opaque and weak connections are more
# translucent)

# Coloring method
color_by = 'count'
# Weak connections -> alpha = .1 // strong connections -> alpha = 1.
dynamic = (.1, 1.)
# Define the connectivity and source object
c_count = ConnectObj('default', nodes, edges, select=select, line_width=4.,
                     color_by=color_by, antialias=True, dynamic=dynamic)
s_obj_c = SourceObj('sources', nodes, color='olive', radius_min=10.,
                    symbol='square')
# And add connect, source and brain objects to the scene
sc.add_to_subplot(c_count, row=0, col=1,
                  title='Color by number of connections per node')
sc.add_to_subplot(s_obj_c, use_this_cam=True, row=0, col=1)
sc.add_to_subplot(BrainObj('B3'), use_this_cam=True, row=0, col=1)

###############################################################################
# Custom colors
###############################################################################
# Finally, you can define your own colors which mean that for a specific
# connectivity strength, you can manually set a unique color. The provided
# dataset has values between [0., 1.]

# First, we take a copy of the connectivity array
edges_copy = edges.copy()
# Then, we force edges to take fixed values
# ====================   =========  ===========
# Condition              New value  Color
# ====================   =========  ===========
# edges >= 0.8              4.      red
# edges in [.78, .8[        3.      orange
# edges in [.74, .78[       2.      blue
# Others                    -       lightgray
# ====================   =========  ===========
edges_copy[edges_copy >= .8] = 4.
edges_copy[np.logical_and(edges_copy >= .78, edges_copy < .8)] = 3.
edges_copy[np.logical_and(edges_copy >= .74, edges_copy < .78)] = 2.
# Now we use a dctionary to set one color per value.
ccol = {
    None: 'lightgray',
    2.: 'blue',
    3.: 'orange',
    4.: 'red'
}

# Define the connectivity and source objects
c_cuscol = ConnectObj('default', nodes, edges_copy, select=edges > .7,
                      custom_colors=ccol)
s_obj_cu = SourceObj('sources', nodes, color='slategray', radius_min=10.,
                     symbol='ring')
# Add objects to the scene
sc.add_to_subplot(c_cuscol, row=0, col=2, title='Custom colors')
sc.add_to_subplot(s_obj_cu, row=0, col=2)
sc.add_to_subplot(BrainObj('white'), use_this_cam=True, row=0, col=2)

# Finally, display the scene
sc.preview()
