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

# Load thalamus sources :
s_xyz = np.loadtxt('thalamus.txt')
# Load alpha power. In fact, the PX.npy contains the power across several time
# windows. So we take the mean across time :
s_data = np.load('Px.npy').mean(1) * 10e26

# Define a Brain instance :
vb = Brain(s_xyz=s_xyz, s_data=s_data, s_cmap='viridis')
# Rotate the brain in axial view :
vb.rotate(fixed='axial_0')

"""
Select the thalamus index (76 for the left and 77 for the right). If you
don't know what is the index of your ROI, open the GUI and look at the
number in front of the name. Otherwise, un comment the following line :
"""
# print(vb.roi_list('AAL'))
vb.roi_control(selection=[76, 77], subdivision='AAL', smooth=5,
               name='thalamus')

# Project the source's activity onto ROI directly :
vb.cortical_projection(project_on='thalamus', cmap='Spectral_r',
                       clim=(100, 2300))

"""The displayed sources can be forced to fit to the roi. To this end, the
sources_fit() method find the closest roi vertex to each source and change the
source's coordinate for it.
"""
# vb.sources_fit(obj='roi')

# Eventualy, take a screenshot :
# vb.screenshot('thalamus.png', autocrop=True)

# Show the interface :
vb.show()
