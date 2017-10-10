
from vispy import scene
from vispy.scene import visuals
import vispy.visuals.transforms as vist

from visbrain.objects.visbrain_obj import VisbrainObject
from visbrain.utils import tal2mni, color2vb, normalize


class SourceObj(VisbrainObject):
    """Create a source object.

    Parameters
    ----------
    name : string
        Name of the source object.
    xyz : array_like
        Array of positions of shape (n_sources, 2) or (n_sources, 3).
    data : array_like | None
        Array of weights of shape (n_sources,).
    """

    def __init__(self, name, xyz, data=None, color='black', alpha=1.,
                 symbol='disc', radiusmin=5., radiusmax=10., edge_width=0.,
                 edge_color='black', system='mni', mask=None, maskcolor='red',
                 text=None, text_size=3., text_color='black', text_bold=False,
                 text_shift=(0., 2., 0.), _z=-10.):
        """Init."""
        self._node = scene.Node(name='SourceObj')
        # _______________________ CHECKING _______________________
        # Init Visbrain object base class :
        VisbrainObject.__init__(self)
        # Name :
        assert isinstance(name, str)
        self._name = name
        # XYZ :
        sh = xyz.shape
        assert sh[1] in [2, 3]
        self._n_sources = sh[0]
        pos = xyz if sh[1] == 3 else np.c_[xyz, np.full((len(self),), _z)]
        # Radius min and max :
        assert all([isinstance(k, (int, float)) for k in (
            radiusmin, radiusmax)])
        assert radiusmax >= radiusmin
        self._radiusmin, self._radiusmax = radiusmin, radiusmax
        # Data :
        if data is None:
            data = np.ones((len(self),))
        else:
            data = np.asarray(data).ravel()
            assert len(data) == len(self)
        self._data = data
        # System :
        pos = pos if system == 'mni' else tal2mni(pos)
        self._xyz = pos
        # Color :
        self._color, self._alpha = color, alpha
        # Mask :
        if mask is None:
            mask = [False] * len(self)
        self._mask = np.asarray(mask).ravel().astype(bool)
        assert len(self._mask) == len(self)
        self._maskcolor = color2vb(maskcolor)

        # _______________________ MARKERS _______________________
        self._sources = visuals.Markers(pos=pos, name=name,
                                        edge_color=edge_color,
                                        edge_width=edge_width,
                                        parent=self._node)
        # Radius / color :
        self._update_radius()
        self._update_color()

        # _______________________ TEXT _______________________
        tvisible = text is None
        self._text = [''] * len(self) if tvisible else text
        assert len(self._text) == len(self)
        self._sources_text = visuals.Text(self._text, pos=pos, bold=text_bold,
                                          color=color2vb(text_color),
                                          font_size=text_size,
                                          parent=self._node)
        self._sources_text.visible = not tvisible
        self._sources_text.transform = vist.STTransform(translate=text_shift)

    def __len__(self):
        """Get the number of sources."""
        return self._n_sources

    def update(self):
        """Update the source object."""
        self._sources.update()

    def _update_radius(self):
        """Update marker's radius."""
        if np.unique(self._data).size == 1:
            radius = self._radiusmin * np.ones((len(self,)))
        else:
            radius = normalize(self._data, tomin=self._radiusmin,
                               tomax=self._radiusmax)
        self._sources._data['a_size'] = radius
        self._sources.update()

    def _update_color(self):
        """Update marker's color."""
        # Get marker's background color :
        if isinstance(self._color, str):   # color='white'
            bg_color = color2vb(self._color, length=len(self))
        elif isinstance(self._color, list):  # color=['white', 'green']
            assert len(self._color) == len(self)
            bg_color = np.squeeze(np.array([color2vb(k) for k in self._color]))
        elif isinstance(self._color, np.ndarray):  # color = [[0, 0, 0], ...]
            csh = self._color.shape
            assert (csh[0] == len(self)) and (csh[1] >= 3)
            if self._color.shape[1] == 3:  # RGB
                self._color = np.c_[self._color, np.full(len(self),
                                                         self._alpha)]
            bg_color = self._color.copy()
        # Update masked marker's color :
        bg_color[self._mask, :] = self._maskcolor
        self._sources._data['a_bg_color'] = bg_color

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._xyz.mean(0)
        dist = np.sqrt(np.sum(d_mean ** 2))
        return scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)

    ###########################################################################
    #                                PROPERTIES
    ###########################################################################
    # ----------- RADIUSMIN -----------
    @property
    def radiusmin(self):
        """Get the radiusmin value."""
        return self._radiusmin

    @radiusmin.setter
    def radiusmin(self, value):
        """Set radiusmin value."""
        assert isinstance(value, (int, float))
        self._radiusmin = value
        self._update_radius()

    # ----------- RADIUSMAX -----------
    @property
    def radiusmax(self):
        """Get the radiusmax value."""
        return self._radiusmax

    @radiusmax.setter
    def radiusmax(self, value):
        """Set radiusmax value."""
        assert isinstance(value, (int, float))
        self._radiusmax = value
        self._update_radius()

    # ----------- SYMBOL -----------
    @property
    def symbol(self):
        """Get the symbol value."""
        return self._sources.symbol

    @symbol.setter
    def symbol(self, value):
        """Set symbol value."""
        self._sources.symbol = value
        self._sources.update()

    # ----------- EDGE_WIDTH -----------
    @property
    def edge_width(self):
        """Get the edge_width value."""
        return self._edge_width

    @edge_width.setter
    def edge_width(self, value):
        """Set edge_width value."""
        assert isinstance(value, (int, float))
        self._edge_width = value
        self._sources._data['a_edgewidth'] = value
        self._sources.update()

    # ----------- EDGE_COLOR -----------
    @property
    def edge_color(self):
        """Get the edge_color value."""
        return self._edge_color

    @edge_color.setter
    def edge_color(self, value):
        """Set edge_color value."""
        color = color2vb(value)
        self._sources._data['a_fg_color'] = color
        self._edge_color = color
        self._sources.update()

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Set alpha value."""
        assert isinstance(value, (int, float))
        assert 0 <= value <= 1
        self._alpha = value
        self._sources._data['a_fg_color'][:, -1] = value
        self._sources._data['a_bg_color'][:, -1] = value
        self._sources.update()

    # ----------- COLOR -----------
    @property
    def color(self):
        """Get the color value."""
        return self._color

    @color.setter
    def color(self, value):
        """Set color value."""
        self._color = value
        self._update_color()

    # ----------- MASK -----------
    @property
    def mask(self):
        """Get the mask value."""
        return self._mask

    @mask.setter
    def mask(self, value):
        """Set mask value."""
        assert len(value) == len(self)
        self._mask = value
        self._update_color()

    # ----------- MASKCOLOR -----------
    @property
    def maskcolor(self):
        """Get the maskcolor value."""
        return self._maskcolor

    @maskcolor.setter
    def maskcolor(self, value):
        """Set maskcolor value."""
        self._maskcolor = color2vb(value)
        self._update_color()









import numpy as np
pos = 100*np.random.rand(100, 3) + 100
pos = np.sort(pos, axis=0)
color = np.random.rand(100, 3)
color = ['orange'] * 50 + ['red'] * 50
data = np.arange(100)
mask = np.logical_and(data >= 20, data <= 30)
text = ['channel' + str(k) for k in range(len(data))]
s = SourceObj('test', pos, data=data, color=color, mask=mask, text=text,
              text_size=15, text_bold=True)
s.edge_width = 1
s.edge_color = 'orange'
s.symbol = 'x'
s.radiusmax = 30.
s.radiusmin = 10.
s.alpha = 1.
s.maskcolor = 'blue'
s.mask = np.logical_and(data >= 60, data <= 90)
s.preview(axis=False)
