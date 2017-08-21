"""
Basic topoplot
==============

Basic topographic plot based on channel names.

.. image:: ../../picture/pictopo/ex_basic_topoplot.png
"""
from visbrain import Topo

# Create a topoplot instance :
t = Topo()

# Create a list of channels, data, title and colorbar label :
name = 'Topo_1'
channels = ['C3', 'C4', 'Cz', 'Fz', 'Pz']
data = [10, 20, 30, 10, 10]
title = 'Basic topoplot illustration'
cblabel = 'Colorbar label'

# Add a central topoplot :
t.add_topoplot(name, data, channels=channels, title=title, cblabel=cblabel)

# Show the window :
t.show()
