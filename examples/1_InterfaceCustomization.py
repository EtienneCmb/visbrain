"""Start with some possible customization for the ui and for the brain
template
"""
from visbrain import vbrain


# For the color definition, you can use matplotlib 
# colors ('b', 'r', 'slaeblue'...), RBG tuple (1,1,0) or hexadecimal ('#e74c3c')
ui_bgcolor = '#34495e' 		# Background color for the ui.
a_color = (0.9, 0.29, 0.24)	# Brain color
a_opacity = 1.0				# Opacity of the brain
a_template = 'B3'			# Change the template of the brain to a smoothest one
a_projection = 'external'	# Change the render for an external one

vb = vbrain(ui_bgcolor=ui_bgcolor, a_color=a_color, a_opacity=a_opacity,
            a_template=a_template, a_projection=a_projection)

vb.show()