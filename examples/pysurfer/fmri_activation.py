"""
Display fMRI activation
=======================

Display fMRI activations from a nii.gz file (NiBabel required).

See the original example :

https://pysurfer.github.io/auto_examples/plot_fmri_activation.html#sphx-glr-auto-examples-plot-fmri-activation-py

.. image:: ../../picture/picpysurfer/ex_pysurfer_fmri_activations.png
"""
from visbrain import Brain
from visbrain.objects import BrainObj
from visbrain.io import path_to_visbrain_data

file = path_to_visbrain_data(file='lh.sig.nii.gz')

b_obj = BrainObj('inflated', translucent=False)
b_obj.add_activation(file=file, clim=(5., 20.), hide_under=5, cmap='viridis',
                     hemisphere='left')

vb = Brain(brain_obj=b_obj)
vb.rotate('left')
vb.show()
