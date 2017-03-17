"""This is the most basic example to illustrate how to start a Brain instance
and visualize a basic standard MNI brain.
"""
from visbrain import Brain


# ********************************************************************
# 0 - Create a Brain instance without any customization
# ********************************************************************
vb = Brain(a_template='B3')
vb.show()

