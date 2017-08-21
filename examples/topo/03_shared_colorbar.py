"""
Shared colorbar
===============

Add a shared colorbar across topographic plot.

If you have several topographic plot that shared the same color properties
(such as limits, colormap...) it might be redundant to have one colorbar per
topoplot. In that case, use the add_shared_colorbar() to have one shared
colorbar for all subplots.

.. image:: ../../picture/pictopo/ex_shared_colorbar.png
"""
import numpy as np
from visbrain import Topo

# Create a topoplot instance :
t = Topo()

# Define the list of channels :
channels = ['C1', 'C2', 'C3', 'C4', 'Cz', 'FCz', 'CPz', 'Fz', 'Pz', 'FC1',
            'FC2', 'FC3', 'FC4', 'CP3', 'CP4', 'CP1', 'CP2', 'F3', 'F4', 'P3',
            'P4', 'C5', 'C6']
n_channels = len(channels)

# Generate 4 random datasets :
data_1 = np.random.randn(n_channels)
data_2 = np.random.randn(n_channels)
data_3 = np.random.randn(n_channels)
data_4 = np.random.randn(n_channels)

"""It is more save to define one dictionnary with all of the color properties
and to use the same dictionnary across all topoplots.

"""
kwargs = {'cmap': 'viridis', 'clim': (-1.02, 1.01), 'vmin': -.81,
          'under': 'gray', 'vmax': .85, 'over': 'red'}

"""
Create the (2, 2) topoplot grid with the random datasets. The colorbar is
disabled for each one of those subplots.
"""
t.add_topoplot('Topo_1', data_1, channels=channels, cbar=False, row=0, col=0,
               **kwargs)
t.add_topoplot('Topo_2', data_2, channels=channels, cbar=False, row=0, col=1,
               **kwargs)
t.add_topoplot('Topo_3', data_3, channels=channels, cbar=False, row=1, col=0,
               **kwargs)
t.add_topoplot('Topo_4', data_4, channels=channels, cbar=False, row=1, col=1,
               **kwargs)

"""Finally, add the shared colorbar. This colorbar is on the last column
(col=2) and take all rows (row_span=2).

The rect input is a tuple defined by (x_start, y_start, width, heigth). This
variable can be used to :
    * Translate the colorbar (using x_start and y_start) to be closer to the
    subplots.
    * Scale the colorbar to have a nice proportion between width and heigth.
"""
t.add_shared_colorbar('Shared', col=2, row_span=2, rect=(0.1, -2, 1.6, 4),
                      cblabel='Shared colorbar', **kwargs)

# Show the window :
t.show()
