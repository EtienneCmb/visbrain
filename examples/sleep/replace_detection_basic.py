"""
Replace detection algorithm : basic example
===========================================

This example illustrate how to replace the default detection algorithm.

.. note::

    Once your methods come to replace those included by default, in the GUI, go
    to Detection > Settings / Detection type > Type and select the detection
    type to run. BTW, the console should confirm that you're using your method
    and not the one included by default.

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

    This function do not intend to perform any signal processing. It just
    highlights samples between [0, 100], [200, 300] and [400, 500].
    """
    indices = np.array([[0, 100],
                       [200, 300],
                       [400, 500]])
    return indices

def fcn_rem(data, sf, time, hypno):  # noqa
    """New REM detection function.

    This function doesn't claim to really detect REM events. But it performs a
    basic thresholding and return boolean values of data that are than the
    threshold.
    """
    mean_data = np.mean(data)
    std_data = np.std(data)
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
