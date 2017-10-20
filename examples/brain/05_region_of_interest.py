"""
Add Region of interest (ROI)
============================

This example illustrate how to display Region Of Interest (ROI).

This small dataset (thx to Tarek Lajnef) contains sources inside the thalamus
and alpha power for each source. We are going to display the thalamus, then
project the source's activity on it.

Download source's coordinates (thalamus.txt) :
https://drive.google.com/open?id=0B6vtJiCQZUBvSkEwclFlaUdJVW8

Download alpha power (Px.npy):
https://drive.google.com/open?id=0B6vtJiCQZUBvTXhVc1NvSHRxQzA

.. image:: ../../picture/picbrain/ex_region_of_interest.png
"""
from __future__ import print_function
import numpy as np

from visbrain import Brain
from visbrain.objects import SourceObj
from visbrain.io import download_file, path_to_visbrain_data

# Load thalamus sources :
download_file('thalamus.txt')
s_xyz = np.loadtxt(path_to_visbrain_data('thalamus.txt'))
# Load alpha power. In fact, the PX.npy contains the power across several time
# windows. So we take the mean across time :
download_file('Px.npy')
s_data = np.load(path_to_visbrain_data('Px.npy')).mean(1) * 10e26

s_obj = SourceObj('ThalamusSources', s_xyz, data=s_data, color='#ab4642',
                  radius_min=10., radius_max=20.)

# Define a Brain instance :
vb = Brain(source_obj=s_obj)

"""
Select the thalamus index (76 for the left and 77 for the right). If you
don't know what is the index of your ROI, open the GUI and look at the
number in front of the name. Otherwise, un comment the following line :
"""
# print(vb.roi_list('AAL'))
vb.roi_control(selection=[76, 77], subdivision='AAL', smooth=5,
               name='thalamus', translucent=False)

# Project the source's activity onto the thalamus :
vb.cortical_projection(project_on='thalamus', cmap='Spectral_r',
                       clim=(11., 18.), cblabel="Alpha power", vmin=11.7,
                       vmax=17.1, under='gray', over='darkred', isvmin=True,
                       isvmax=True)

"""The displayed sources can be forced to fit to the roi. To this end, the
sources_fit() method find the closest roi vertex to each source and change the
source's coordinate for it.
"""
# vb.sources_fit_to_vertices(obj='thalamus')

# Eventualy, take a screenshot :
# vb.screenshot('thalamus.png', autocrop=True)

# Show the interface :
vb.show()
