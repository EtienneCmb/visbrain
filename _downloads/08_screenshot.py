"""
Screenshot example
==================

Offline rendering of selected canvas.

First, ou can take screenshot from the graphical interface using the menu
File/save/screenshot. The aim of this script is more to illustrate how to
take screenshots without opening the interface.

Further explanations about screenshot and transparency can be foud here :
http://visbrain.org/vbexport.html

Download source's coordinates (xyz_sample.npz) :
https://drive.google.com/open?id=0B6vtJiCQZUBvSFJvaTFSRDJvMEE

.. image:: ../../picture/picbrain/ex_screenshot.png
"""
import numpy as np

from visbrain import Brain

# Define a empty dictionnary :
kwargs = {}

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
kwargs['s_xyz'], subjects = mat['xyz'], mat['subjects']

# Now, create some random data between [-50,50]
kwargs['s_data'] = 50. * np.random.rand(kwargs['s_xyz'].shape[0])
kwargs['s_color'] = 'darkred'
kwargs['s_opacity'] = .5

# Control the dynamic range of sources radius :
kwargs['s_radiusmin'] = 2               # Minimum radius
kwargs['s_radiusmax'] = 8               # Maximum radius
kwargs['s_edgewidth'] = 0.              # Width of the edges

# Create a brain instance :
vb = Brain(**kwargs)

"""First, make a basic screenshot of the scene.

Once exported, you should notice that the image doesn't have a proper size to
be used in a paper. In addition, the image have to cropped to remove
unnecessary background.
"""
vb.screenshot('0_main_brain.jpg')

# Run the cortical projection :
vb.cortical_projection(clim=(0, 50), cmap='Spectral_r', vmin=10.1,
                       isvmin=True, under='black', vmax=41.2, over='green',
                       isvmax=True)
vb.sources_opacity(show=False)        # Hide sources
vb.rotate(custom=(-160., 10.))        # Rotate the brain
vb.brain_control(transparent=False)   # Make the brain opaque

"""Now, we take a screenthot of the scene but this time, we used the
autocrop argument to crop the image as close as possible to the brain.

Then, we used the print_size, dpi and unit inputs to get higher resolution
image.
Taken together, this mean that the image should have a sufficient size to be
(20 centimeters x 20 centimeters) at 300 dpi.
"""
vb.screenshot('1_proj_brain.tiff', autocrop=True, print_size=(20, 20),
              unit='centimeter', dpi=300.)

"""Colorbar screenshot

The previous screenshot use the print_size input to increase the resolution.
Now, we use the factor input to do the same. This input simply increase
the image size proportionally.

Start by selecting the colorbar of the cortical projection, improve the
appearance and make a screenshot of it.
"""
vb.cbar_select('Projection')
vb.cbar_control('Projection', txtsz=8., cbtxtsz=9.,
                cblabel='Cortical projection')
vb.screenshot('1_proj_colorbar.tiff', canvas='colorbar', autocrop=True,
              factor=4.)

"""Cross-sections splitted-view screenshot
"""
vb.cross_sections_control(pos=kwargs['s_xyz'][10, :], split_view=True,
                          cmap='viridis', show_text=False)
vb.screenshot('2_cross_sections.png', canvas='cross-sections',
              print_size=(200, 100), unit='millimeter', dpi=600.)
vb.cross_sections_control(visible=False, split_view=False)

"""Background color and transparency control of ROI screenshot
"""
vb.roi_control(selection=[3, 5, 32], subdivision='Brodmann', smooth=7)

# Run the cortical repartition
vb.cortical_repartition(radius=20., project_on='roi', clim=(1, 48),
                        isvmin=True, vmin=7, under='gray', cmap='viridis',
                        cblabel='Roi colorbar')
vb.cbar_select('Projection')                # Select the Projection colorbar
vb.sources_opacity(show=False)              # Display sources
vb.rotate(custom=(-210, 10.))               # Rotate the brain
vb.brain_control(visible=False)             # Hide the brain

"""
Export ROI with a transparent background and the colorbar with a green one
"""
vb.screenshot('3_roi_repartition.png', transparent=True, autocrop=True,
              print_size=(5, 5), unit='inch')

# Alternatively, you can display the GUI at the end, but it's not a necessity
# vb.show()
