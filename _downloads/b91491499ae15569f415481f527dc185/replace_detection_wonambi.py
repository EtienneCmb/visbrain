"""
Replace detection with wonambi algorithm
========================================

This example illustrates how to replace the default spindle detection algorithm
with those implemented inside wonambi.

This example uses the wonambi package. See
https://wonambi-python.github.io/installation.html for a detailed installation.

.. warning::

    After running this script, just go to the Detection panel and run the
    selected detection by clicking on Apply. The software will automatically
    use your new detection algorithm. The Python console should confirm that
    you're using the new method and not the default method.

Required dataset at :
https://www.dropbox.com/s/bj1ra95rbksukro/sleep_edf.zip?dl=1

.. image:: ../../_static/examples/ex_replace_detection_wonambi.png
"""
###############################################################################
# Load your file and create an instance of Sleep
###############################################################################

import os
import numpy as np

from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

from wonambi.detect.spindle import DetectSpindle, detect_Moelle2011
from wonambi.detect.slowwave import DetectSlowWave, detect_Massimini2004

# Download the file :
download_file('sleep_edf.zip', unzip=True, astype='example_data')
target_path = path_to_visbrain_data(folder='example_data')

# Get data path :
dfile = os.path.join(target_path, 'excerpt2.edf')            # data
hfile = os.path.join(target_path, 'Hypnogram_excerpt2.txt')  # hypnogram
cfile = os.path.join(target_path, 'excerpt2_config.txt')     # GUI config

# Define an instance of Sleep :
sp = Sleep(data=dfile, hypno=hfile, config_file=cfile)

###############################################################################
# Define new methods
###############################################################################

###############################################################################
# Spindle function
# ~~~~~~~~~~~~~~~~

# Define a DetectSpindle instance :
opts_spin = DetectSpindle('Moelle2011')
# Define the function to replace :
def fcn_spindle(data, sf, time, hypno):  # noqa
    """New spindle detection function.

    See : https://wonambi-python.github.io/api/wonambi.detect.spindle.html
    for an exhaustive list of implemented detections inside wonambi.
    """
    out, _, _ = detect_Moelle2011(data, sf, time, opts_spin)
    indices = np.zeros((len(out), 2))
    for i, k in enumerate(out):
        indices[i, 0] = k['start']
        indices[i, 1] = k['end']
    indices *= sf
    return indices.astype(int)

###############################################################################
# Slow-waves function
# ~~~~~~~~~~~~~~~~~~~

# Define a DetectSlowWave instance :
opts_sw = DetectSlowWave('Massimini2004')
# Define the function to replace :
def fcn_slowwave(data, sf, time, hypno):  # noqa
    """New slowwave detection function.

    See : https://wonambi-python.github.io/api/wonambi.detect.slowwave.html
    for an exhaustive list of implemented detections inside wonambi.
    """
    out = detect_Massimini2004(data, sf, time, opts_sw)
    indices = np.zeros((len(out), 2))
    for i, k in enumerate(out):
        indices[i, 0] = k['start']
        indices[i, 1] = k['end']
    indices *= sf
    return indices.astype(int)

###############################################################################
# Replace existing methods
###############################################################################
# Now we use the :class:`visbrain.gui.Sleep.replace_detections` method to
# overwrite existing spindles and slow-waves detections.

# Replace the spindle detection function :
sp.replace_detections('spindle', fcn_spindle)
# Replace the slow-wave detection function :
sp.replace_detections('sw', fcn_slowwave)

# Finally, open the graphical user interface :
sp.show()
