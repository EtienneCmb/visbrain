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
from visbrain.io import path_to_visbrain_data, download_file

"""Download files if needed
"""
file_name_1 = 'lh.sig.nii.gz'
file_name_2 = 'lh.alt_sig.nii.gz'
download_file(file_name_1)
download_file(file_name_2)

file_1 = path_to_visbrain_data(file=file_name_1)
file_2 = path_to_visbrain_data(file=file_name_2)

b_obj = BrainObj('inflated', translucent=False)
b_obj.add_activation(file=file_1, clim=(4., 30.), hide_under=4, cmap='Reds_r',
                     hemisphere='left')
b_obj.add_activation(file=file_2, clim=(4., 30.), hide_under=4, cmap='Blues_r',
                     hemisphere='left')

vb = Brain(brain_obj=b_obj)
vb.rotate('left')
vb.show()
