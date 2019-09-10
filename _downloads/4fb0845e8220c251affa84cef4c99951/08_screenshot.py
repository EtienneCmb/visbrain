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
https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1

.. image:: ../../_static/examples/ex_brain_screenshot.png
"""
import os
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import BrainObj, SourceObj, RoiObj
from visbrain.io import download_file, path_to_visbrain_data

save_pic_path = path_to_visbrain_data(folder='Example_pic')

# Load the xyz coordinates and corresponding subject name :
s_xyz = np.load(download_file('xyz_sample.npz', astype='example_data'))['xyz']

"""Create a source object with random data between [-50,50]
"""
s_data = np.random.uniform(-50, 50, s_xyz.shape[0])
s_obj = SourceObj('Sobj', s_xyz, data=s_data, color='darkred', alpha=.5,
                  radius_min=2., radius_max=8., edge_width=0.)

"""Create a Region of Interest Object (ROI) and display brodmann area 4 and 6
"""
roi_obj = RoiObj('brodmann')
idx_4_6 = roi_obj.where_is(['BA4', 'BA6'], exact=True)
roi_color = {idx_4_6[0]: 'red',    # BA4 in red and BA6 in green
             idx_4_6[1]: 'green'}
roi_obj.select_roi(idx_4_6, unique_color=True, roi_to_color=roi_color,
                   smooth=7)

"""Create a brain object
"""
b_obj = BrainObj('B1', hemisphere='both', translucent=True)

"""Pass the brain, source and ROI object to the GUI
"""
vb = Brain(brain_obj=b_obj, source_obj=s_obj, roi_obj=roi_obj)

"""Render the scene and save the jpg picture with a 300dpi
"""
save_as = os.path.join(save_pic_path, '0_main_brain.jpg')
vb.screenshot(save_as, dpi=300, print_size=(10, 10), autocrop=True)

"""Project source's activity onto the surface
"""
vb.cortical_projection(clim=(0, 50), cmap='Spectral_r', vmin=10.1,
                       under='black', vmax=41.2, over='green')
vb.sources_control('Sobj', visible=False)        # Hide sources
vb.rotate(custom=(-160., 10.))                   # Rotate the brain
vb.brain_control(translucent=False)              # Make the brain opaque

"""Now, we take a screenthot of the scene but this time, we used the
autocrop argument to crop the image as close as possible to the brain.

Then, we used the print_size, dpi and unit inputs to get higher resolution
image.
Taken together, this mean that the image should have a sufficient size to be
(20 centimeters x 20 centimeters) at 300 dpi.
"""
save_as = os.path.join(save_pic_path, '1_proj_brain.tiff')
vb.screenshot(save_as, autocrop=True, print_size=(20, 20),
              unit='centimeter', dpi=300.)

"""Colorbar screenshot

The previous screenshot use the print_size input to increase the resolution.
Now, we use the factor input to do the same. This input simply increase
the image size proportionally.

Start by selecting the colorbar of the cortical projection, improve the
appearance and make a screenshot of it.
"""
save_as = os.path.join(save_pic_path, '2_proj_colorbar.tiff')
vb.screenshot(save_as, canvas='colorbar', autocrop=True, factor=2.)

"""Background color and transparency control of ROI screenshot
"""
roi_obj('aal')
idx_precentral_l = roi_obj.where_is(['Precentral (L)'], exact=True)
idx_postcentral_r = roi_obj.where_is(['Postcentral (R)'], exact=True)
roi_obj.select_roi(idx_precentral_l + idx_postcentral_r, smooth=11)

vb.cortical_repartition(project_on='roi', clim=(1, 17), vmin=2,
                        under='gray', cmap='Reds')
vb.sources_control('Sobj', visible=False)   # Display sources
vb.rotate(custom=(-210, 10.))               # Rotate the brain
vb.brain_control(visible=False)             # Hide the brain

save_as = os.path.join(save_pic_path, '3_cort_proj_roi.tiff')
save_as_cbar = os.path.join(save_pic_path, '3_cort_proj_roi_cbar.tiff')
vb.screenshot(save_as, transparent=True, autocrop=True, print_size=(5, 5))
vb.screenshot(save_as_cbar, canvas='colorbar', autocrop=True, factor=2.)

# Alternatively, you can display the GUI at the end, but it's not a necessity
# vb.show()
