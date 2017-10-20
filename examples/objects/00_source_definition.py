"""
Source object definition
========================

Define and customize a source object and then, display those sources.

# .. image:: ../../picture/picbrain/ex_brain_control.png
"""
import numpy as np
import vispy
import sys
from visbrain.objects import SourceObj


n_sources = 100
pos = np.random.uniform(-10, 10, n_sources)
color = np.random.rand(100, 3)
color = ['orange'] * 50 + ['red'] * 50
data = np.arange(100)
mask = np.logical_and(data >= 20, data <= 30)
text = ['channel' + str(k) for k in range(len(data))]
visible = np.logical_and(data >= 10, data <= 25)

s = SourceObj('test', pos, data=data, color=color, mask=mask, text=text,
              text_size=15, text_bold=True, visible=visible)
s.preview()