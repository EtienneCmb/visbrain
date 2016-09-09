"""This example demonstrate how to display connectivity. To this end,
we will define some deep sources and connect them. See 2_Sources.py
to defined sources
"""
from visbrain import vbrain
import numpy as np

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
s_xyz, subjects = mat['xyz'], mat['subjects']

N = s_xyz.shape[0]	# Number of electrodes
s_opacity = 0.5 	# Sources opacity

# Now, create some random data between [-50,50]
s_data = np.round(100*np.random.rand(s_xyz.shape[0])-50)

# Control the dynamic range of sources radius :
s_radiusmin, s_radiusmax, s_edgecolor = 2, 7, 'white'

# Colormap properties :
cmap = 'viridis'				# Matplotlib colormap
cmap_vmin, cmap_vmax = -40, 21
cmap_under, cmap_over = 'midnightblue', "#e74c3c"

# To connect sources between them, we create a (N, N) array.
# This array should be either upper or lower triangular to avoid
# redondant connections.
c_connect = 100*np.random.rand(N, N)				# Random array of connections
c_connect[np.tril_indices_from(c_connect)] = 0		# Set to zero inferior triangle


# Because all connections are not necessary interesting,
# it's possible to select only certain either using a
# c_select array composed with ones and zeros, or by
# masking the connection matrix.
# We are giong to search vealues between umin and umax to
# limit the number of connections :
umin, umax = 30, 30.05

# 1 - Using c_select (0: hide, 1: display):
c_select = np.zeros_like(c_connect)
c_select[(c_connect > umin) & (c_connect < umax)] = 1

# 2 - Using masking (True: hide, 1: display):
c_connect = np.ma.masked_array(c_connect, mask=True)
c_connect.mask[np.where((c_connect > umin) & (c_connect < umax))] = False

print('Methods 1 and 2 equivalent :', np.array_equal(c_select, ~c_connect.mask + 0))

# Finally, use c_colorby to define how connections have to be colored.
# if c_colorby is 'count', it's the number of connections which pear node
# drive the colormap. If 'strength', it's the connectivity strength between
# two nodes. Warning with this second method, which is much much slower...
c_colorby = 'count'
c_radiusmin = 4

vb = vbrain(s_xyz=s_xyz, s_color='crimson', s_data=s_data, s_radiusmin=s_radiusmin, s_radiusmax=s_radiusmax, s_opacity=s_opacity, a_opacity=0.05,
            cmap=cmap, cmap_vmin=cmap_vmin, cmap_vmax=cmap_vmax, cmap_under=cmap_under, cmap_over=cmap_over, c_connect=c_connect, c_colorby=c_colorby,
            c_radiusmin=c_radiusmin, a_template='B3')
vb.show()
