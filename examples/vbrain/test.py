"""This example demonstrate how to display deep sources using MNI coordinates."""
from visbrain import vbrain
import numpy as np

# Define a empty dictionnary :
kwargs = {}

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
kwargs['s_xyz'], subjects = mat['xyz'], mat['subjects'][0]
print(kwargs['s_xyz'].shape)
# The "subjects" list is composed of 6 diffrents subjects.
# Now, we define the color of sources pear subject :
# u_color = ["#9b59b6", "#3498db", "white", "#e74c3c", "#34495e", "#2ecc71"]	# The unique color pear subject
# kwargs['s_color'] = [u_color[int(k[1])] for k in subjects]	# Set the subject corresponding color, for each electrode 
# kwargs['s_opacity'] = 0.9 # Sources opacity

# Now, create some random data between [-50,50]
kwargs['s_data'] = np.arange(kwargs['s_xyz'].shape[0])#np.round(100*np.random.rand(kwargs['s_xyz'].shape[0])-50)




# Cortical projection/repartition :
# Navigate to the menu to transform -> cortical projection (or CTRL+P)
# then, the activity of deep sources can be project on the surface. 
# To make a pretty plot, we can define some colormap properties :
kwargs['s_cmap'] = 'Blues'				# Matplotlib colormap
kwargs['s_cmap_clim'] = (kwargs['s_data'].min(), kwargs['s_data'].max())

# If you want to customize the colormap, display the quick settings menu (or CTRL+D)
# and checked the button 'See live changement of colormap settings'
kwargs['cb_label'] = 'Deep sources projection'
# Pass all arguments in the dictionnary :
kwargs['t_smooth'] = 0.9
vb = vbrain(**kwargs)

vb._cortical_projection()
vb.light_reflection('external')
vb.show()

 # Define a vbrain instance with 10 random sources:
# vb = vbrain(**kwargs)
# vb.show()