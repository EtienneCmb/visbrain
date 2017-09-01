"""
Plotting properties
===================

Display topographic plots in a grid using several plotting properties.

Download topoplot data (topoplot_data.npz) :
https://drive.google.com/open?id=0B6vtJiCQZUBvaHNUeTROWDBPRG8

.. image:: ../../picture/pictopo/ex_topoplot_plotting_properties.png
"""
import numpy as np
from visbrain import Topo

# Load the data :
mat = np.load('topoplot_data.npz')
xyz, data = mat['xyz'], mat['data']
channels = [str(k) for k in range(len(data))]

kwargs = {'title_size': 3., 'cb_txt_size': 2, 'margin': 15 / 100,
          'chan_offset': (0., 1.1, 0.), 'chan_size': 1.5}

# Create a topoplot instance :
t = Topo()

# Topoplot with 10 regulary spaced levels :
t.add_topoplot('Topo_1', data, xyz=xyz, channels=channels,
               title='Regulary spaced levels', cmap='viridis', levels=10,
               level_colors='Spectral_r', cblabel='Beta power',
               title_color='#ab4642', **kwargs)

"""
Topoplot with custom levels :
    * red : 2.
    * green : 2.2
    * blue : 2.5
"""
level_colors = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
t.add_topoplot('Topo_2', data, xyz=xyz, title='Custom levels', cmap='plasma',
               levels=[2., 2.2, 2.5], level_colors=level_colors,
               cblabel='Beta power', line_color='#3498db', line_width=7.,
               chan_mark_color='gray', bgcolor='#34495e', col=1,
               title_color='white', chan_mark_symbol='cross', cbar=False,
               **kwargs)

# Fixed colorbar limits :
t.add_topoplot('Topo_3', data, xyz=xyz, title='Fixed colorbar limits',
               cmap='Spectral_r', clim=(2., 2.8), channels=channels,
               chan_txt_color='white', chan_mark_symbol='x',
               bgcolor=(.1, .1, .1), title_color='white',
               line_color='white', row=1, **kwargs)

# Colorbar properties :
t.add_topoplot('Topo_4', data, xyz=xyz, title='Colorbar properties',
               cmap='gist_gray', vmin=2., under='slateblue',
               vmax=2.8, over='darkred', title_color='#34495e', col=1, row=1,
               cblabel='Custom color for extrema', **kwargs)

# Show the window :
t.show()
