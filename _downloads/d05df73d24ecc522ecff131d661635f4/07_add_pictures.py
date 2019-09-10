"""
Add pictures
============

This example demonstrate how to display small pictures attached to sources. The
pictures can then be controlled from the GUI in the Sources/Pictures tab.

Download source's coordinates (xyz_sample.npz) :
https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1

.. image:: ../../_static/examples/ex_pictures.png
"""
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import Picture3DObj, SourceObj
from visbrain.io import download_file

kwargs = {}
# Load the xyz coordinates and corresponding subject name :

s_xyz = np.load(download_file('xyz_sample.npz', astype='example_data'))['xyz']
s_xyz = s_xyz[4::10, ...]
n_sources = s_xyz.shape[0]

"""Define a source object
"""
s_obj = SourceObj('MySources', s_xyz, symbol='disc', color='green')

"""Define picture data
"""
sf = 1024.
n = 50
x, y = np.ogrid[0:n / 2, 0:n / 2]
x, y = np.append(x, np.flip(x, 0)), np.append(y, np.flip(y, 1))
time = (x.reshape(-1, 1) + y.reshape(1, -1)) / sf
time = np.tile(time[np.newaxis, ...], (n_sources, 1, 1))
coef = s_xyz[:, 0].reshape(-1, 1, 1) / 2.
data = np.sinc(coef * 2 * np.pi * 1. * time)
data += .2 * np.random.rand(*data.shape)

"""If you want to remove some pictures, define a pic_select array of boolean
values and specify if those pictures has to be hide or displayed :
"""
pic_select = np.ones((n_sources,), dtype=bool)
pic_to_hide = [2, 6, 10, 11, 31, 35, 41, 44, 51, 55]
pic_select[pic_to_hide] = False
kwargs['select'] = pic_select

kwargs['pic_width'] = 5.             # Width
kwargs['pic_height'] = 5.            # Height
kwargs['translate'] = (4., 5., 1.)   # Offset along (x, y, z) axis
kwargs['clim'] = (.01, 1.12)         # Colorbar limits
kwargs['cmap'] = 'viridis'           # Colormap
kwargs['vmin'] = .1                  # Vmin
kwargs['under'] = 'gray'             # Color under vmin
kwargs['vmax'] = .9                  # Vmax
kwargs['over'] = '#ab4642'           # Color over vmax
kwargs['cblabel'] = '3D Pictures'    # Color over vmax

"""Define the 3-D picture object
"""
pic = Picture3DObj('Pic', data, s_xyz, **kwargs)

vb = Brain(picture_obj=pic, source_obj=s_obj)
vb.show()
