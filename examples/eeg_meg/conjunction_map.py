"""
Display conjunction map
=======================

Display a conjunction map from a nii.gz file (NiBabel required).

See the original PySurfer example :

https://pysurfer.github.io/auto_examples/plot_fmri_conjunction.html#sphx-glr-auto-examples-plot-fmri-conjunction-py

.. image:: ../../_static/examples/ex_eegmeg_conjunction_map.png
"""
from visbrain.gui import Brain
from visbrain.objects import BrainObj
from visbrain.io import download_file

"""Download files if needed
"""
file_1 = download_file('lh.sig.nii.gz', astype='example_data')
file_2 = download_file('lh.alt_sig.nii.gz', astype='example_data')

b_obj = BrainObj('inflated', translucent=False, sulcus=True)
b_obj.add_activation(file=file_1, clim=(4., 30.), hide_under=4, cmap='Reds_r',
                     hemisphere='left')
b_obj.add_activation(file=file_2, clim=(4., 30.), hide_under=4, cmap='Blues_r',
                     hemisphere='left')

vb = Brain(brain_obj=b_obj)
vb.rotate('left')
vb.show()
