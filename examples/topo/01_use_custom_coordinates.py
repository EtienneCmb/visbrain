"""
Use custom coordinates
======================

Display topographic plots using custom coordinates.

.. image:: ../../picture/pictopo/ex_custom_coordinates.png
"""
import numpy as np

from visbrain.objects import TopoObj, ColorbarObj, SceneObj
from visbrain.io import download_file

###############################################################################
# Download data
###############################################################################
# First, we download the data. A directory should be created to
# ~/visbrain_data/example_data. This example contains beta power for several
# channels defined by there xy coordinates.

path = download_file('topoplot_data.npz', astype='example_data')
mat = np.load(path)
xyz, data = mat['xyz'], mat['data']
channels = [str(k) for k in range(len(data))]

###############################################################################
# Create the topoplot object
###############################################################################
# Then we pass the channel names and data to the topo object (TopoObj) and
# create a colorbar object based on the topoplot.

t_obj = TopoObj('topo', data, channels=channels, xyz=xyz)
cb_obj = ColorbarObj(t_obj, cblabel='Beta power', cbtxtsz=12, txtsz=10.,
                     width=.2, txtcolor='black')

###############################################################################
# Creation of the scene
###############################################################################
# Finally we create the scene with a white background and a size so that
# topoplot looks rectangular

sc = SceneObj(bgcolor='white', size=(950, 800))
sc.add_to_subplot(t_obj, row=0, col=0, title='Custom data',
                  title_color='black')
sc.add_to_subplot(cb_obj, row=0, col=1, width_max=200)
sc.preview()
