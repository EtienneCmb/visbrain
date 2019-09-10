"""
Add Region of interest (ROI)
============================

This example illustrate how to display Region Of Interest (ROI).

This small dataset (thx to Tarek Lajnef) contains sources inside the thalamus
and alpha power for each source. We are going to display the thalamus, then
project the source's activity on it.

.. image:: ../../_static/examples/ex_region_of_interest.png
"""
from __future__ import print_function
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import BrainObj, SourceObj, RoiObj
from visbrain.io import download_file

"""Download the location of sources closed to the thalamus and the power of
alpha oscillations
"""
thalamus_xyz = download_file('thalamus.txt', astype='example_data')
thalamus_data = download_file('Px.npy', astype='example_data')
s_xyz = np.loadtxt(thalamus_xyz)
s_data = np.load(thalamus_data).mean(1)

"""Create a source object
"""
s_obj = SourceObj('ThalamusSources', s_xyz, data=s_data, color='#ab4642',
                  radius_min=10., radius_max=20.)

"""Create a ROI object. The ROI object comes with three default templates :
* 'brodmann' : Brodmann areas
* 'aal' : Automatic Anatomical Labeling
* 'talairach'

You can also define your own RoiObj with your own labels.
"""
roi_obj = RoiObj('aal', cblabel="Alpha power", border=False)

"""Find index of the thalamus and get the mesh.

If you want to get all of the index of the ROI template use :
* `roi_obj.get_labels()` : return a pandas DatFrame
* `roi_obj.get_labels('/home/')` : save all supported ROI and labels in an
  excel file.
"""
idx_thalamus = roi_obj.where_is('Thalamus')
roi_obj.select_roi(idx_thalamus, smooth=5)

"""Once the ROI object created, we can project source's alpha modulations
directly on the thalamus
"""
roi_obj.project_sources(s_obj, cmap='Spectral_r', clim=(200., 2000.),
                        vmin=300., under='gray', vmax=1800., over='darkred')

"""You can also force sources to fit onto the thalamus
"""
# s_obj.fit_to_vertices(roi_obj.vertices)

"""
"""
b_obj = BrainObj('B3')

# Define a Brain instance :
vb = Brain(brain_obj=b_obj, source_obj=s_obj, roi_obj=roi_obj)

"""Select the colorbar of the ROI
"""
vb.cbar_select('roi')

"""Eventualy, take a screenshot
"""
# vb.screenshot('thalamus.png', autocrop=True)

# Show the interface :
vb.show()
