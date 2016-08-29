"""This example demonstrate how to display deep sources using MNI
coordinates
"""
from visbrain import vbrain
import numpy as np

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
s_xyz, subjects = mat['xyz'], mat['subjects']

# The "subjects" list is composed of 6 diffrents subjects.
# Now, we define the color of sources pear subject :
u_color = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]	# The unique color pear subject
s_color = [u_color[int(k[1])] for k in subjects]	# Set the subject corresponding color, for each electrode 
s_opacity = 0.9 # Sources opacity

# Now, create some random data between [-50,50]
s_data = np.round(100*np.random.rand(s_xyz.shape[0])-50)

# Control the dynamic range of sources radius :
s_radiusmin = 2		# Minimum radius
s_radiusmax = 8		# Maximum radius

# Cortical projection/repartition :
# Navigate to the menu to transform -> cortical projection (or CTRL+P)
# then, the activity of deep sources can be project on the surface. 
# To make a pretty plot, we can define some colormap properties :
cmap = 'viridis'				# Matplotlib colormap
cmap_vmin = -40					# Define a minimum
cmap_vmax = 21					# Define a maximum
cmap_under = 'gray'				# Every values under vmin are going to be gray
cmap_over = (0.1,0.1,0.1, 1)	# Every values over vmax are going to be black

# If you want to customize the colormap, display the quick settings menu (or CTRL+D)
# and checked the button 'See live changement of colormap settings'
cb_label = 'Deep sources projection'


vb = vbrain(s_xyz=s_xyz, s_color=s_color, s_data=s_data, s_radiusmin=s_radiusmin, s_radiusmax=s_radiusmax, s_opacity=s_opacity,
            cmap=cmap, cmap_vmin=cmap_vmin, cmap_vmax=cmap_vmax, cmap_under=cmap_under, cmap_over=cmap_over, cb_label=cb_label)
vb.show()
