"""Main topoplot class."""
import numpy as np
from scipy.interpolate import interp2d

from warnings import warn
from vispy.scene import visuals
from vispy.scene import Node
import vispy.visuals.transforms as vist

from .projection import array_project_radial_to3d, array_project_radial_to2d
from ...utils import array2colormap, color2vb, normalize, vpnormalize


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
                 chans=None, pixels=32, bgcolor='white', levels=10,
                 linecolor='black', width=4, textcolor='black', interp=.1,
                 scale=800., parent=None):
        """Init."""
        # ================== VARIABLES ==================
        self.width = width
        self.system = system
        self.linecolor = color2vb(linecolor)
        self.textcolor = color2vb(textcolor)
        self.bgcolor = color2vb(bgcolor)
        self.electrodescale = np.asarray(1.)
        self.interprange = np.pi * 3 / 4
        self.interp = interp
        self.pixels = pixels
        self.scale = scale
        self.onload = True
        self.xyz = None
        self.levels = levels
        # Legendre factors :
        m = 4
        num_lterms = 10
        self.legendre_factors = self.calc_legendre_factors(m, num_lterms)
        # Vispy parents : :
        self.node = Node(name='Topoplot', parent=parent)
        self.headset = Node(name='Headset', parent=self.node)

        # ================== CHANNELS ==================
        # ----------- Checking -----------D
        # Check coordinates shape :
        if (xyz is not None) and isinstance(xyz, np.ndarray):
            if xyz.shape[1] not in [2, 3]:
                raise ValueError("Shape of xyz must be (nchan, 2) or "
                                 "(nchan, 3)")
            nchan = xyz.shape[0]
            if xyz.shape[1] == 2:
                xyz = np.c_[xyz, np.zeros((nchan), dtype=np.float)]
            xyz[:, 2] = 1.
        elif (xyz is None) and (chans is not None):
            if all([isinstance(k, str) for k in chans]):
                xyz, abort = self._load_chan(chans)
                xyz = np.c_[xyz, np.zeros((xyz.shape[0]), dtype=np.float)]
                self.system = 'spheric'
            if abort:
                warn("No channels found.")

        # ----------- Conversion -----------D
        if isinstance(xyz, np.ndarray):
            if self.system == 'cart':
                self.xyzp = xyz
            elif self.system == 'spheric':
                xyz = self._sphere2cart(xyz, unit='degree')
                self.xyzp = array_project_radial_to2d(xyz)
        self.xyz = xyz

        # ================== OBJECT ==================
        pos = np.zeros((2, 3), dtype=np.float32)
        self.mesh = visuals.Image(pos=pos, parent=self.headset, name='cmap',
                                  interpolation='gaussian')
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

        # ------------- Channel names -------------
        if chans is not None:
            self.name = visuals.Text(pos=self.xyzp, text=chans,
                                     parent=self.node, color=self.textcolor)

        # =================== TRANSFORMATIONS ===================
        self.node.transform = vist.STTransform(scale=[self.scale] * 3)

        # =================== CAMERA ===================
        marge = 100.
        factor = self.scale * self.interprange
        self.cam = {'rect': (-factor-marge, -factor-marge,
                             2*(factor+marge), 2*(factor+h+marge)),
                    'aspect': 1.}

    def __len__(self):
        """Return the number of channels."""
        return self.xyz.shape[0]

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
        file = np.load('eegref.npz')
        nameRef, xyzRef = file['chan'], file['xyz']
        # nameRef = list(nameRef)
        # Find and load xyz coordinates :
        xyz, abort = [], True
        for k in chan:
            # Find if the channel is present :
            idx = np.where(nameRef == k)[0]
            if idx.size:
                xyz.append(xyzRef[idx, :].ravel())
                abort = False
            else:
                warn("\n"+k+" not found. This channel will be ignore.")
        return np.array(xyz), abort

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
    def calc_legendre_factors(m, num_lterms):
        """Compute legendre factors."""
        return [0] + [(2 * n + 1) / (n ** m * (
                   n + 1) ** m * 4 * np.pi) for n in range(1, num_lterms + 1)]

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

    def calc_g(self, x):
        """Get polynom from legendre factors."""
        return np.polynomial.legendre.legval(x, self.legendre_factors)

    ###########################################################################
    # PLOTTING METHODS
    ###########################################################################

    def _topoScott(self, data):
        """Get topoplot for spheric data using Scott method.

        Args:
            xyz: np.ndarray
                The array of converted coordinates (from spheric to cartesian)

            data: np.ndarray
                Vector of data.

        Returns:
            image: np.ndarray
                The topoplot image.
        """
        xyz, nchan = self.xyz, len(self)
        # Check data shape :
        if data.ndim > 1:
            data = data.ravel()
        if len(data) is not nchan:
            raise ValueError("The length of data must be (nchans,)")

        # =================== LOCATIONS ===================
        g = np.zeros((1 + nchan, 1 + nchan))
        g[:, 0] = np.ones(1 + nchan)
        g[-1, :] = np.ones(1 + nchan)
        g[-1, 0] = 0.
        for i in range(nchan):
            for j in range(nchan):
                g[i, j + 1] = self.calc_g(np.dot(xyz[i], xyz[j]))

        # =================== MESHDATA ===================
        c = np.linalg.solve(g, np.concatenate((data, [0])))
        # Create intepolation grid :
        x = np.linspace(xyz[:, 0].min(), xyz[:, 0].max(), )
        x = np.linspace(-self.interprange, self.interprange, self.pixels)
        y = np.linspace(self.interprange, -self.interprange, self.pixels)
        xy = np.transpose(np.meshgrid(x, y)) / self.electrodescale
        e = array_project_radial_to3d(xy)
        gmap = self.calc_g(e.dot(np.transpose(xyz)))

        # =================== TRANSFORMATION ===================
        self.headset.transform = vpnormalize(self._head,
                                             dist=2.*self.interprange)
        self.name.transform = vist.STTransform(translate=(0., .1, 0.))

        return np.flipud(gmap.dot(c[1:]) + c[0])

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
        self.name.transform = vist.STTransform(translate=(0., .03, 0.))

        return self._griddata(pos_x, pos_y, data, Xi, Yi)

    ###########################################################################
    # SETTING METHODS
    ###########################################################################
    def set_data(self, data, cmap='Spectral_r', clim=None, vmin=None,
                 vmax=None, under=None, over=None, chans_color='white'):
        """Set data to the topoplot.

        Kargs:
            system: string, optional, (def: 'cart')
                Coordinates system. Use 'cart' for cartesian system, 'sphere'
                for spheric (with a theta / phi angle).
        """
        # =================== GET IMAGE ===================
        if self.system == 'cart':
            image = self._topoMNE(data)
        elif self.system == 'spheric':
            image = self._topoScott(data)

        # =================== INTERPOLATION ===================
        if self.interp is not None:
            # Initialize interpolation function :
            x = np.arange(0, image.shape[1], 1)
            y = np.arange(0, image.shape[1], 1)
            xx, yy = np.meshgrid(x, y)
            f = interp2d(x, y, image, kind='cubic')
            # Define newaxis :
            xnew = np.arange(0, image.shape[1], self.interp)
            ynew = np.arange(0, image.shape[1], self.interp)
            image = f(xnew, ynew)
            csize = len(xnew)
        else:
            csize = self.pixels
        # Variables :
        l = csize/2
        y, x = np.ogrid[-l:l, -l:l]
        disc = x**2 + y**2
        mask = disc >= l**2

        # ------------- Head map -------------
        # Turn it into a colormap and set it :
        image[mask] = data.mean()
        cm = array2colormap(image, cmap=cmap, clim=clim, vmin=vmin,
                            vmax=vmax, under=under, over=over)
        cm[mask] = self.bgcolor
        self.mesh.set_data(cm)

        # =================== ISOCURVE ===================
        if self.levels is not None:
            # Get levels and color :
            levels = np.linspace(image.min(), image.max(), self.levels)
            color_lev = array2colormap(levels, cmap='Spectral_r')
            # Set image :
            image[mask] = np.inf
            self.iso = visuals.Isocurve(data=image, parent=self.headset,
                                        levels=levels, color_lev=color_lev,
                                        width=2.)
            self.iso.transform = vist.STTransform(translate=(0., 0., -5.))

        # =================== CHANNELS ===================
        # Markers :
        chanc = color2vb(chans_color)
        radius = normalize(data, 5., 20.)
        self.chan.set_data(pos=self.xyzp, size=radius, face_color=chanc,
                           edge_color=self.linecolor)
