import numpy as np
from vispy.scene import Node, visuals
import vispy.visuals.transforms as vist
import vispy.scene.cameras as viscam

from visbrain.utils import array2colormap, color2vb, normalize


class CbarVisual(object):
    """Create a colorbar using Vispy."""

    def __init__(self, cmap='viridis', clim=(0, 1), vmin=None, vmax=None,
                 under='gray', over='red', cblabel='', border=True,
                 txtsz=20, cbtxtsz=26, txtcolor='w', width=.14, parent=None,
                 vminmax=True, ndigits=2):
        """Init."""
        # _____________________ INIT _____________________
        self._n = 1000
        self._xsh = 1.2
        self._ratio = 4/5
        self._cmap, self._clim = cmap, clim
        self._vmin, self._vmax = vmin, vmax
        self._under, self._over = under, over
        self._cblabel = cblabel
        self._border = border
        self._minmax = clim
        self._ndigits = ndigits
        self._vminmax = vminmax
        self._txtsz = txtsz
        self._cbtxtsz = cbtxtsz

        # _____________________ OBJECTS _____________________
        # --------------------- Node ---------------------
        # Define node parent :
        self._cbNode = Node(name='Colorbar', parent=parent)
        # Rescale between (-1., 1.) :
        rsc = vist.STTransform(scale=(width, 2/self._n, 1),
                               translate=(0, -1., 0))
        # Set transformation to the node :
        self._cbNode.transform = rsc

        # --------------------- Image ---------------------
        self._mImage = visuals.Image(parent=self._cbNode, name='image')

        # --------------------- Border ---------------------
        pos = np.array([[0., 0., -3.],
                        [1., 0., -3.],
                        [1., 0., -3.],
                        [1., self._n, -3.],
                        [1., self._n, -3.],
                        [0., self._n, -3.],
                        [0., self._n, -3.],
                        [0., 0., -3.]])
        self._mBorder = visuals.Line(parent=self._cbNode, name='Border')
        self._mBorder.set_data(pos=pos, width=2., connect='segments',
                               color=txtcolor)

        # --------------------- Labels ---------------------
        # Clim labels :
        self._mClimM = visuals.Text(pos=(self._xsh, self._n, -2.),
                                    parent=self._cbNode, color=txtcolor,
                                    font_size=txtsz, name='Clim_M',
                                    anchor_x='left')
        self._mClimm = visuals.Text(pos=(self._xsh, 0, -2.), name='Clim_m',
                                    color=txtcolor, font_size=txtsz,
                                    parent=self._cbNode, anchor_x='left')

        # Cblabel :
        self._mcblabel = visuals.Text(parent=self._cbNode, color=txtcolor,
                                      font_size=cbtxtsz, name='clim_M',
                                      anchor_x='center')
        self._mcblabel.rotation = -90

        # Vmin/Vmax :
        self._vmMNode = Node(name='VminVmax', parent=self._cbNode)
        self._mVm = visuals.Text(parent=self._vmMNode, color=txtcolor,
                                 font_size=self._ratio * txtsz, name='Vmin',
                                 anchor_x='left')
        self._mVM = visuals.Text(parent=self._vmMNode, color=txtcolor,
                                 font_size=self._ratio * txtsz, name='Vmax',
                                 anchor_x='left')

        self._build()

    def _check(self):
        """Check variables."""
        try:
            # Check if clim is int/float :
            if self._clim is None:
                self._clim = self._minmax
            assert all([isinstance(k, (int, float)) for k in self._clim])
            # Check vmin/vmax :
            assert (self._vmin is None) or isinstance(self._vmin, (int, float))
            assert (self._vmax is None) or isinstance(self._vmax, (int, float))
            return True
        except:
            return False

    def _setter(self):
        clim = np.array(self._clim)
        self._mImage.set_data(self._colormap)
        # Clim :
        self._mClimm.text = str(self._digits(clim[0]))
        self._mClimM.text = str(self._digits(clim[1]))
        # Vmin/Vmax :
        if (self._vmin is not None) and (clim[0] < self._vmin < clim[1]):
            self._mVm.visible = True
            self._mVm.text = str(self._digits(self._vmin))
            self._mVm.pos = (self._xsh, self._conv(self._vmin), 2.)
        else:
            self._mVm.visible = False
        if (self._vmax is not None) and (clim[0] < self._vmax < clim[1]):
            self._mVM.visible = True
            self._mVM.text = str(self._digits(self._vmax))
            self._mVM.pos = (self._xsh, self._conv(self._vmax), 2.)
        else:
            self._mVM.visible = False
        # Label :
        if self._cblabel is not None:
            self._mcblabel.text = self._cblabel
            self._mcblabel.pos = (1.9 * self._xsh, self._n / 2., 2.)
        # Clim/Vmin/Vmax font size :
        if isinstance(self._txtsz, (int, float)):
            self._mClimm.font_size = self._txtsz
            self._mClimM.font_size = self._txtsz
            self._mVm.font_size = self._ratio * self._txtsz
            self._mVM.font_size = self._ratio * self._txtsz
        # Cblabel txt size :
        if isinstance(self._cbtxtsz, (int, float)):
            self._mcblabel.font_size = self._cbtxtsz

    def _build(self, needupdate=True):
        """Build the colormap."""
        if self._check() and needupdate:
            # Generate a sample vector between clim :
            sample = np.linspace(self._clim[0], self._clim[1], self._n,
                                 endpoint=True)
            # Get the associated colormap :
            cp = array2colormap(sample, cmap=self._cmap, vmin=self._vmin,
                                vmax=self._vmax, under=self._under,
                                over=self._over)
            self._colormap = cp[:, np.newaxis, :]
            self._setter()
            self._update()

    def _update(self):
        """Update VisPy objects."""
        self._mImage.update()
        self._mcblabel.update()
        self._mClimm.update()
        self._mClimM.update()
        self._mVm.update()
        self._mVM.update()
        self._mBorder.update()

    def _conv(self, value):
        clim = self._clim
        return self._n * (value - clim[0]) / (clim[1] - clim[0])

    def _digits(self, value):
        if isinstance(self._ndigits, int):
            txt = np.round(value * 10**self._ndigits) / 10**self._ndigits
        else:
            txt = value
        return txt

    def set_data(self, data, clim=None, vmin=None, vmax=None, under=None,
                 over=None):
        self._clim = clim
        self.minmax = (data.min(), data.max())

    # ----------- CLIM -----------
    @property
    def clim(self):
        """Get the clim value."""
        return self._clim

    @clim.setter
    def clim(self, value):
        """Set clim value."""
        bck = self._clim
        self._clim = value
        self._build(bck is not value)

    # ----------- VMIN -----------
    @property
    def vmin(self):
        """Get the vmin value."""
        return self._vmin

    @vmin.setter
    def vmin(self, value):
        """Set vmin value."""
        bck = self._vmin
        self._vmin = value
        self._build(bck is not value)

    # ----------- UNDER -----------
    @property
    def under(self):
        """Get the under value."""
        return self._under

    @under.setter
    def under(self, value):
        """Set under value."""
        bck = self._under
        self._under = value
        self._build(bck is not value)

    # ----------- VMAX -----------
    @property
    def vmax(self):
        """Get the vmax value."""
        return self._vmax

    @vmax.setter
    def vmax(self, value):
        """Set vmax value."""
        bck = self._vmax
        self._vmax = value
        self._build(bck is not value)

    # ----------- OVER -----------
    @property
    def over(self):
        """Get the over value."""
        return self._over

    @over.setter
    def over(self, value):
        """Set over value."""
        bck = self._over
        self._over = value
        self._build(bck is not value)

    # ----------- CBLABEL -----------
    @property
    def cblabel(self):
        """Get the cblabel value."""
        return self._cblabel

    @cblabel.setter
    def cblabel(self, value):
        """Set cblabel value."""
        bck = self._cblabel
        self._cblabel = value
        self._build(bck is not value)

    # ----------- TXTSZ -----------
    @property
    def txtsz(self):
        """Get the txtsz value."""
        return self._txtsz
    
    @txtsz.setter
    def txtsz(self, value):
        """Set txtsz value."""
        bck = self._txtsz
        self._txtsz = value
        self._build(bck is not value)

    # ----------- CBTXTSZ -----------
    @property
    def cbtxtsz(self):
        """Get the cbtxtsz value."""
        return self._cbtxtsz
    
    @cbtxtsz.setter
    def cbtxtsz(self, value):
        """Set cbtxtsz value."""
        bck = self._cbtxtsz
        self._cbtxtsz = value
        self._build(bck is not value)
    










###########################################################################
###########################################################################
###########################################################################
###########################################################################
import vispy
canvas = vispy.scene.SceneCanvas(keys='interactive', show=True, resizable=True)
useaxis = False

if useaxis:
    from vispy import scene
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
else:
    wc = canvas.central_widget.add_view()


class vbShortcuts(object):

    def __init__(self, canvas):
        # Add shortcuts to vbCanvas :
        @canvas.events.key_press.connect
        def on_key_press(event):
            if event.text == '-':
                cb.vmin -= .1
                cb.vmax = cb.vmax
                cb.txtsz -= 1. 
                # cb.under = 'slateblue'
                # cb.over = '#ab4642'
            elif event.text == '+':
                cb.vmin += .1
                cb.vmax += .1
                cb.over = (.1, .1, .1, 1.)
                cb.under = (.5, .5, .5, 1.)
                cb.cbtxtsz += 1.
                # cb.cblabel += ' ok'

vbShortcuts(canvas)
###########################################################################
###########################################################################
###########################################################################
###########################################################################


cb = CbarVisual(parent=wc.scene, cblabel='Ceci est mon titre', clim=(0, 170),
                vmin=30., vmax=160, ndigits=2, cmap='Spectral_r')
camera = viscam.PanZoomCamera(rect=(-1, -1, 2, 2))
wc.camera = camera
if useaxis:
    xaxis.link_view(wc)
    yaxis.link_view(wc)

if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()