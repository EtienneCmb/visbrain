"""
Connectivity
============

Add connectivity to the topoplot.

.. image:: ../../picture/pictopo/ex_connectivity.png
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

t_obj = TopoObj('topo', data, channels=channels, xyz=xyz, cmap='bwr')
cb_obj = ColorbarObj(t_obj, cblabel='Beta power', cbtxtsz=12, txtsz=10.,
                     width=.2, txtcolor='black')

###############################################################################
# Connect channels
###############################################################################
# To connect channels together, we need a 2D array of shape
# (n_channels, n_channels) describing connectivity strength between channels.
# Note that the `visbrain.objects.TopoObj.connect` method basically use the
# `visbrain.objects.ConnectObj` object.

# Create the 2D array of connectivity links :
connect = (data.reshape(-1, 1) + data.reshape(1, -1)) / 2.
# Select only connectivity links with a connectivity strength under 1.97
select = connect < 1.97
# Connect the selected channels :
t_obj.connect(connect, select=select, cmap='inferno', antialias=True,
              line_width=4.)


###############################################################################
# Creation of the scene
###############################################################################
# Finally we create the scene with a white background and a size so that
# topoplot looks rectangular

sc = SceneObj(bgcolor='white', size=(950, 800))
sc.add_to_subplot(t_obj, row=0, col=0, title='Custom data',
                  title_color='black', width_max=800, height_max=800)
sc.add_to_subplot(cb_obj, row=0, col=1, width_max=200)
sc.preview()
