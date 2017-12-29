"""Visual colorbar object using VisPy."""
import numpy as np
from vispy.scene import Node, visuals
from vispy import scene
import vispy.visuals.transforms as vist

from ...utils import array2colormap, color2tuple, FixedCam
from .CbarBase import CbarBase


class CbarVisual(CbarBase):
    """Create a colorbar using Vispy.

    Parameters
    ----------
    cmap : string | None
        Matplotlib colormap (like 'viridis', 'inferno'...).
    clim : tuple/list | None
        Colorbar limit. Every values under / over clim will
        clip.
    isvmin : bool | False
        Activate/deactivate vmin.
    vmin : float | None
        Every values under vmin will have the color defined
        using the under parameter.
    isvmax : bool | False
        Activate/deactivate vmax.
    vmax : float | None
        Every values over vmin will have the color defined
        using the over parameter.
    under : tuple/string | None
        Matplotlib color under vmin.
    over : tuple/string | None
        Matplotlib color over vmax.
    cblabel : string | ''
        Colorbar label.
    cbtxtsz : float | 5..
        Text size of the colorbar label.
    cbtxtsh : float | 2.3
        Shift for the colorbar label.
    txtcolor : string | 'white'
        Text color.
    txtsz : float | 3.
        Text size for clim/vmin/vmax text.
    txtsh : float | 1.2
        Shift for clim/vmin/vmax text.
    border : bool | True
        Display colorbar borders.
    bw : float | 2.
        Border width.
    limtxt : bool | True
        Display vmin/vmax text.
    bgcolor : tuple/string | (0., 0., 0.)
        Background color of the colorbar canvas.
    ndigits : int | 2
        Number of digits for the text.
    parent : VisPy | None
        VisPy parent to use.
    """

    def __init__(self, parent=None, **kwargs):
        """Init."""
        # _____________________ INIT _____________________
        self._n = 1000
        self._ratio = 4 / 5
        CbarBase.__init__(self, **kwargs)

        # _____________________ CANVAS _____________________
        if parent is None:
            # Define a canvas :
            self._canvas = scene.SceneCanvas(keys='interactive', show=False,
                                             resizable=True, dpi=600,
                                             bgcolor=self._bgcolor,
                                             size=(300, 900))
            self._wc = self._canvas.central_widget.add_view()
            parent = self._wc.scene
            # Define the camera :
            self._camera = FixedCam(rect=(-1.2, -1.2, 2.4, 2.4))
            self._wc.camera = self._camera
        self.parent = parent

        # _____________________ OBJECTS _____________________
        # --------------------- Node ---------------------
        # Define node parent and limit node :
        self._cbNode = Node(name='Colorbar', parent=parent)
        self._limNode = Node(name='Limits', parent=self._cbNode)
        # Rescale between (-1., 1.) :
        self._rsc = vist.STTransform(scale=(self._width, 2 / self._n, 1),
                                     translate=(0, -1., 0))
        # Set transformation to the node :
        self._cbNode.transform = self._rsc

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
                               color=self._txtcolor)
        self._mBorder.visible = self._border

        # --------------------- Labels ---------------------
        # Clim labels :
        self._mClimM = visuals.Text(parent=self._limNode, color=self._txtcolor,
                                    font_size=self._txtsz, name='Clim_M',
                                    anchor_x='left')
        self._mClimm = visuals.Text(parent=self._limNode, color=self._txtcolor,
                                    font_size=self._txtsz, name='Clim_m',
                                    anchor_x='left')

        # Cblabel :
        self._mcblabel = visuals.Text(parent=self._limNode, name='Cblabel',
                                      color=self._txtcolor, anchor_x='center',
                                      font_size=self._cbtxtsz)
        self._mcblabel.rotation = -90

        # Vmin/Vmax :
        self._vmMNode = Node(name='VminVmax', parent=self._limNode)
        self._mVm = visuals.Text(parent=self._vmMNode, color=self._txtcolor,
                                 font_size=self._ratio * self._txtsz,
                                 name='Vmin', anchor_x='left')
        self._mVM = visuals.Text(parent=self._vmMNode, color=self._txtcolor,
                                 font_size=self._ratio * self._txtsz,
                                 name='Vmax', anchor_x='left')

        # Build colorbar :
        self._build(True, 'all')

    # -------------------------------------------------------------------------
    #                             DEEP METHODS
    # -------------------------------------------------------------------------
    def _check(self):
        """Check variables."""
        try:
            # Check if clim is int/float :
            if self._clim is None:
                if not hasattr(self, '_minmax'):
                    self._minmax = (0., 1.)
                self._clim = self._minmax
            assert all([isinstance(k, (int, float)) for k in self._clim])
            # Check vmin/vmax :
            assert (self._vmin is None) or isinstance(self._vmin, (int, float))
            assert (self._vmax is None) or isinstance(self._vmax, (int, float))
            return True
        except:
            raise ValueError("Error in checking")

    def _setter(self, toset):
        # _____________________ IMAGE _____________________
        self._mImage.set_data(self._colormap)

        # _____________________ CLIM _____________________
        clim = np.array(self._clim)
        if toset in ['all', 'clim']:
            self._mClimm.text = str(self._digits(clim[0]))
            self._mClimM.text = str(self._digits(clim[1]))

        # _____________________ VMIN/VMAX _____________________
        # ------------ VMIN ------------
        if toset in ['all', 'vmin']:
            isnn = (self._vmin is not None) and self._isvmin
            if isnn and (clim[0] < self._vmin < clim[1]):
                self._mVm.visible = True
                self._mVm.text = str(self._digits(self._vmin))
                self._mVm.pos = (self.txtsh, self._conv(self._vmin), -3.)
            else:
                self._mVm.visible = False
        # ------------ VMAX ------------
        if toset in ['all', 'vmax']:
            isnn = (self._vmax is not None) and self._isvmax
            if isnn and (clim[0] < self._vmax < clim[1]):
                self._mVM.visible = True
                self._mVM.text = str(self._digits(self._vmax))
                self._mVM.pos = (self.txtsh, self._conv(self._vmax), -3.)
            else:
                self._mVM.visible = False

        # _____________________ TEXT _____________________
        # Text color :
        if toset in ['all', 'txtcolor']:
            self._mClimm.color = self._txtcolor
            self._mClimM.color = self._txtcolor
            self._mcblabel.color = self._txtcolor
            self._mVm.color = self._txtcolor
            self._mVM.color = self._txtcolor
            self._mBorder.set_data(color=self._txtcolor)
            self._mcblabel.color = self._txtcolor

        # Label :
        self._cblabel = '' if self._cblabel is None else self._cblabel
        if toset in ['all', 'cblabel']:
            self._mcblabel.text = self._cblabel
        if toset in ['all', 'cbtxtsh']:
            self._mcblabel.pos = (self.cbtxtsh, self._n / 2., -3.)
        if toset in ['all', 'cbtxtsz']:
            self._mcblabel.font_size = self._cbtxtsz
        # Clim/Vmin/Vmax font size and position :
        if toset in ['all', 'txtsz']:
            self._mClimm.font_size = self._txtsz
            self._mClimM.font_size = self._txtsz
            self._mVm.font_size = self._ratio * self._txtsz
            self._mVM.font_size = self._ratio * self._txtsz
        if toset in ['all', 'txtsh']:
            self._mClimM.pos = (self.txtsh, self._n, -3.)
            self._mClimm.pos = (self.txtsh, 0., -3.)
            if self._vmin is not None:
                self._mVm.pos = (self.txtsh, self._conv(self._vmin), 3.)
            if self._vmax is not None:
                self._mVM.pos = (self.txtsh, self._conv(self._vmax), 3.)

    def _build(self, needupdate=True, toset='all'):
        """Build the colormap."""
        if self._check() and needupdate:
            # Generate a sample vector between clim :
            sample = np.linspace(self._clim[0], self._clim[1], self._n,
                                 endpoint=True)
            # Avoid setting vmin/vmax if checkboxes inactives :
            vmin = self._vmin if self._isvmin else None
            vmax = self._vmax if self._isvmax else None
            # Get the associated colormap :
            cp = array2colormap(sample, cmap=self._cmap, vmin=vmin,
                                vmax=vmax, under=self._under, over=self._over)
            self._colormap = cp[:, np.newaxis, :]
        self._setter(toset)
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
        if clim[1] > clim[0]:
            return self._n * (value - clim[0]) / (clim[1] - clim[0])

    def _digits(self, value):
        if isinstance(self._ndigits, int):
            txt = np.round(value * 10**self._ndigits) / 10**self._ndigits
        else:
            txt = value
        return txt

    ###########################################################################
    ###########################################################################
    #                                 SETTINGS
    ###########################################################################
    ###########################################################################
    # ----------- NAME -----------
    @property
    def name(self):
        """Get the name value."""
        return self._name

    @name.setter
    def name(self, value):
        """Set name value."""
        self._name = value

    # ----------- BGCOLOR -----------
    @property
    def bgcolor(self):
        """Get the bgcolor value."""
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, value):
        """Set bgcolor value."""
        self._bgcolor = value
        self._canvas.bgcolor = value
        self._canvas.update()

    # ----------- NDIGITS -----------
    @property
    def ndigits(self):
        """Get the ndigits value."""
        return self._ndigits

    @ndigits.setter
    def ndigits(self, value):
        """Set ndigits value."""
        bck = self._ndigits
        self._ndigits = value
        self._build(bck is not value, 'all')

    # ----------- WIDTH -----------
    @property
    def width(self):
        """Get the width value."""
        return self._width

    @width.setter
    def width(self, value):
        """Set width value."""
        self._width = value
        sc = self._cbNode.transform.scale
        tr = self._cbNode.transform.translate
        self._cbNode.transform.scale = (value, sc[1], sc[2], sc[3])
        self._cbNode.transform.translate = (-value, tr[1], tr[2], tr[3])

    # ----------- BORDER -----------
    @property
    def border(self):
        """Get the border value."""
        return self._border

    @border.setter
    def border(self, value):
        """Set border value."""
        self._border = value
        self._mBorder.visible = value

    # ----------- BW -----------
    @property
    def bw(self):
        """Get the bw value."""
        return self._bw

    @bw.setter
    def bw(self, value):
        """Set bw value."""
        self._bw = value
        self._mBorder.set_data(width=value)

    # ----------- LIMTXT -----------
    @property
    def limtxt(self):
        """Get the limtxt value."""
        return self._limtxt

    @limtxt.setter
    def limtxt(self, value):
        """Set limtxt value."""
        self._limtxt = value
        self._vmMNode.visible = value

    ###########################################################################
    ###########################################################################
    #                       CMAP/VMIN/VMAX/UNDER/OVER
    ###########################################################################
    ###########################################################################
    # ----------- CMAP -----------
    @property
    def cmap(self):
        """Get the cmap value."""
        return self._cmap

    @cmap.setter
    def cmap(self, value):
        """Set cmap value."""
        bck = self._cmap
        self._cmap = value
        self._build(bck is not value)

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
        self._build(bck is not value, 'all')

    # ----------- ISVMIN -----------
    @property
    def isvmin(self):
        """Get the isvmin value."""
        return self._isvmin

    @isvmin.setter
    def isvmin(self, value):
        """Set isvmin value."""
        bck = self._isvmin
        self._isvmin = value
        self._build(bck is not value, 'vmin')

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
        self._build(bck is not value, 'vmin')

    # ----------- UNDER -----------
    @property
    def under(self):
        """Get the under value."""
        return self._under

    @under.setter
    def under(self, value):
        """Set under value."""
        bck = self._under
        self._under = color2tuple(value, float)
        self._build(bck is not value)

    # ----------- ISVMAX -----------
    @property
    def isvmax(self):
        """Get the isvmax value."""
        return self._isvmax

    @isvmax.setter
    def isvmax(self, value):
        """Set isvmax value."""
        bck = self._isvmax
        self._isvmax = value
        self._build(bck is not value, 'vmax')

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
        self._build(bck is not value, 'vmax')

    # ----------- OVER -----------
    @property
    def over(self):
        """Get the over value."""
        return self._over

    @over.setter
    def over(self, value):
        """Set over value."""
        bck = self._over
        self._over = color2tuple(value, float)
        self._build(bck is not value)

    ###########################################################################
    ###########################################################################
    #                                 TEXT
    ###########################################################################
    ###########################################################################
    # ----------- CBLABEL -----------
    @property
    def cblabel(self):
        """Get the cblabel value."""
        return self._cblabel

    @cblabel.setter
    def cblabel(self, value):
        """Set cblabel value."""
        self._cblabel = value
        self._build(False, 'cblabel')

    # ----------- CBTXTSZ -----------
    @property
    def cbtxtsz(self):
        """Get the cbtxtsz value."""
        return self._cbtxtsz

    @cbtxtsz.setter
    def cbtxtsz(self, value):
        """Set cbtxtsz value."""
        self._cbtxtsz = value
        self._build(False, 'cbtxtsz')

    # ----------- CBTXTSH -----------
    @property
    def cbtxtsh(self):
        """Get the cbtxtsh value."""
        return self._cbtxtsh

    @cbtxtsh.setter
    def cbtxtsh(self, value):
        """Set cbtxtsh value."""
        self._cbtxtsh = value
        self._build(False, 'cbtxtsh')

    # ----------- TXTCOLOR -----------
    @property
    def txtcolor(self):
        """Get the txtcolor value."""
        return self._txtcolor

    @txtcolor.setter
    def txtcolor(self, value):
        """Set txtcolor value."""
        self._txtcolor = color2tuple(value, float)
        self._build(False, 'txtcolor')

    # ----------- TXTSZ -----------
    @property
    def txtsz(self):
        """Get the txtsz value."""
        return self._txtsz

    @txtsz.setter
    def txtsz(self, value):
        """Set txtsz value."""
        self._txtsz = value
        self._build(False, 'txtsz')

    # ----------- TXTSH -----------
    @property
    def txtsh(self):
        """Get the txtsh value."""
        return self._txtsh

    @txtsh.setter
    def txtsh(self, value):
        """Set txtsh value."""
        self._txtsh = value
        self._build(False, 'txtsh')
