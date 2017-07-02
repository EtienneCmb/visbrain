"""
Screenshot example
==================

This script illustrate how to export your figures and the colorbar.

The full tutorial is :
https://etiennecmb.github.io/visbrain/vbexport.html
"""
import numpy as np

from visbrain import Brain

# Define a empty dictionnary :
kwargs = {}

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
kwargs['s_xyz'], subjects = mat['xyz'], mat['subjects']

# Now, create some random data between [-50,50]
kwargs['s_data'] = np.round(100*np.random.rand(kwargs['s_xyz'].shape[0])-50)
kwargs['s_color'] = 'darkred'
kwargs['s_opacity'] = .5

# Control the dynamic range of sources radius :
kwargs['s_radiusmin'] = 2               # Minimum radius
kwargs['s_radiusmax'] = 8               # Maximum radius
kwargs['s_edgewidth'] = 0.              # Width of the edges

# Add label to the colorbar :
kwargs['cb_label'] = 'My exported colorbar !'
kwargs['cb_fontcolor'] = 'black'

# Define your monitor properties for figure exportation
# (this configuration has been tested on a 17" laptop) :
region = (1200, 200, 500, 600)     # Crop your figure using this region
cbzoom = 50.                       # Zoom level over the colobar canvas

# Create a brain instance :
vb = Brain(**kwargs)

# First, make a basic screenshot of the scene :
vb.screenshot('screenshot1.jpg', region=region)

# Make a screenshot of the cortical projection :
vb.cortical_projection()          # Run the cortical projection
vb.sources_opacity(show=False)    # Hide sources
vb.rotate(custom=(-160., 10.))    # Rotate the brain
vb.light_reflection('external')   # Make the brain opaque
vb.screenshot('screenshot2.tiff', region=region)

# Make a screenshot of ROI :
vb.roi_plot(selection=[4, 6, 40],       # Display Brodmann area 4 and 6 :
            subdivision='brod',
            smooth=5)
vb.sources_colormap(cmap='Spectral_r')
vb.cortical_repartition(radius=20.,     # Run the cortical repartition
                        project_on='roi')
vb.sources_opacity(show=False)           # Display sources
vb.rotate(custom=(-210, 10.))           # Rotate the brain
vb.brain_control(show=False)            # Hide the brain
vb.screenshot('screenshot3.png',        # Export with transparent background and colorbar
              region=region,
              transparent=False, colorbar=True)

# Alternatively, you can display the GUI at the end, but it's not a necessity :
# vb.show()
