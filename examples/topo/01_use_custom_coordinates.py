"""
Use custom coordinates
======================

Display topographic plots using custom coordinates.

Download topoplot data (topoplot_data.npz) :
https://www.dropbox.com/s/m76y3p0fyj6lxht/topoplot_data.npz?dl=1

.. image:: ../../picture/pictopo/ex_custom_coordinates.png
"""
import numpy as np

from visbrain import Topo
from visbrain.io import download_file

# Load the data :
path = download_file('topoplot_data.npz', astype='example_data')
mat = np.load(path)
xyz, data = mat['xyz'], mat['data']
channels = [str(k) for k in range(len(data))]

# Create a topoplot instance :
t = Topo()

# Add the topoplot defined using xyz coordinates :
t.add_topoplot('Topo_1', data, xyz=xyz, channels=channels, title='Custom data',
               cmap='viridis', cblabel='Beta power')

# Show the window :
t.show()
