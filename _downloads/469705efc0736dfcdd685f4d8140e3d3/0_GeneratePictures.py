"""
Generate pictures
=================

This script generate some figures using the Brain module. Those exported
pictures are going to be set in a layout in the 1_LayoutExample.py script.
"""
import numpy as np
from visbrain.gui import Brain


kwargs = {}

# Generate some random coordinates and data :
N = 500   # Number of sources
kwargs['s_xyz'] = np.random.randint(-70, 70, (N, 3))
kwargs['s_data'] = np.random.rand(N)
kwargs['s_radiusmin'] = 1.
kwargs['s_radiusmax'] = 20.

n_connections = 150
rnd_selection = np.random.randint(0, N ** 2, n_connections)
connect = np.random.randint(0, 20, (N, N))
mask = np.ones(N ** 2, dtype=bool)
mask[rnd_selection] = False
mask = mask.reshape(N, N)
connect = np.ma.masked_array(connect, mask=mask)
kwargs['c_connect'] = connect

kwargs['ui_bgcolor'] = 'white'

vb = Brain(**kwargs)


# ============= Sources =============
# # Screenshot of the default view :
vb.screenshot('default.png', autocrop=True)

# Hide sources that are not in the brain :
vb.sources_display('inside')
vb.screenshot('inside.png', autocrop=True)

# ============= Connectivity =============
# Colorby network density :
vb.sources_display('none')
vb.connect_control(show=True, cmap='magma', colorby='density', clim=(0., 35.),
                   vmin=10., vmax=30., under='gray', over='darkred',
                   dynamic=(.7, 1.))
vb.screenshot('density.png', autocrop=True)
# Color by number of connections per node :
vb.connect_control(show=True, cmap='viridis', colorby='count', clim=(1., 5.),
                   vmin=0., vmax=10., dynamic=(.1, 1.))
vb.screenshot('count.png', autocrop=True)

# ============= Projection =============
vb.connect_control(show=False)
vb.sources_display('all')
vb.cortical_repartition(cmap='viridis', clim=(1., 6.), vmin=2., under='gray',
                        vmax=4., over='#ab4642', radius=16.)
vb.brain_control(transparent=False)
vb.sources_opacity(show=False)
vb.rotate(custom=(-125., 0.))
vb.screenshot('repartition.jpg', autocrop=True)

vb.sources_display('all')
vb.roi_control(selection=[4, 6], roi_type='Brodmann', smooth=5)
vb.cortical_projection(project_on='roi', radius=12., cmap='inferno',
                       clim=(.1, .5), vmin=0., vmax=6.)
vb.sources_display('none')
vb.brain_control(template='B3')
vb.brain_control(transparent=True)
vb.rotate('coronal')
vb.screenshot('roi.jpg', autocrop=True)

vb.show()
