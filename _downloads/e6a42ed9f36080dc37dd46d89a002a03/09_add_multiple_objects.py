"""
Add multiple objects to the scene
=================================

Add multiple source's and connectivity object to the scene.

Download source's coordinates (xyz_sample.npz) :
https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1

.. image:: ../../_static/examples/ex_add_multiple_objects.png
"""
from __future__ import print_function
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import SourceObj, ConnectObj
from visbrain.io import download_file

print(__doc__)

# Create an empty kwargs dictionnary :
kwargs = {}

# Load the xyz coordinates and corresponding subject name :
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
s_xyz, subjects = mat['xyz'], mat['subjects']

"""
Separate source's coodinates : in this part, first we find where sources
are in the left hemisphere, then in the right hemisphere and in front and
finally right hemisphere back :
"""
s_xyz_l = s_xyz[s_xyz[:, 0] <= 0, :]
s_xyz_rb = s_xyz[np.logical_and(s_xyz[:, 0] > 0, s_xyz[:, 1] <= 0), :]
s_xyz_rf = s_xyz[np.logical_and(s_xyz[:, 0] > 0, s_xyz[:, 1] > 0), :]

data_l = np.random.uniform(-10, 10, s_xyz_l.shape[0])


###############################################################################
#                                 SOURCES
###############################################################################
"""Create a first source object with uniform red square markers
"""
s_obj_l = SourceObj('S_left', s_xyz_l, data=data_l, color='red',
                    edge_color='white', symbol='disc', edge_width=2.,
                    radius_min=10., radius_max=20., alpha=.4)

"""Color the sources according to data
"""
s_obj_l.color_sources(data=data_l, cmap='plasma')

"""Create a second source object. Then, we analyse where are located the
sources using the AAL region of interest and used color according to gyrus
"""
s_obj_rb = SourceObj('S_right_back', s_xyz_rb, symbol='arrow', radius_min=20.,
                     edge_width=0., text_color='white', text_size=1.,
                     text_bold=True)
"""Analyse where the source are located using the Brodmann area (BA) atlas.
This method returns a pandas.DataFrame
"""
df = s_obj_rb.analyse_sources('brodmann')
# print(df.keys())
"""Then, color the sources according to the BA. Without further arguments,
this function use random colors for each BA :
"""
s_obj_rb.color_sources(df, 'brodmann')
"""Finally, set the name of the BA for the text :
"""
s_obj_rb.text = df['brodmann']

"""Create a third source object
"""
s_obj_rf = SourceObj('S_right_front', s_xyz_rf, symbol='ring', radius_min=10.,
                     edge_width=0., alpha=.8)
"""Analyse source's locations using the Talairach atlas
"""
df = s_obj_rf.analyse_sources('talairach')

"""Color source's according to the lobe location. This time we set different
colors to lobes :
"""
custom_color = {'Frontal': 'orange', 'Temporal': 'green', 'Sub-lobar': 'red'}
color_others = 'gray'  # color of every sources that are not in custom_color
hide_others = False    # hide every sources that are not in custom_color
s_obj_rf.color_sources(analysis=df, color_by='lobe', roi_to_color=custom_color,
                       color_others=color_others, hide_others=hide_others)

###############################################################################
#                            CONNECTIVITY
###############################################################################

# Function in order to create random connection dataset for each
# source object :


def create_connect(xyz, min, max):
    """Create connectivity dataset."""
    # Create a random connection dataset :
    connect = np.random.uniform(-100., 100., (len(xyz), len(xyz)))
    # Mask the connection aray :
    connect = np.ma.masked_array(connect, False)
    # Hide lower triangle :
    connect.mask[np.tril_indices_from(connect.mask)] = True
    # Hide connexions that are not between min and max :
    connect.mask[np.logical_or(connect.data < min,
                               connect.data > max)] = True
    return connect


"""Create two connectivity objects.
"""
connect_l = create_connect(s_xyz_l, -.5, .2)
c_obl_l = ConnectObj('C_left', s_xyz_l, connect_l, color_by='strength',
                     dynamic=(.1, 1.), cmap='viridis', vmin=0., vmax=.1,
                     under='gray', over='red')

connect_rb = create_connect(s_xyz_rb, -.5, .2)
c_obj_rb = ConnectObj('C_right_back', s_xyz_rb, connect_rb, color_by='count',
                      alpha=.7, cmap='plasma')

"""Finally, open _Brain_ with those list of objects
"""
vb = Brain(source_obj=[s_obj_l, s_obj_rb, s_obj_rf],
           connect_obj=[c_obl_l, c_obj_rb])
vb.show()
