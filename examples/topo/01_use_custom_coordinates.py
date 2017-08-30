"""
Use custom coordinates
======================

Display topographic plots using custom coordinates.

Download topoplot data (topoplot_data.npz) :
https://drive.google.com/open?id=0B6vtJiCQZUBvaHNUeTROWDBPRG8

.. image:: ../../picture/pictopo/ex_custom_coordinates.png
"""
import numpy as np
from visbrain import Topo

# Load the data :
mat = np.load('topoplot_data.npz')
xyz, data = mat['xyz'], mat['data']
channels = [str(k) for k in range(len(data))]

# Create a topoplot instance :
t = Topo()

# Add the topoplot defined using xyz coordinates :
t.add_topoplot('Topo_1', data, xyz=xyz, channels=channels, title='Custom data',
               cmap='viridis', cblabel='Beta power')

# Show the window :
t.show()
