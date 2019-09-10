"""
Connect deep sources
====================

Display and customize connectivity. To this end, we define some deep sources
and connect them.

Download source's coordinates (xyz_sample.npz) :
https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1

.. image:: ../../_static/examples/ex_connectivity.png
"""
from __future__ import print_function
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import SourceObj, ConnectObj
from visbrain.io import download_file

# Create an empty kwargs dictionnary :
kwargs = {}

# ____________________________ DATA ____________________________

# Load the xyz coordinates and corresponding subject name :
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
xyz, subjects = mat['xyz'], mat['subjects']

N = xyz.shape[0]  # Number of electrodes

# Now, create some random data between [-50,50]
data = np.random.uniform(-50, 50, len(subjects))

"""Create the source object :
"""
s_obj = SourceObj('SourceObj1', xyz, data, color='crimson', alpha=.5,
                  edge_width=2., radius_min=2., radius_max=10.)

"""
To connect sources between them, we create a (N, N) array.
This array should be either upper or lower triangular to avoid
redondant connections.
"""
connect = 1000 * np.random.rand(N, N)		# Random array of connections
connect[np.tril_indices_from(connect)] = 0  # Set to zero inferior triangle

"""
Because all connections are not necessary interesting, it's possible to select
only certain either using a select array composed with ones and zeros, or by
masking the connection matrix. We are giong to search vealues between umin and
umax to limit the number of connections :
"""
umin, umax = 30, 31

# 1 - Using select (0: hide, 1: display):
select = np.zeros_like(connect)
select[(connect > umin) & (connect < umax)] = 1

# 2 - Using masking (True: hide, 1: display):
connect = np.ma.masked_array(connect, mask=True)
connect.mask[np.where((connect > umin) & (connect < umax))] = False

print('1 and 2 equivalent :', np.array_equal(select, ~connect.mask + 0))

"""Create the connectivity object :
"""
c_obj = ConnectObj('ConnectObj1', xyz, connect, color_by='strength',
                   dynamic=(.1, 1.), cmap='gnuplot', vmin=umin + .2,
                   vmax=umax - .1, under='red', over='green',
                   clim=(umin, umax), antialias=True)

"""Finally, pass source and connectivity objects to Brain :
"""
vb = Brain(source_obj=s_obj, connect_obj=c_obj)

vb.show()
