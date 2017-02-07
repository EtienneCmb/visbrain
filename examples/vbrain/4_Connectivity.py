"""This example demonstrate how to display connectivity. To this end,
we will define some deep sources and connect them. See 2_Sources.py
to defined sources
"""
from visbrain import vbrain
import numpy as np

# Create an empty kwargs dictionnary :
kwargs = {}

# ____________________________ DATA ____________________________

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
s_xyz, subjects = mat['xyz'], mat['subjects']

N = s_xyz.shape[0]  # Number of electrodes
kwargs['s_opacity'] = 0.5 	# Sources opacity

# Now, create some random data between [-50,50]
s_data = np.round(100*np.random.rand(s_xyz.shape[0])-50)
kwargs['s_xyz'], kwargs['s_data'] = s_xyz, s_data
kwargs['s_color'] = 'crimson'

# To connect sources between them, we create a (N, N) array.
# This array should be either upper or lower triangular to avoid
# redondant connections.
c_connect = 1000*np.random.rand(N, N)		    # Random array of connections
c_connect[np.tril_indices_from(c_connect)] = 0  # Set to zero inferior triangle


# Because all connections are not necessary interesting,
# it's possible to select only certain either using a
# c_select array composed with ones and zeros, or by
# masking the connection matrix.
# We are giong to search vealues between umin and umax to
# limit the number of connections :
umin, umax = 30, 31

# 1 - Using c_select (0: hide, 1: display):
c_select = np.zeros_like(c_connect)
c_select[(c_connect > umin) & (c_connect < umax)] = 1

# 2 - Using masking (True: hide, 1: display):
c_connect = np.ma.masked_array(c_connect, mask=True)
c_connect.mask[np.where((c_connect > umin) & (c_connect < umax))] = False

print('Methods 1 and 2 equivalent :', np.array_equal(c_select, ~c_connect.mask + 0))
kwargs['c_connect'] = c_connect
# ____________________________ SETTINGS ____________________________


# Control the dynamic range of sources radius and the edge color :
kwargs['s_radiusmin'], kwargs['s_radiusmax'] = 2, 10
kwargs['s_edgecolor'] = None#'white'
kwargs['s_edgewidth'] = 0

# Colormap properties (for sources) :
kwargs['s_cmap'] = 'viridis'				# Matplotlib colormap
kwargs['s_cmap_vmin'], kwargs['s_cmap_vmax'] = -40, 21
kwargs['s_cmap_under'], kwargs['s_cmap_over'] = 'midnightblue', "#e74c3c"

# Colormap properties (for connectivity) :
kwargs['c_cmap'] = 'gnuplot'				# Matplotlib colormap
kwargs['c_cmap_vmin'], kwargs['c_cmap_vmax'] = umin+0.2, umax-0.1
kwargs['c_cmap_under'], kwargs['c_cmap_over'] = 'green', "white"
kwargs['c_cmap_clim'] = [umin, umax]

# Finally, use c_colorby to define how connections have to be colored.
# if c_colorby is 'count', it's the number of connections which pear node
# drive the colormap. If 'strength', it's the connectivity strength between
# two nodes.
kwargs['c_colorby'] = 'strength'
kwargs['c_radiusmin'] = 4
kwargs['c_dynamic'] = (0.1, 1)

# Atlas template and opacity :
kwargs['a_template'] = 'B2'
kwargs['a_opacity'] = 0.05

# Set font size, color and label for the colorbar :
kwargs['cb_fontsize'] = 15
kwargs['cb_fontcolor'] = 'white'
kwargs['cb_label'] = 'My colorbar label'

vb = vbrain(**kwargs)
vb.show()
