"""
Open the colorbar editor
========================

Open the colorbar editor and pass inputs to control it.

.. image:: ../../picture/piccbar/ex_open_editor.png
"""
from visbrain import Colorbar

cb = Colorbar(vmin=.1, under='slateblue', vmax=.8, over='olive',
              cmap='viridis', ndigits=4, cblabel='oki !', border=False,
              name='Example1')
cb.show()
