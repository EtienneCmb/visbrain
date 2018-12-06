"""
Plot source space
=================

Plot from a .fif file using the :class:`visbrain.mne.mne_plot_source_space`
function

.. image:: ../../_static/examples/ex_eegmeg_plot_source_space.png
"""
###############################################################################
# Load .fif file in the MNE-python dataset
###############################################################################
import os
import numpy as np

from mne.datasets import sample

from visbrain.gui import Brain
from visbrain.mne import mne_plot_source_space

# Define path :
main_path = sample.data_path()
sbj_dir = os.path.join(*(main_path, 'subjects', 'fsaverage', 'bem'))

# fif file to load :
fif_file = os.path.join(sbj_dir, 'fsaverage-ico-5-src.fif')

###############################################################################
# Active data
###############################################################################
# Active data defined for illustration.
active_data = np.arange(20484)

###############################################################################
# Additional inputs
###############################################################################
# Additional inputs for BrainObj :
kw_b_obj = dict(translucent=False, hemisphere='both')
# Additional inputs for SourceObj :
kw_s_obj = dict(color='blue', symbol='square')
# Additional inputs for activations (colormap, clim...) :
kw_activation = dict(cmap='viridis', hide_under=10000,
                     clim=(active_data.min(), active_data.max()), vmax=20000,
                     over='red')

###############################################################################
# Get the brain and source objects
###############################################################################
# Note that here, we use `show=False`. In that case, a
# :class:`visbrain.objects.BrainObj` and a :class:`visbrain.objects.SourceObj`
# are returned.

b_obj, s_obj = mne_plot_source_space(fif_file, active_data=active_data,
                                     kw_brain_obj=kw_b_obj,
                                     kw_source_obj=kw_s_obj,
                                     kw_activation=kw_activation,
                                     show=False)

###############################################################################
# Pass the brain and source objects to the :class:`visbrain.Brain` module
###############################################################################
# Note that here, we pass the source object to Brain but by default we set it
# as not visible. But if you don't need to see it, simply remove the
# `source_obj=s_obj`

s_obj.visible_obj = False
brain = Brain(brain_obj=b_obj, source_obj=s_obj)
brain.show()
