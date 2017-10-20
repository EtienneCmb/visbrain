import numpy as np
import vispy
import sys

from visbrain.objects import ConnectObj, SourceObj, CombineConnect
from visbrain.visuals import VisbrainCanvas

c = VisbrainCanvas(show=True, )




# n_sources = 4
# edges = np.arange(n_sources * n_sources).reshape(n_sources, n_sources)
# # select = np.zeros_like(edges).astype(bool)
# # select[0, :] = True
# # select[-2, :] = True
# nodes = np.array([[0, 0],
#                   [1, 0],
#                   [1, 1],
#                   [0, 1]])
# select = np.array([[False, True, False, True],
#                    [False, False, True, True],
#                    [False, False, False, True],
#                    [False, False, False, False]])

nodes = np.random.rand(100, 3)
edges = np.random.rand(100, 100)
select = np.logical_and(edges >= .5, edges <= .52)
text = ['s' + str(k) for k in range(100)]

s1 = SourceObj('Source1', nodes, text=text, text_size=30, parent=c.wc.scene,
               text_shift=(0., 0.02, 0.), text_bold=True)
co = ConnectObj('connect', nodes, edges, select, color_by='count', line_width=3, dynamic=None, custom_colors={5: 'red', 4: 'orange', None: 'lightgray'})
co2 = ConnectObj('connect2', np.random.rand(100, 3), edges, select, color_by='strength', line_width=5)
co2.alpha = .1

coo = CombineConnect([co, co2], parent=c.wc.scene)

# from visbrain.brain.base.ConnectBase import ConnectBase

# ConnectBase(nodes, nodes, edges, select)

c.camera = co._get_camera()

if sys.flags.interactive != 1:
    vispy.app.run()