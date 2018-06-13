"""
Replace detection algorithm : basic example
===========================================

This example illustrates how to replace the default detection algorithm.

.. note::

    After running this script, just go to the Detection panel and run the
    selected detection by clicking on Apply. The software will automatically
    use your new detection algorithm. The Python console should confirm that
    you're using the new method and not the default method.

Required dataset at :
https://www.dropbox.com/s/bj1ra95rbksukro/sleep_edf.zip?dl=1

"""
import os
import numpy as np

from visbrain import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
current_path = path_to_visbrain_data()
target_path = os.path.join(current_path, 'sleep_data', 'edf')

download_file('sleep_edf.zip', unzip=True, to_path=target_path)

dfile = os.path.join(target_path, 'excerpt2.edf')
hfile = os.path.join(target_path, 'Hypnogram_excerpt2.txt')
cfile = os.path.join(target_path, 'excerpt2_config.txt')


###############################################################################
#                             DEFINE NEW METHODS
###############################################################################
def fcn_spindle(data, sf, time, hypno):  # noqa
    """New spindle detection function.

    This function does NOT perform a real spindle detection. It's purpose is to
    show how to replace the default detection behavior by a custom function.
    It just highlights samples between [0, 100], [200, 300] and [400, 500].
    """
    indices = np.array([[0, 100],
                       [200, 300],
                       [400, 500]])
    return indices

def fcn_rem(data, sf, time, hypno):  # noqa
    """New REM detection function.

    This function does NOT perform a real REM detection. It illustrates how to
    replace the default detection behavior by a basic thresholding function.
    Note that the function returns a boolean array indicating samples that are
    above a specific threshold.
    """
    mean_data = np.mean(data)
    std_data = np.std(data)
    # Threshold is mean + 3 * STD
    return data > mean_data + 3. * std_data


###############################################################################
#                         REPLACE EXISTING METHODS
###############################################################################
# Define an instance of Sleep :
sp = Sleep(data=dfile, hypno=hfile, config_file=cfile)

# Replace the spindle detection function :
sp.replace_detections('spindle', fcn_spindle)
# Replace the REM detection function :
sp.replace_detections('rem', fcn_rem)

# Finally, open Sleep :
sp.show()
