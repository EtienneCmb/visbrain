"""
Replace detection algorithm : basic example
===========================================

This example illustrates how to replace the default detection algorithm.

.. warning::

    After running this script, just go to the Detection panel and run the
    selected detection by clicking on Apply. The software will automatically
    use your new detection algorithm. The Python console should confirm that
    you're using the new method and not the default method.

Required dataset at :
https://www.dropbox.com/s/bj1ra95rbksukro/sleep_edf.zip?dl=1

.. image:: ../../_static/examples/ex_replace_detection_basic.png
"""
###############################################################################
# Load your file and create an instance of Sleep
###############################################################################

import os
import numpy as np

from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

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

###############################################################################
#
# This function does NOT perform a real spindle detection. It's purpose is to
# show how to replace the default detection behavior by a custom function.
# It just highlights samples between [0, 100], [200, 300] and [400, 500].

def fcn_spindle(data, sf, time, hypno):  # noqa
    """New spindle detection function."""
    indices = np.array([[0, 100],
                       [200, 300],
                       [400, 500]])
    return indices

###############################################################################
# Rapid eye movement function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

###############################################################################
# This function does NOT perform a real REM detection. It illustrates how to
# replace the default detection behavior by a basic thresholding function.
# Note that the function returns a boolean array indicating samples that are
# above a specific threshold.

def fcn_rem(data, sf, time, hypno):  # noqa
    """New REM detection function."""
    mean_data = np.mean(data)
    std_data = np.std(data)
    # Threshold is mean + 3 * STD
    return data > mean_data + 3. * std_data

###############################################################################
# Replace existing methods
###############################################################################
# Now we use the :class:`visbrain.gui.Sleep.replace_detections` method to
# overwrite existing spindles and REM detections.

# Replace the spindle detection function :
sp.replace_detections('spindle', fcn_spindle)
# Replace the REM detection function :
sp.replace_detections('rem', fcn_rem)

# Finally, open the graphical user interface :
sp.show()
