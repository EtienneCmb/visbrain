"""This example illustrate how to display Region Of Interest (ROI).

This small dataset (thx to Tarek Lajnef) contains sources inside the thalamus
and alpha power for each source. We are going to display the thalamus, then
project the source's activity on it.
"""
import numpy as np

from visbrain import vbrain

# Load thalamus sources :
s_xyz = np.loadtxt('thalamus.txt')
# Load alpha power. In fact, the PX.npy contains the power across several time
# windows. So we take the mean across time :
s_data = np.load('Px.npy').mean(1)

# Define a vbrain instance :
vb = vbrain(s_xyz=s_xyz, s_data=s_data, s_cmap='viridis')
# Rotate the brain in axial view :
vb.rotate(fixed='axial')
# Select the thalamus index (77 for the left and 78 for the right). If you
# don't know what is the index of your ROI, open the GUI and look at the
# number in front of the name.
vb.area_plot(selection=[77, 78], subdivision='aal', smooth=5)
# Project the source's activity onto ROI directly :
vb.cortical_projection(project_on='roi')
# Eventualy, take a screenshot :
# vb.screenshot('thalamus.png', region=(1000, 300, 570, 550), colorbar=False)
# Show the interface :
vb.show()
