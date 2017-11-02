"""
Source object definition
========================

Define and customize a source object and then, display those sources.

# .. image:: ../../picture/picbrain/ex_brain_control.png
"""
import numpy as np
from visbrain.objects import SourceObj


# pos = 10*np.random.rand(100, 3)
# # pos = np.sort(pos, axis=0)
# color = np.random.rand(100, 3)
# color = ['orange'] * 50 + ['red'] * 50
# data = np.arange(100)
# mask = np.logical_and(data >= 20, data <= 30)
# text = ['channel' + str(k) for k in range(len(data))]
# visible = np.logical_and(data >= 10, data <= 25)

# s = SourceObj('test', pos, data=data, color=color, mask=mask, text=text,
#               text_size=15, text_bold=True, visible=visible)
# s.edge_width = 1
# s.edge_color = 'orange'
# s.symbol = 'x'
# s.radiusmax = 30.
# s.radiusmin = 10.
# s.alpha = 1.
# s.maskcolor = 'blue'
# s.mask = np.logical_and(data >= 60, data <= 90)
# s.text_shift = (0, 0, 0)
# # s.visible = True#np.logical_and(data >= 1, data <= 60)

# pos2 = np.ones((10, 2))
# text2 = np.array(['Chan' + str(k) for k in range(10)])
# s2 = SourceObj('test2', pos2, data=np.ones((10)), text=text2)

# s += s2
# # print(s.project_modulation.__doc__)


# print(s.project_modulation)
# s.project_repartition
# # s.preview(axis=False)

import pickle
filename = '/home/etienne/Documents/Database/Study/CenterOut/physiology/C_rev_Near-on_r-5_Atlas-Talairach.pickle'
with open(filename, 'rb') as f:
    x = pickle.load(f)
xyz = np.array(x[['X', 'Y', 'Z']])[0:20, :]
text = list(x['Channel'])[0:20]
s = SourceObj('C-rev', xyz, text=text, text_size=10.)
print(x.keys())



analysis = s.analyse_sources(roi_obj=['talairach', 'brodmann'])
# analysis2 = s.analyse_sources(roi_obj='talairach')
print(analysis)
# print(analysis2)
# s.preview()
