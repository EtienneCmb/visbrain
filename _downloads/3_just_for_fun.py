"""
Configure the uni and multi-dimensional plot
============================================

This example show how to display and control a ND signal.

.. image:: ../../picture/picndviz/ex_just_for_fun.png
"""

import numpy as np
from visbrain import Ndviz

# Create an empty dictionary :
kw = {}

sf = 1024.
npts = 200
time = np.arange(-npts / 2, npts / 2) / 1024.
# Create a 2d signal :
y = np.sinc(2 * 10 * time).astype(np.float32)
y = y.reshape(len(y), 1) + y
y = y.reshape(200, 200, 1) + y
kw['sf'] = sf

# ===================================================================
# Nd-plot configuration
# ===================================================================
kw['nd_visible'] = False
kw['nd_grid'] = False
kw['nd_axis'] = [0, 2, 1]

# ===================================================================
# 1d-plot configuration
# ===================================================================
# Display the Nd-plot panel and display the grid :
kw['od_visible'] = True
kw['od_grid'] = True
kw['od_title'] = 'Long press on "N", then "P" to come back...'
kw['od_xlabel'] = ''
kw['od_ylabel'] = ''
kw['ui_region'] = (50, 50, 1000, 1000)

Ndviz(y, **kw).show()
