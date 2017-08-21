"""
Plot a 1d signal
================

This example show how to display and control simple 1d signal.

.. image:: ../../picture/picndviz/ex_basic_signal.png
"""

import numpy as np
from visbrain import Ndviz

# Create an empty dictionary :
kw = {}

# Sampling frequency :
sf = 1024.
# Create a 10hz cardinal sinus :
time = np.arange(-1000.1, 1000.1) / 1024.
y = np.sinc(2 * 10 * time).astype(np.float32)
kw['sf'] = sf

# ===================================================================
# Nd-plot configuration :
# -----------------------
"""
The Nd-plot can be used to display a large number of signals. I this example,
we defined above a row signal. In that case, the Nd-plot is not really usefull
be we just illustrate some of the possible inputs.
"""
# ===================================================================
# Display the Nd-plot panel and display the grid :
kw['nd_visible'] = True
kw['nd_grid'] = True
# Add a title / xlabel / ylabel :
kw['nd_title'] = 'Press 0 to reset camera / <space> for playing / r to reset'
kw['nd_xlabel'] = 'Configure using the "Nd-plot" tab of quick settings panel'
kw['nd_ylabel'] = 'Display quick settings using CTRL + d'
# Use a dynamic color (across time) :
kw['nd_color'] = 'dyn_time'
kw['nd_cmap'] = 'Spectral_r'
# Set the linewidth :
kw['nd_lw'] = 2

# ===================================================================
# 1d-plot configuration :
# -----------------------
"""
The 1d-plot can be used to inspect signal by signal. The signal can be display
in several forms cad (press the shortcut in parenthesis):
- As a continuous line (l)
- As a markers cloud (m)
- As a histogram (h)
- As a spectrogram (s)
- As an image (i - not available in this exemple -)
"""
# ===================================================================
# Display the Nd-plot panel and display the grid :
kw['od_visible'] = True
kw['od_grid'] = True
kw['od_title'] = 'Press m (marker), h (histogram), s (spectrogram), l (line)'
kw['od_xlabel'] = 'Switch between different plotting types'
kw['od_ylabel'] = 'Configure using the "Inspect" tab of quick settings panel'
# Marker size :
kw['od_msize'] = 20
# Number of bins in the histogram :
kw['od_bins'] = 100
# Number of fft points / step / starting and ending frequency :
kw['od_nfft'] = 512.
kw['od_step'] = 10.
kw['od_fstart'] = 0.
kw['od_fend'] = 50
# The color dynamically change with the amplitude of the signal :
kw['od_cmap'] = 'viridis'
kw['od_color'] = 'dyn_minmax'
# Every values under 0 will be set to red :
kw['od_vmin'], kw['od_under'] = 0., '#ab4642'
# Every values over 0.9 will be set to gay :
kw['od_vmax'], kw['od_over'] = 0.9, 'gray'
# Linewidth :
kw['od_lw'] = 2

Ndviz(y, **kw).show()
