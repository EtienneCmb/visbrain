"""Main topoplot class."""
import numpy as np
from scipy.interpolate import interp2d

from warnings import warn
import os
import sys

from vispy.scene import visuals
from vispy.scene import Node
import vispy.visuals.transforms as vist

from .projection import array_project_radial_to3d
from .. import array2colormap, color2vb, normalize#, vpnormalize
from visbrain.utils.transform import vpnormalize


class TopoPlot(object):
    """Create a topoplot.

    Kargs:
        pixels: int, optional, (def: 32)
            The pixels density. Must be even number.

        bgcolor: tuple/array/string, optional, (def: 'black')
            The background color.

        linecolor: tuple/array/string, optional, (def: 'white')
            The topoplot line color for the head / ear / nose.

        width: float, optional, (def: 4.)
            Line width of the head / ear / nose.

        textcolor: tuple/array/string, optional, (def: 'black')
            The textcolor of channel names.

        interp: float, optional, (def: .1)
            The image interpolation ratio.

        scale: float, optional, (def: 800.)
            The plot length (fix OpenGL bugs for small plots).

        parent: vispy, optional, (def: None)
            The parent of the topoplot.
    """

    def __init__(self, xyz=None, system='cart', unit='rad', axtheta=0, axphi=1,
                 chans=None, pixels=32, bgcolor='white', levels=None,
                 linecolor='black', width=4, textcolor='black', interp=.1,
                 scale=800., parent=None, camera=None):
        """Init."""
        # ================== VARIABLES ==================
        self.width = width
        self.system = system
        self.linecolor = color2vb(linecolor)
        self.textcolor = color2vb(textcolor)
        self.bgcolor = color2vb(bgcolor)
        self.interp = interp
        self.pixels = pixels
        self.scale = scale
        self.onload = True
        self.xyz = None
        self.clim, self.cmap = (None, None), 'viridis'
        self.vmin, self.under, self.vmax, self.over = None, None, None, None
        self._params = {}
        self.levels = levels
        self.camera = camera
        # Vispy parents : :
        self.node = Node(name='Topoplot', parent=parent)
        self.headset = Node(name='Headset', parent=self.node)

        # ================== OBJECT ==================
        pos = np.zeros((2, 3), dtype=np.float32)
        self.mesh = visuals.Image(pos=pos, parent=self.headset, name='cmap')
        self.head = visuals.Line(pos=pos, parent=self.headset, name='Head')
        self.nose = visuals.Line(pos=pos, parent=self.headset, name='Nose')
        self.earL = visuals.Line(pos=pos, parent=self.headset, name='EarL')
        self.earR = visuals.Line(pos=pos, parent=self.headset, name='EarR')
        self.chan = visuals.Markers(pos=pos, parent=self.node, name='chan')
        self.chan.transform = vist.STTransform(translate=(0., 0., -10.))

        # ================== HEADSET ==================
        csize = int(pixels/interp) if interp else pixels
        l = csize / 2
        # ------------- Head line -------------
        theta = np.arange(0, 2*np.pi, 0.001)
        head = np.full((len(theta), 3), -1., dtype=np.float32)
        head[:, 0] = l*(1. + np.cos(theta))
        head[:, 1] = l*(1. + np.sin(theta))
        self._head = head
        self.head.set_data(pos=head, color=self.linecolor,
                           width=self.width)

        # ------------- Nose -------------
        w, h = csize * 50. / 512., csize * 30. / 512.
        nose = np.array([[l-w, 2*l-w, 2.],
                         [l, 2*l+h, 2.],
                         [l, 2*l+h, 2.],
                         [l+w, 2*l-w, 2.]
                         ])
        self.nose.set_data(pos=nose, width=self.width, connect='segments',
                           color=self.linecolor)

        # ------------- Ear -------------
        w, h = csize * 10. / 512., csize * 30. / 512.
        yh = l + h * np.sin(theta)
        # Ear left :
        earL = np.full((len(theta), 3), 3., dtype=np.float32)
        earL[:, 0] = 2*l + w * np.cos(theta)
        earL[:, 1] = yh
        self.earL.set_data(pos=earL, color=self.linecolor,
                           width=self.width)
        # Ear right :
        earR = np.full((len(theta), 3), 3., dtype=np.float32)
        earR[:, 0] = 0. + w * np.cos(theta)
        earR[:, 1] = yh
        self.earR.set_data(pos=earR, color=self.linecolor,
                           width=self.width)

        # =================== TRANSFORMATIONS ===================
        self.node.transform = vist.STTransform(scale=[self.scale] * 3)

        # ================== XYZ / CHANNELS ==================
        # ----------- Checking -----------
        # Coordinates given as a input :
        if (xyz is not None) and isinstance(xyz, np.ndarray):
            if xyz.shape[1] not in [2, 3]:
                raise ValueError("Shape of xyz must be (nchan, 2) or "
                                 "(nchan, 3)")
            nchan = xyz.shape[0]
            if xyz.shape[1] == 2:
                xyz = np.c_[xyz, np.zeros((nchan), dtype=np.float)]
            xyz[:, 2] = 1.
            keeponly = np.ones((xyz.shape[0],), dtype=bool)

        # No coordinates -> search in the npz file :
        elif (xyz is None) and (chans is not None):
            if all([isinstance(k, str) for k in chans]):
                xyz, keeponly = self._load_chan(chans)
                self.system = 'spheric'
        self.keeponly = keeponly

        if any(self.keeponly):
            if not all(keeponly):
                ignore = list(np.array(chans)[np.invert(keeponly)])
                warn("Channels " + str(ignore) + " have been "
                     "ignored")

            # ----------- Selection -----------
            xyz = xyz[keeponly, :]
            chans = list(np.array(chans)[keeponly])

            # ----------- Conversion -----------
            if isinstance(xyz, np.ndarray):
                if self.system == 'cart':
                    pass
                elif self.system == 'spheric':
                    xyz = self._sphere2cart(xyz, unit='degree')
                    xyz = array_project_radial_to3d(xyz)
            self.xyz = xyz

            # ------------- Channel names -------------
            if chans is not None:
                self.name = visuals.Text(pos=self.xyz, text=chans,
                                         parent=self.node,
                                         color=self.textcolor)

            # ------------- Prepare data -------------
            self._prepare_data()

        # =================== CAMERA ===================
        marge = 0.
        factor = self.scale
        self.camera.rect = (-factor-marge, -factor-marge,
                            2*(factor+marge), 2*(factor+h+marge))
        self.camera.aspect = 1.

    def __len__(self):
        """Return the number of channels."""
        return self.xyz.shape[0]

    def __getitem__(self, key):
        """Get the parameter."""
        return self._params[key]

    def __setitem__(self, key, value):
        """Set parameter."""
        self._params[key] = value

    ###########################################################################
    # STATIC METHODS
    ###########################################################################

    @staticmethod
    def _load_chan(chan):
        """From the name of the channels, find xyz coordinates.

        Args:
            chan: list
                List of channel names.
        """
        # Load the coordinates template :
        path = sys.modules[__name__].__file__.split('topoviz')[0]
        file = np.load(os.path.join(path, 'eegref.npz'))
        nameRef, xyzRef = file['chan'], file['xyz']
        keeponly = np.ones((len(chan)), dtype=bool)
        # nameRef = list(nameRef)
        # Find and load xyz coordinates :
        xyz = np.zeros((len(chan), 3), dtype=np.float32)
        for num, k in enumerate(chan):
            # Find if the channel is present :
            idx = np.where(nameRef == k)[0]
            if idx.size:
                xyz[num, 0:2] = np.array(xyzRef[idx[0], :])
            else:
                keeponly[num] = False

        return np.array(xyz), keeponly

    @staticmethod
    def _sphere2cart(xyz, axtheta=0, axphi=1, unit='rad'):
        """Convert spheric coordinates to cartesian.

        Args:
            xyz: np.ndarray
                The array of spheric coordinate of shape (N, 3).

        Kargs:
            axtheta: int, optional, (def: 0)
                Specify where is located the theta angle axis (elevation with
                respect to z-axis)

            axphi: int, optional, (def: 1)
                Specify where is located the phi angle axis (counterclockwise
                rotation from +x in x-y plane)

            unit: string, optional, (def: 'rad')
                Specify the unit angles. Use either 'degree' or 'rad'.

        Returns:
            xyz: np.ndarray
                The cartesian coordinates of the angle of shape (N, 3).
        """
        # Get theta / phi :
        theta, phi = xyz[:, 0], xyz[:, 1]
        if unit is 'degree':
            np.deg2rad(theta, out=theta)
            np.deg2rad(phi, out=phi)
        # Get radius :
        r = np.sin(theta)
        # Get cartesian coordinates :
        np.multiply(np.cos(phi), r, out=xyz[:, 0])
        np.multiply(np.sin(phi), r, out=xyz[:, 1])
        np.cos(theta, xyz[:, 2])
        return xyz

    @staticmethod
    def _griddata(x, y, v, xi, yi):
        """Make griddata."""
        xy = x.ravel() + y.ravel() * -1j
        d = xy[None, :] * np.ones((len(xy), 1))
        d = np.abs(d - d.T)
        n = d.shape[0]
        d.flat[::n + 1] = 1.

        g = (d * d) * (np.log(d) - 1.)
        g.flat[::n + 1] = 0.
        weights = np.linalg.solve(g, v.ravel())

        m, n = xi.shape
        zi = np.zeros_like(xi)
        xy = xy.T

        g = np.empty(xy.shape)
        for i in range(m):
            for j in range(n):
                d = np.abs(xi[i, j] + -1j * yi[i, j] - xy)
                mask = np.where(d == 0)[0]
                if len(mask):
                    d[mask] = 1.
                np.log(d, out=g)
                g -= 1.
                g *= d * d
                if len(mask):
                    g[mask] = 0.
                zi[i, j] = g.dot(weights)
        return zi

    ###########################################################################
    # PLOTTING METHODS
    ###########################################################################

    def _topoMNE(self, data):
        """Get topoplot for spheric data using MNE method.

        Args:
            xyz: np.ndarray
                The array of converted coordinates (cartesian)

            data: np.ndarray
                Vector of data.

        Returns:
            image: np.ndarray
                The topoplot image.
        """
        # =================== GRID ===================
        xyz = self.xyz
        pos_x, pos_y = xyz[:, 0], xyz[:, 1]
        xmin, xmax = pos_x.min(), pos_x.max()
        ymin, ymax = pos_y.min(), pos_y.max()
        xi = np.linspace(xmin, xmax, self.pixels)
        yi = np.linspace(ymin, ymax, self.pixels)
        Xi, Yi = np.meshgrid(xi, yi)

        # =================== TRANSFORMATION ===================
        eucl = np.sqrt(xyz[:, 0]**2 + xyz[:, 1]**2).max()
        self.headset.transform = vpnormalize(self._head, dist=2*eucl)
        self.name.transform = vist.STTransform(translate=(0., .1, 0.))
        if self.onload:
            factor = eucl*self.scale + 70.
            self.camera.rect = (-factor, -factor, 2*factor, 2*factor)
            self.onload = False

        return self._griddata(pos_x, pos_y, data, Xi, Yi)

    ###########################################################################
    # SETTING METHODS
    ###########################################################################
    def _prepare_data(self):
        """Prepare the data before plotting."""
        self._params = {}
        if self.interp is not None:
            # Initialize interpolation function :
            self['x'] = np.arange(0, self.pixels, 1)
            self['y'] = np.arange(0, self.pixels, 1)
            # Define newaxis :
            self['xnew'] = np.arange(0, self.pixels, self.interp)
            self['ynew'] = np.arange(0, self.pixels, self.interp)
            self['csize'] = len(self['xnew'])
        else:
            self['csize'] = self.pixels
        # Variables :
        l = int(self['csize'] / 2)
        self['l'] = l
        y, x = np.ogrid[-l:l, -l:l]
        disc = x**2 + y**2
        self['mask'] = disc < l**2
        self['nmask'] = np.invert(self['mask'])
        # self['image'] = np.tile(self.bgcolor[np.newaxis, ...], (2*l, 2*l, 1))

    def set_data(self, data, chans_color='white'):
        """Set data to the topoplot.

        Kargs:
            system: string, optional, (def: 'cart')
                Coordinates system. Use 'cart' for cartesian system, 'sphere'
                for spheric (with a theta / phi angle).
        """
        data = data[self.keeponly]
        # =================== GET IMAGE ===================
        image = self._topoMNE(data)

        # =================== INTERPOLATION ===================
        if self.interp is not None:
            # Initialize interpolation function :
            f = interp2d(self['x'], self['y'], image, kind='linear')
            image = f(self['xnew'], self['ynew'])

        # ------------- Head map -------------
        # Turn it into a colormap and set it :
        image[self['nmask']] = data.mean()
        image = normalize(image, data.min(), data.max())
        cm = array2colormap(image, cmap=self.cmap, clim=self.clim,
                            vmin=self.vmin, vmax=self.vmax, under=self.under,
                            over=self.over)
        cm[self['nmask']] = self.bgcolor
        self.mesh.set_data(cm)

        # =================== ISOCURVE ===================
        if self.levels is not None:
            # Get levels and color :
            levels = np.linspace(image.min(), image.max(), self.levels)
            color_lev = array2colormap(levels, cmap='Spectral_r')
            # Set image :
            image[self['nmask']] = np.inf
            self.iso = visuals.Isocurve(data=image, parent=self.headset,
                                        levels=levels, color_lev=color_lev,
                                        width=2.)
            self.iso.transform = vist.STTransform(translate=(0., 0., -5.))

        # =================== CHANNELS ===================
        # Markers :
        chanc = color2vb(chans_color)
        radius = normalize(data, 5., 20.)
        self.chan.set_data(pos=self.xyz, size=radius, face_color=chanc,
                           edge_color=self.linecolor)

    def set_cmap(self, clim=(None, None), cmap='viridis', vmin=None, vmax=None,
                 under=None, over=None):
        """Set colorbar properties.

        Kargs:
            clim: float, optional, (def: None)
                Minimum / Maximum of the colorbar.

            cmap: string, optional, (def: 'viridis')
                The colormap to use.
        """
        self.clim, self.cmap = clim, cmap
        self.vmin, self.under, self.vmax, self.over = vmin, under, vmax, over
