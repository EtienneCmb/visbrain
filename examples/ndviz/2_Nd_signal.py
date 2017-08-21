"""
Plot multidimensional signals
=============================

This example show how to display and control a ND signal.

.. image:: ../../picture/picndviz/ex_nd_signals.png
"""

import numpy as np
from visbrain import Ndviz

# Create an empty dictionary :
kw = {}

# Sampling frequency :
sf = 1024.
# Create a 10hz cardinal sinus :
time = np.arange(10 * 8 * 1000 * 20) / 1024.
y = np.sin(2 * 10 * time).astype(np.float32).reshape(10, 8, 1000, 20)
y += np.random.rand(10, 8, 1000, 20).astype(np.float32)
y *= np.random.rand(10, 8, 1, 20).astype(np.float32)
kw['sf'] = sf

# ===================================================================
# Nd-plot configuration :
# -----------------------
"""
Here, the signal y has a shape of (10, 8, 1000, 20). We are going to define the
nd_axis parameter in order to control how to display this signal. The nd_axis
parameter is define like this :
nd_axis = [time_axis, rows_axis, cols_axis] where each -_axis refer to the
location of the corresponding axis in the data. For example, the 1000 points
are going to be considered as time points. Then, the 8 the number of rows and
20, the number of columns. The nd_axis parameter is :
nd_axis = [2, 1, 3].
"""
# ===================================================================
# Display the Nd-plot panel and display the grid :
kw['nd_visible'] = True
kw['nd_grid'] = False
kw['nd_axis'] = [2, 1, 3]
kw['nd_scale'] = (0.9, 1.)
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
kw['od_grid'] = False
kw['od_title'] = 'The 2D signal'
# kw['od_axis'] = [2, 0]
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
