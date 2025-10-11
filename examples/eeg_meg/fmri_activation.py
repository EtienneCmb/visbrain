"""
Display fMRI activation
=======================

Display fMRI activations from a nii.gz file (NiBabel required).

See the original example :

https://pysurfer.github.io/auto_examples/plot_fmri_activation.html#sphx-glr-auto-examples-plot-fmri-activation-py

.. image:: ../../_static/examples/ex_eegmeg_fmri_activations.png
"""
from visbrain.gui import Brain
from visbrain.objects import BrainObj
from visbrain.io import download_file

"""Download file if needed
"""
file = download_file('lh.sig.nii.gz', astype='example_data',
                     allow_download=True)

b_obj = BrainObj('inflated', translucent=False, sulcus=True)
b_obj.add_activation(file=file, clim=(5., 20.), hide_under=5, cmap='viridis',
                     hemisphere='left')

vb = Brain(brain_obj=b_obj)
vb.rotate('left')


def _build_example():
    return vb


if __name__ == "__main__":
    from visbrain.examples._runner import run_example

    raise SystemExit(run_example(_build_example))
