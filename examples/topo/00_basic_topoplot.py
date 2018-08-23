"""
Basic topoplot
==============

Basic topographic plot based on channel names.

.. image:: ../../picture/pictopo/ex_basic_topoplot.png
"""
from visbrain.objects import TopoObj, ColorbarObj, SceneObj

###############################################################################
# Generate data
###############################################################################
# First, we need to create some random data. Here, we define a list of eeg
# channel names and set one value per channel

channels = ['C3', 'C4', 'Cz', 'Fz', 'Pz']
data = [10, 20, 30, 10, 10]

###############################################################################
# Create the topoplot object
###############################################################################
# Then we pass the channel names and data to the topo object (TopoObj) and
# create a colorbar object based on the topoplot.

t_obj = TopoObj('topo', data, channels=channels)
cb_obj = ColorbarObj(t_obj, cblabel='Colorbar label', cbtxtsz=12, txtsz=10.,
                     width=.2, txtcolor='black')

###############################################################################
# Creation of the scene
###############################################################################
# Finally we create the scene with a white background and a size so that
# topoplot looks rectangular

sc = SceneObj(bgcolor='white', size=(950, 800))
sc.add_to_subplot(t_obj, row=0, col=0, title='Basic topoplot',
                  title_color='black')
sc.add_to_subplot(cb_obj, row=0, col=1, width_max=200)
sc.preview()
