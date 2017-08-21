"""
Plot 2D signal
==============

This example show how to display and control a 2D signal.

.. image:: ../../picture/picndviz/ex_2d_signals.png
"""

import numpy as np
from visbrain import Ndviz

# Create an empty dictionary :
kw = {}

# Sampling frequency :
sf = 1024.
npts = 200
time = np.arange(-npts/2, npts/2)/1024.
# Create a 2d signal :
y = np.sinc(2*10*time).astype(np.float32)
y = y.reshape(len(y), 1) + y
# Add a little bit of noise :
y = y**2 + np.random.rand(*y.shape) / 10
kw['sf'] = sf

# ===================================================================
# Nd-plot configuration :
# -----------------------
"""
The y signal has a shape of (200, 200). By default, the first axis is
considered as the number of time points. The second axis is then used to
dispatch signals in the most optimal grid. In that case, you'll have a
(10 rows, 20 columns) grid of signals.
You can switch axis directly from the interface or using the nd_axis. 
"""
# ===================================================================
# Display the Nd-plot panel and display the grid :
kw['nd_visible'] = True
kw['nd_grid'] = True
# Use a random color for each signal :
kw['nd_color'] = 'random'
# Set the linewidth :
kw['nd_lw'] = 3

# ===================================================================
# 1d-plot configuration :
# -----------------------
"""
When a 2D array is passed to Nd-viz, you can use the image panel to see
it as an image.
For the line / marker / spectrogram / histogram types, the X-axis is where are
the time points and the Y-axis is the column that is curently inspecting.
For example, if in the Inspect/1d-Signal the X-axis is 0, Y-axis is 1 and index
is 22 this can be resume as data[:, 22]. Then you can use shortcuts "n" and "p"
respectively to display next or previous signal along the Y-axis.
"""
# ===================================================================
# Display the Nd-plot panel and display the grid :
kw['od_visible'] = True
kw['od_grid'] = True
kw['od_title'] = 'The 2D signal'
# Marker size :
kw['od_msize'] = 15
# Number of bins in the histogram :
kw['od_bins'] = 20
# Number of fft points / step / starting and ending frequency :
kw['od_nfft'] = 512.
kw['od_step'] = 10.
kw['od_fstart'] = 0.
kw['od_fend'] = 50
# The color dynamically change with the amplitude of the signal :
kw['od_cmap'] = 'Spectral'
kw['od_color'] = 'dyn_minmax'
# Every values under 0 will be set to red :
kw['od_vmin'], kw['od_under'] = 0., '#ab4642'
# Every values over 0.9 will be set to gay :
kw['od_vmax'], kw['od_over'] = 0.9, 'gray'
# Linewidth :
kw['od_lw'] = 2

Ndviz(y, **kw).show()
