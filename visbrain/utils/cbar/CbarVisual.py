import numpy as np
from vispy.scene import Node, visuals
import vispy.visuals.transforms as vist
import vispy.scene.cameras as viscam

from visbrain.utils import array2colormap, color2vb, normalize

class CbarVisual(object):
    """Create a colorbar using Vispy."""

    def __init__(self, cmap='viridis', clim=(0, 1), vmin=None, vmax=None,
                 under='gray', over='red', label='', n=100, border=True,
                 txtticks=20, txtcolor='w', width=.14, parent=None):
        """Init."""
        # _____________________ INIT _____________________
        self.cmap, self.clim = cmap, clim
        self.vmin, self.vmax = vmin, vmax
        self.under, self.over = under, over
        self.label = label
        self.border = border
        self.minmax = clim
        self.n = n
        self.sample = np.arange(n)
        self._build()
        print(self._colormap.shape)

        # _____________________ OBJECTS _____________________
        # --------------------- Node ---------------------
        self._cbNode = Node(name='Colorbar', parent=parent)

        # --------------------- Image ---------------------
        self._mImage = visuals.Image(parent=self._cbNode, name='image')
        self._mImage.transform = vist.STTransform(scale=(width, 2/n, 1),
                                                  translate=(0, -1., 0))
        self._mImage.set_data(self._colormap)

        # --------------------- Border ---------------------
        # self.head = visuals.Line(pos=pos, parent=self.headset, name='Head')

        # --------------------- Labels ---------------------
        xshift = 1.62 * width
        # Clim labels :
        self._mClimM = visuals.Text(pos=(xshift, 1., -2.), parent=self._cbNode,
                                    color=txtcolor, font_size=txtticks,
                                    name='Clim_M')
        self._mClimm = visuals.Text(pos=(xshift, -1., -2.), parent=self._cbNode,
                                    color=txtcolor, font_size=txtticks,
                                    name='Clim_m')
        self._mClimm.text = str(clim[0])
        self._mClimM.text = str(clim[1])

        # Cblabel :
        self._mcblabel = visuals.Text(pos=(xshift*1.6, 0, 0),
                                      parent=self._cbNode, color=txtcolor,
                                      font_size=4*txtticks/5, name='clim_M')
        self._mcblabel.rotation = -90
        self._mcblabel.text = str(label)

        # --------------------- Vmin/Vmax ---------------------
        self._vmMNode = Node(name='VminVmax', parent=self._cbNode)
        self._mVm = visuals.Text(pos=(xshift, -vmin/2, -2.),
                                 parent=self._vmMNode, color=txtcolor,
                                 font_size=txtticks, name='Vmin')
        self._mVM = visuals.Text(pos=(xshift, vmax/2, -2.),
                                 parent=self._vmMNode, color=txtcolor,
                                 font_size=txtticks, name='Vmax')
        self._mVm.text = str(vmin)
        self._mVM.text = str(vmax)

    def _build(self):
        sample = normalize(np.arange(self.n), self.clim[0], self.clim[1])
        cp = array2colormap(sample, cmap=self.cmap, vmin=self.vmin,
                            vmax=self.vmax, under=self.under, over=self.over)
        self._colormap = cp[:, np.newaxis, :]

    def set_data(self, data, clim=None, vmin=None, vmax=None, under=None,
                 over=None):
        self._clim = clim
        self.minmax = (data.min(), data.max())

    # ----------- SAMPLE -----------
    @property
    def sample(self):
        """Get the sample value."""
        return self._sample
    
    @sample.setter
    def sample(self, value):
        """Set sample value."""
        self._sample = normalize(value, self.clim[0], self.clim[1])
    





###########################################################################
###########################################################################
###########################################################################
###########################################################################
import vispy
from vispy import scene
canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
# view = canvas.central_widget.add_view()
grid = canvas.central_widget.add_grid(margin=10)
grid.spacing = 0

# Add a title :
color = 'k'
x_label=''
x_heightMax=80
y_label=''
y_widthMax=80
font_size=12
color='k'
title=''
axis_label_margin=50
tick_label_margin=5
titleObj = scene.Label('Mon titre', color=color)
titleObj.height_max = 40
grid.add_widget(titleObj, row=0, col=0, col_span=2)

# Add y-axis :
yaxis = scene.AxisWidget(orientation='left', domain=(0, 129),
                         axis_label=y_label,
                         axis_font_size=font_size,
                         axis_label_margin=axis_label_margin,
                         tick_label_margin=tick_label_margin)
yaxis.width_max = y_widthMax
grid.add_widget(yaxis, row=1, col=0)

# Add x-axis :
xaxis = scene.AxisWidget(orientation='bottom',
                         axis_label=x_label,
                         axis_font_size=font_size,
                         axis_label_margin=axis_label_margin,
                         tick_label_margin=tick_label_margin)
xaxis.height_max = x_heightMax
grid.add_widget(xaxis, row=2, col=1)

# Add right padding :
rpad = grid.add_widget(row=1, col=2, row_span=1)
rpad.width_max = 50

# Main plot :
wc = grid.add_view(row=1, col=1, border_color=color)
###########################################################################
###########################################################################
###########################################################################
###########################################################################


cb = CbarVisual(parent=wc.scene, vmin=.2, n=100, vmax=.9, label='Ceci est mon titre')
camera = viscam.PanZoomCamera(rect=(-1, -1, 2, 2))
wc.camera = camera
xaxis.link_view(wc)
yaxis.link_view(wc)

if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()