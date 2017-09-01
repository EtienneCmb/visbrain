"""
Add pictures
============

This example demonstrate how to display small pictures attached to sources. The
pictures can then be controlled from the GUI in the Sources/Pictures tab.

Download source's coordinates (xyz_sample.npz) :
https://drive.google.com/open?id=0B6vtJiCQZUBvSFJvaTFSRDJvMEE

.. image:: ../../picture/picbrain/ex_pictures.png
"""
from visbrain import Brain
import numpy as np

kwargs = {}
# Load the xyz coordinates and corresponding subject name :
s_xyz = np.load('xyz_sample.npz')['xyz']
s_xyz = s_xyz[4::10, ...]
kwargs['s_text'] = [str(k) for k in range(s_xyz.shape[0])]
kwargs['s_textsize'] = 1.5
n_sources = s_xyz.shape[0]

sf = 1024.
n = 50
x, y = np.ogrid[0:n / 2, 0:n / 2]
x, y = np.append(x, np.flip(x, 0)), np.append(y, np.flip(y, 1))
time = (x.reshape(-1, 1) + y.reshape(1, -1)) / sf
time = np.tile(time[np.newaxis, ...], (n_sources, 1, 1))
coef = s_xyz[:, 0].reshape(-1, 1, 1) / 2.
kwargs['pic_data'] = np.sinc(coef * 2 * np.pi * 1. * time)
kwargs['pic_data'] += .2 * np.random.rand(*kwargs['pic_data'].shape)

# If you want to remove some pictures, define a pic_select array of boolean
# values and specify if those pictures has to be hide or displayed :
pic_select = np.ones((n_sources,), dtype=bool)
pic_to_hide = [2, 6, 10, 11, 31, 35, 41, 44, 51, 55]
pic_select[pic_to_hide] = False
kwargs['pic_select'] = pic_select

kwargs['pic_width'] = 5.            # Width
kwargs['pic_height'] = 5.           # Height
kwargs['pic_dxyz'] = (4., 5., 1.)   # Offset along (x, y, z) axis
kwargs['pic_clim'] = (.01, 1.12)    # Colorbar limits
kwargs['pic_cmap'] = 'viridis'      # Colormap
# kwargs['pic_vmin'] = .1             # Vmin
# kwargs['pic_under'] = 'gray'        # Color under vmin
# kwargs['pic_vmax'] = .9             # Vmax
# kwargs['pic_over'] = '#ab4642'      # Color over vmax

b = Brain(s_xyz=s_xyz, **kwargs)
b.show()
