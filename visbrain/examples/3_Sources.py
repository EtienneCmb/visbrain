"""This example demonstrate how to display deep sources using MNI
coordinates
"""
from visbrain import vbrain
import numpy as np

# Define a empty dictionnary :
kwargs = {}

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
kwargs['s_xyz'], subjects = mat['xyz'], mat['subjects']

# The "subjects" list is composed of 6 diffrents subjects.
# Now, we define the color of sources pear subject :
u_color = ["#9b59b6", "#3498db", "white", "#e74c3c", "#34495e", "#2ecc71"]	# The unique color pear subject
kwargs['s_color'] = [u_color[int(k[1])] for k in subjects]	# Set the subject corresponding color, for each electrode 
kwargs['s_opacity'] = 0.9 # Sources opacity

# Now, create some random data between [-50,50]
kwargs['s_data'] = np.round(100*np.random.rand(kwargs['s_xyz'].shape[0])-50)

# Control the dynamic range of sources radius :
kwargs['s_radiusmin'] = 2				# Minimum radius
kwargs['s_radiusmax'] = 8				# Maximum radius
kwargs['s_edgecolor'] = (1,1,1,0.5)	# Color of the edges
kwargs['s_edgewidth'] = 1				# Width of the edges

# Next, we will mask data between [-20, 20]:
kwargs['s_mask'] = np.logical_and(kwargs['s_data'] >= -20, kwargs['s_data'] <= 20)
kwargs['s_maskcolor'] = 'orange'


# Cortical projection/repartition :
# Navigate to the menu to transform -> cortical projection (or CTRL+P)
# then, the activity of deep sources can be project on the surface. 
# To make a pretty plot, we can define some colormap properties :
kwargs['s_cmap'] = 'viridis'				# Matplotlib colormap
kwargs['s_cmap_vmin'] = -40					# Define a minimum
kwargs['s_cmap_vmax'] = 21					# Define a maximum
kwargs['s_cmap_under'] = 'gray'				# Every values under vmin are going to be gray
kwargs['s_cmap_over'] = (0.1,0.1,0.1, 1)	# Every values over vmax are going to be black

# If you want to customize the colormap, display the quick settings menu (or CTRL+D)
# and checked the button 'See live changement of colormap settings'
kwargs['cb_label'] = 'Deep sources projection'

# Now, we can labelize each source :
kwargs['s_text'] = subjects			# Each source will show the name of the subject
kwargs['s_textcolor'] = "#f39c12"	# Set to yellow the text color
kwargs['s_textsize'] = 1.5			# Size of the text
kwargs['s_textshift'] = (1.5,1.5,0)	# To avoid a superposition between the text and sources sphere, we move the text of (x, y, z) points

# Pass all arguments in the dictionnary :
vb = vbrain(**kwargs)
vb.show()
