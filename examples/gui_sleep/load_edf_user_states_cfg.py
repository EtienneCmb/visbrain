"""
Load EDF file with custom vigilance state configuration
=============

This example demonstrate how to specify custom configuration
for vigilance states.

Required dataset at :
https://www.dropbox.com/s/bj1ra95rbksukro/sleep_edf.zip?dl=1

.. image:: ../../_static/examples/ex_LoadEDF.png
"""
import os
import os.path
from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
download_file('sleep_edf.zip', unzip=True, astype='example_data')
target_path = path_to_visbrain_data(folder='example_data')

dfile = os.path.join(target_path, 'excerpt2.edf')
cfile = os.path.join(target_path, 'excerpt2_config.txt')

# Path to states_cfg yaml
sfile = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'example_states_cfg.yml'
)

# Open the GUI :
sleep = Sleep(data=dfile, config_file=cfile, states_config_file=sfile)
sleep.show()
