"""
Add deep sources
================

Add sources to the scene. This script also illustrate most of the controls for
sources. Each source is defined by a (x, y, z) MNI coordinate. Then, we can
attach some data to sources and project this activity onto the surface
(cortical projection). Alternatively, you can run the cortical repartition
which is defined as the number of contributing sources per vertex.

Download source's coordinates (xyz_sample.npz) :
https://drive.google.com/open?id=0B6vtJiCQZUBvSFJvaTFSRDJvMEE

.. image:: ../../picture/picbrain/ex_sources.png
"""
from visbrain import Brain
import numpy as np

# Define a empty dictionnary :
kwargs = {}

"""
Load the xyz coordinates and corresponding subject name
"""
mat = np.load('xyz_sample.npz')
kwargs['s_xyz'], subjects = mat['xyz'], mat['subjects']

"""
The "subjects" list is composed of 6 diffrents subjects and here we set one
unique color (u_color) per subject and send it to the interface (s_color).
We also set the source's opacity to 0.5.
"""
u_color = ["#9b59b6", "#3498db", "white", "#e74c3c", "#34495e", "#2ecc71"]
kwargs['s_color'] = [u_color[int(k[1])] for k in subjects]
kwargs['s_opacity'] = 0.5

"""
Now we attach data to each source. To illustrate this functionality, the data
attached is the x coordinate so that data increase from left to right.
"""
kwargs['s_data'] = kwargs['s_xyz'][:, 0]

"""
The source's radius is proportional to the data attached. But this proportion
can be controlled using a minimum and maximum radius (s_radiusmin, s_radiusmax)
"""
kwargs['s_radiusmin'] = 2               # Minimum radius
kwargs['s_radiusmax'] = 15              # Maximum radius
kwargs['s_edgecolor'] = (1, 1, 1, 0.5)  # Color of the edges
kwargs['s_edgewidth'] = .5              # Width of the edges
kwargs['s_symbol'] = 'square'           # Source's symbol

"""
Next, we mask source's data that are comprised between [-20, 20] and color
each source to orange
"""
mask = np.logical_and(kwargs['s_data'] >= -20, kwargs['s_data'] <= 20)
kwargs['s_mask'] = mask
kwargs['s_maskcolor'] = 'orange'

"""
After defining sources, it's possible to run the cortical projection and/or the
cortical repartition. The lines bellow are used to control the colormap when
opening the interface.
Run the projection from the menu Project/Run projection, from the source's tab
or using the shortcut CTRL + P (for projection) or CTRL + R (repartition)

Use CTRL + D to hide/display the quick-settings panel, the shortcut C to
display the colorbar.
"""
kwargs['s_cmap'] = 'viridis'           # Matplotlib colormap
kwargs['s_vmin'] = -60                 # Define a minimum
kwargs['s_vmax'] = 60                  # Define a maximum
kwargs['s_under'] = 'gray'             # Values under vmin are set to gray
kwargs['s_over'] = (0.1, 0.1, 0.1, 1)  # Values over vmax are set to black
kwargs['s_clim'] = (-70, 70)

"""
It's also possible to add text to each source. Here, we show the name of the
subject in yellow.
To avoid a superposition between the text and sources sphere, we introduce an
offset to the text using the s_textshift input
"""
kwargs['s_text'] = subjects             # Name of the subject
kwargs['s_textcolor'] = "#f39c12"       # Set to yellow the text color
kwargs['s_textsize'] = 1.5              # Size of the text
kwargs['s_textshift'] = (1.5, 1.5, 0)

# Pass all arguments in the dictionnary :
vb = Brain(**kwargs)
vb.show()
