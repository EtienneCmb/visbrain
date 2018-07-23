"""
Connectivity
============

Add connectivity to the topoplot.

Download topoplot data (topoplot_data.npz) :
https://www.dropbox.com/s/m76y3p0fyj6lxht/topoplot_data.npz?dl=1

.. image:: ../../picture/pictopo/ex_connectivity.png
"""
import numpy as np

from visbrain import Topo
from visbrain.io import download_file

# Load the data :
path = download_file('topoplot_data.npz', astype='example_data')
mat = np.load(path)
xyz, data = mat['xyz'], mat['data']
channels = [str(k) for k in range(len(data))]
n_channels = len(channels)

"""The connectivity is defined by an upper triangle array of shape
(n_channels, n_channels).
In addition, to improve the selection of edges to display, use the boolean
array `c_select` input parameter to select edges that need to be drawn.
"""
connect = (data.reshape(-1, 1) + data.reshape(1, -1)) / 2.
select = connect < 1.97

# Create a topoplot instance :
t = Topo()

# Add the topoplot defined using xyz coordinates :
t.add_topoplot('Topo_1', data, xyz=xyz, title='Connectivity example',
               cblabel='Beta power', c_connect=connect, c_select=select,
               cmap='viridis', c_linewidth=4., c_cmap='plasma')

# Show the window :
t.show()
