"""
Display conjunction map
=======================

Display a conjunction map from a nii.gz file (NiBabel required).

See the original PySurfer example :

https://pysurfer.github.io/auto_examples/plot_fmri_conjunction.html#sphx-glr-auto-examples-plot-fmri-conjunction-py

.. image:: ../../picture/picpysurfer/ex_pysurfer_conjunction_map.png
"""
from visbrain import Brain
from visbrain.objects import BrainObj
from visbrain.io import path_to_visbrain_data

file = path_to_visbrain_data(file='lh.sig.nii.gz')
file2 = path_to_visbrain_data(file='lh.alt_sig.nii.gz')

b_obj = BrainObj('inflated', translucent=False)
b_obj.add_activation(file=file, clim=(4., 30.), hide_under=4, cmap='Reds_r',
                     hemisphere='left')
b_obj.add_activation(file=file2, clim=(4., 30.), hide_under=4, cmap='Blues_r',
                     hemisphere='left')

vb = Brain(brain_obj=b_obj)
vb.rotate('left')
vb.show()
