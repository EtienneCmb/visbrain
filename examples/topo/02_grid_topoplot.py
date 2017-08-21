"""
Grid topoplot
=============

Display topographic plots into a grid.

.. image:: ../../picture/pictopo/ex_grid_topoplot.png
"""
from visbrain import Topo

# Create a topoplot instance :
t = Topo()

# Create a list of channels, data, title and colorbar label :
channels = ['C3', 'C4', 'Cz', 'Fz', 'Pz']
data = [10, 20, 30, 10, 10]
kwargs = {'title_size': 2., 'cb_txt_size': 2, 'margin': 20 / 100,
          'chan_offset': (0., 0.08, 0.)}

# Position (0, 0)
t.add_topoplot('Topo_1', data, channels=channels, title='Topo_1',
               cmap='viridis', row=0, col=0, **kwargs)

# Position (0, 1)
t.add_topoplot('Topo_2', data, channels=channels, title='Topo_2',
               cmap='plasma', row=0, col=1, **kwargs)

# Position (1, 0)
t.add_topoplot('Topo_3', data, channels=channels, title='Topo_3',
               cmap='Spectral_r', row=1, col=0, **kwargs)

# Position (1, 1)
t.add_topoplot('Topo_4', data, channels=channels, title='Topo_4',
               cmap='gist_stern', row=1, col=1, **kwargs)

# Position (2, 0:1)
t.add_topoplot('Topo_5', data, channels=channels, title='Topo_5',
               cmap='Blues', row=2, col=0, col_span=2, **kwargs)

# Position (0:3, 2)
t.add_topoplot('Topo_6', data, channels=channels, title='Topo_6',
               cmap='Reds', row=0, col=2, row_span=3, **kwargs)

# Show the window :
t.show()
