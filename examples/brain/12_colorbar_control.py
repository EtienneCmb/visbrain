"""
Colorbar control
================

Control the colorbar of selected objects. The colormap of three objects can
actually be controlled :

    * Cortical projection / repartition (name = 'Projection')
    * Pictures (name = 'Pictures')
    * Connectivity (name = 'Connectivity')

In this example we define some sources with some random data, random pictures
and random connections and set the colorbar for each object. Here's the list of
parameters to control each colorbar :

    * cmap : Matplotlib colormap (like 'viridis', 'inferno'...).
    * clim : Colorbar limit. Every values under / over clim will clip.
    * isvmin : Activate/deactivate vmin.
    * vmin : Every values under vmin will have the color defined by under.
    * under : Matplotlib color under vmin.
    * isvmax : Activate/deactivate vmax.
    * vmax : Every values over vmin will have the color defined by over.
    * over :  Matplotlib color over vmax.
    * cblabel : Colorbar label.
    * cbtxtsz : Text size of the colorbar label.
    * cbtxtsh : Shift for the colorbar label.
    * txtcolor : Text color.
    * txtsz : Text size for clim/vmin/vmax text.
    * txtsh : Shift for clim/vmin/vmax text.
    * border : Display colorbar borders.
    * bw : Border width.
    * limtxt : Display vmin/vmax text.
    * bgcolor : Background color of the colorbar canvas.
    * ndigits : Number of digits for the text.

Download source's coordinates (xyz_sample.npz) :
https://drive.google.com/open?id=0B6vtJiCQZUBvSFJvaTFSRDJvMEE

.. image:: ../../picture/picbrain/ex_colorbar_control.png
"""
from __future__ import print_function

import numpy as np

from visbrain import Brain, Colorbar


"""
Define some sources with random data between [0, 100.]
"""
n_sources = 50
s_xyz = np.load('xyz_sample.npz')['xyz'][:n_sources, :]
s_data = 100. * np.random.rand(n_sources)

"""
Define random connectivity with connectivity strength between [12.1 and 15.23].
We used a masked array to hide connections that are not comprised in this
interval
"""
c_connect = 100. * np.random.rand(n_sources, n_sources)
mask = np.logical_and(12.1 <= c_connect, c_connect < 15.23)
c_connect = np.ma.masked_array(c_connect, mask=~mask)

"""
Define random pictures with values between [0, 50]. Each picture have 10 rows
and 20 columns
"""
pic_data = 50. * np.random.rand(n_sources, 10, 20)


"""
Define the Brain instance and pass variables for sources, pictures and
connections
"""
vb = Brain(s_xyz=s_xyz, s_data=s_data, a_template='B3', c_connect=c_connect,
           pic_data=pic_data)

"""
Set the Brain opaque to visualize the cortical projection :
"""
vb.brain_control(transparent=False)

"""
The colormap of the projection can't be controlled without running it. So we
print the list of controllable objects before and after the cortical
projection. Note that the code below is the same for the cortical_repartition()
method.
"""
print("List of controllable objects before projection : ", vb.cbar_list())
vb.cortical_projection()
print("List of controllable objects after projection : ", vb.cbar_list())


"""
Control the colorbar / colormap of cortical projection
"""
vb.cbar_control('Projection', cmap='Spectral_r', clim=(10.2, 95.1), vmin=15.4,
                under='#ab4642', bgcolor=(0., .1, 0.), cbtxtsz=4., isvmin=True,
                cblabel='Cortical projection', vmax=90.4, isvmax=True,
                over=(.1, .1, .1))

"""
Control the colorbar / colormap of pictures. The cbar_autoscale() method
fit the limit of the colorbar to the (minimum, maximum) across all pictures
"""
vb.cbar_autoscale('Pictures')
vb.cbar_control('Pictures', cmap='inferno', isvmin=True, vmin=20.3,
                under=(.7, .7, .7), cblabel='My Pictures', cbtxtsz=3.)

"""
Control the colorbar / colormap of connectivity.
"""
vb.cbar_autoscale('Connectivity')
vb.cbar_control('Connectivity', cmap='Reds', bgcolor='orange',
                txtcolor='black', cblabel='Connect sources', isvmin=True,
                vmin=13.012, under='black', ndigits=6, isvmax=True, vmax=14.8,
                over='slateblue', cbtxtsz=3., cbtxtsh=3.)

"""
Finally, set the colorbar of the projecton visible
"""
vb.cbar_select('Projection', visible=True)

"""
Visbrain also have a Colorbar module dedicated to colorbar managment. As a
consequence, we can use the cbar_export() to get all of the colorbars and
open a Colorbar instance
"""
# Get all colorbars
# args = vb.cbar_export(get_dict=True)
# Save all colorbars
# vb.cbar_export(filename='colorbar_config.txt')
# Save only the colorbar of Pictures and Projection :
# vb.cbar_export(filename='pic_and_proj.txt',
#                export_only=['Pictures', 'Projection'])
# Open the Colorbar colorbar :
# Colorbar(config=args).show()

vb.show()
