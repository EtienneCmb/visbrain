"""
Screenshot tutorial
===================

Export all of the time-frequency maps, psd of a dataset.

.. image:: ../../_static/examples/ex_screenshot.png
"""
import numpy as np

from visbrain.gui import Signal

sf = 1000.  # Sampling-frequency
n_pts = 4000  # Number of time points
n_sines = 10  # Number of sines

"""Create artificial sines :
"""
time = np.arange(n_pts) / sf
f_sines = np.linspace(13, 30, n_sines)
data = np.sin(2 * np.pi * f_sines.reshape(-1, 1) * time.reshape(1, -1))
data += np.random.randn(*data.shape)

"""Create the signal instance and pass data to it
"""
sig = Signal(data, axis=1, sf=sf, time=time, form='tf', tf_cmap='Spectral_r',
             psd_nperseg=n_pts)

"""Start by exporting the grid of signals.
"""
sig.screenshot('grid.tiff', canvas='grid', dpi=600, autocrop=True)

"""Loop over all of the signals and export all time-frequency maps.
"""
for k in sig:
    # Set the signal index :
    sig.set_signal_index(k)
    # Set final exported image to be the power spectrum density
    if k == n_sines - 2:
        sig.set_signal_form('psd')
    # Export image :
    sig.screenshot('tf_' + str(k) + '.png', dpi=600, autocrop=True)
sig.show()
