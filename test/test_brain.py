
import numpy as np
from warnings import warn

from visbrain.brain import Brain


# def test_brain_gui():
#     vb = Brain()
#     vb._app.exit()

# def test_brain_user_functions():
#     """Test brain rotation."""

#     # ---------------- VARIABLES  ----------------
#     kwargs = {}
#     # Define some random sources :
#     kwargs['s_xyz'] = np.random.randint(-20, 20, (10, 3))
#     sdata = 100 * np.random.rand(10)
#     scolor = ['blue'] * 3 + ['white'] * 3 + ['red'] * 4
#     smask = np.array([True + False] + [True] * 9)
#     scmap = {'clim': (-1, 1), 'vmin': .3, 'under': 'gray', 'vmax': .7,
#              'over': (1., 0.5, 0.2), 'cmap': 'magma_r'}

#     # Connectivity array :
#     c_connect = np.random.rand(10, 10)
#     c_connect[np.tril_indices_from(c_connect)] = 0
#     c_connect = np.ma.masked_array(c_connect, mask=True)
#     nz = np.where((c_connect > .6) & (c_connect < .7))
#     c_connect.mask[nz] = False
#     kwargs['c_connect'] = c_connect

#     # Define a Brain instance :
#     vb = Brain(**kwargs)

#     # ---------------- ROTATION  ----------------
#     # Predefined rotation :
#     vb.rotate(fixed='sagittal_1')
#     # Custom rotation :
#     vb.rotate(custom=(90.0, 0.0))

#     # ---------------- BACKGROUND COLOR  ----------------
#     # Set the background color (using a RGB tuple) :
#     vb.background_color(color=(1., 1., 1.))
#     # Set the background color (using matplotlib format) :
#     vb.background_color(color='white')
#     # Set the background color (using hexadecimal format) :
#     vb.background_color(color='#ffffff')

#     # ---------------- SCREENSHOT  ----------------
#     pass

#     # ---------------- LOAD / SAVE CONFIG  ----------------
#     pass

#     # ---------------- BRAIN CONTROL  ----------------
#     vb.brain_control(template='B3', hemisphere='right', visible=False)
#     vb.brain_control(template='B2', hemisphere='left')
#     vb.brain_control(transparent=False)
#     vb.brain_control(alpha=.7, color='black')

#     # ---------------- ADD MESH  ----------------
#     # Get convex hull :
#     # cvh = vb.sources_to_convex_hull(kwargs['s_xyz'])
#     # vb.add_mesh('mymesh', kwargs['s_xyz'], cvh)

#     # ---------------- SOURCES DATA  ----------------
#     # Send data :
#     vb.sources_control(data=sdata, symbol='x', radiusmin=1., radiusmax=20.,
#                        color=scolor, edgecolor='orange', edgewidth=2,
#                        mask=smask, maskcolor='blue')
#     # Set opacity :
#     vb.sources_opacity(alpha=0.1, show=True)
#     # Test visibility :
#     allviz = ('outside', 'none', 'left', 'right', 'inside', 'all')
#     for k in allviz:
#         vb.sources_display(k)

#     # ---------------- PROJECTION  ----------------
#     # Projection / repartition on brain :
#     vb.cortical_projection(radius=20, project_on='brain', contribute=True,
#                            **scmap)
#     vb.cortical_repartition(radius=20, project_on='brain', contribute=True,
#                             **scmap)
#     # Change colormap :
#     vb.sources_colormap(cmap='Spectral', vmin=20, vmax=60, under='orange',
#                         over='black', clim=(10, 80), cblabel='Mon titre')
#     # Force sources to fit on the brain :
#     vb.sources_fit('brain')
#     # Add new sources :
#     vb.add_sources('NewSources', s_xyz=np.random.randint(-20, 20, (10, 3)),
#                    s_cmap='viridis')

#     # ---------------- CONNECTIVITY  ----------------
#     # Test coloring :
#     for k in ['strength', 'count', 'density']:
#         vb.connect_control(colorby=k, dynamic=(.1, .7), cmap='jet',
#                            clim=(.4, .8), vmin=.5, vmax=.75, under='gray',
#                            over=(.1, .1, .1), cblabel='Colorby ' + k)
#     # Test to add connectivity object :
#     vb.add_connect('NewObject', c_connect=c_connect, c_xyz=kwargs['s_xyz'])

#     # ---------------- ROI  ----------------
#     # Add roi :
#     vb.roi_control(selection=[3, 5], subdivision='Brodmann', smooth=5)
#     # Transparency :
#     vb.roi_light_reflection('external')
#     vb.roi_light_reflection('internal')
#     vb.roi_opacity(alpha=0.1, show=True)
#     # ROI list :
#     vb.roi_list('AAL')
#     vb.roi_list('Brodmann')
#     # Projection :
#     vb.cortical_projection(radius=50, project_on='roi', contribute=True,
#                            **scmap)
#     vb.cortical_repartition(radius=50, project_on='roi', contribute=True,
#                             **scmap)
#     # Force sources to fit on the brain :
#     vb.sources_fit('roi')

#     # ---------------- CBAR  ----------------
#     # Properties :
#     vb.cbar_control('Projection', cmap='Reds_r', clim=(12, 24), isvmin=False,
#                     vmin=13, under='#ab4642', isvmax=True, vmax=23.4567,
#                     over=(.1, .1, 1.), cblabel='Tit', cbtxtsz=7.2,
#                     cbtxtsh=3., txtcolor='orange', txtsz=2, border=True,
#                     bw=2., limtxt=True, bgcolor='slateblue', ndigits=6)
#     # Autoscale :
#     vb.cbar_autoscale('Connectivity')
#     vb.cbar_autoscale('Projection')

#     # vb.show()
