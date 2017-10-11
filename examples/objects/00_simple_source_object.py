import numpy as np
from visbrain.objects import SourceObj


pos = 100*np.random.rand(100, 3) + 100
# pos = np.sort(pos, axis=0)
color = np.random.rand(100, 3)
color = ['orange'] * 50 + ['red'] * 50
data = np.arange(100)
mask = np.logical_and(data >= 20, data <= 30)
text = ['channel' + str(k) for k in range(len(data))]
visible = np.logical_and(data >= 10, data <= 25)

s = SourceObj('test', pos, data=data, color=color, mask=mask, text=text,
              text_size=15, text_bold=True, visible=visible)
s.edge_width = 1
s.edge_color = 'orange'
s.symbol = 'x'
s.radiusmax = 30.
s.radiusmin = 10.
s.alpha = 1.
s.maskcolor = 'blue'
s.mask = np.logical_and(data >= 60, data <= 90)
s.text_shift = (0, 0, 0)
# s.visible = True#np.logical_and(data >= 1, data <= 60)

pos2 = np.ones((10, 2))
text2 = np.array(['Chan' + str(k) for k in range(10)])
s2 = SourceObj('test2', pos2, data=np.ones((10)), text=text2)

s += s2
# print(s.project_modulation.__doc__)


print(s.project_modulation.__doc__)
# s.preview(axis=False)
