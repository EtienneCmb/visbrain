"""
Load REC files
==============

This example demonstrate how to load a .rec file.

Required dataset at :
https://www.dropbox.com/s/hc18bgn2hlnmiph/sleep_edf.zip?dl=1

.. image:: ../../_static/examples/ex_load_rec.png
"""
import os

from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
download_file('sleep_rec.zip', unzip=True, astype='example_data',
              allow_download=True)
target_path = path_to_visbrain_data(folder='example_data')

dfile = os.path.join(target_path, '1.rec')


def _build_example():
    return Sleep(data=dfile)


if __name__ == "__main__":
    from visbrain.examples._runner import run_example

    raise SystemExit(run_example(_build_example))
