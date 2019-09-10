"""
Plot forward solution
=====================

Plot source estimation.

.. image:: ../../_static/examples/ex_eegmeg_mne_forward_solution.png
"""
import os

from mne.datasets import sample
from visbrain.mne import mne_plot_source_estimation

# Define path :
sbj = 'sample'
main_path = sample.data_path()
data_path = os.path.join(main_path, 'MEG')

# Set sbj dir path, i.e. where the FS folfers are :
sbj_dir = os.path.join(main_path, 'subjects')

parc = 'aparc'  # apar, aparc.a2009s
fwd_fname = os.path.join(data_path, sbj, 'sample_audvis-meg-oct-6-fwd.fif')

# Inverse solution file :
inv_solution_fname = 'sample_audvis-meg-lh.stc'
inv_solution_path = os.path.join(data_path, sbj, inv_solution_fname)

# Additional inputs for BrainObj :
kw_b_obj = dict(translucent=False)
# Additional inputs for SourceObj :
kw_s_obj = dict(color='blue', symbol='square')
# Additional inputs for activations (colormap, clim...) :
kw_activation = dict(cmap='Reds', hide_under=0., clim=(0., .6))

"""Show control :
- True -> directly display the Brain interface
- False -> return a SourceObj and a BrainObj
- 'scene' -> return a SceneObj
"""
mne_plot_source_estimation(sbj, sbj_dir, fwd_fname, stc_file=inv_solution_path,
                           hemisphere='both', kw_activation=kw_activation,
                           kw_brain_obj=kw_b_obj, kw_source_obj=kw_s_obj,
                           active_data=12, show=True)
