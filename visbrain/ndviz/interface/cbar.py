"""Main class for colorbar managment."""

import numpy as np

from matplotlib import cm

from vispy.scene.visuals import ColorBar, Text
from vispy.scene import Node
from vispy.color import Colormap

from ...utils import array2colormap, color2vb, textline2color

__all__ = ['Cbar']


class Cbar(object):
    """docstring for Cbar."""

    def __init__(self, parent, cmap='viridis', clim=None, vmin=None, vmax=None,
                 under=None, over=None, label='', fontsize=15,
                 fontcolor='white'):
        """Init."""
        # ------------------------------------------
        # Get inputs :
        self._obj = {}
        self._l = 10
        self._fontcolor = fontcolor
        self._fontsize = fontsize
        self._cbNode = Node(name='colorbar')

        # ------------------------------------------
        # Add a default colorbar object :
        self._cname = ''
        self.add_object('default', cmap='viridis',
                        label='Default colorbar')
        self.set_default('default', update=False)

        # ------------------------------------------
        # Create the default colorbar and add it parent :
        self.cbcreate()
        self._cbNode.parent = parent
        self.update()

    def __getitem__(self, name):
        """Get the item value, specified using the key parameter."""
        return self.current[name]

    def __str__(self):
        """Return the current object in a string."""
        return self._cname + ': ' + str(self.current)

    def __setitem__(self, name, value):
        """Set the value specified in name to the current colorbar object."""
        self.maincb[name] = value

    # ==================================================================
    # COLORBAR
    # ==================================================================
    def cbcreate(self):
        """Create a default colorbar between 0 and 1."""
        # Define colors :
        cmap = self.cbcolor(length=self._l)

        # -------------------------------------------------
        # COLORBAR OBJECT
        # -------------------------------------------------
        self.cbW = ColorBar(cmap=cmap, orientation='right', size=(40, 5),
                            label='', clim=('', ''), border_color="w",
                            padding=-10, margin=-10, border_width=1)
        self.cbW.parent = self._cbNode

        # -------------------------------------------------
        # COLORBAR TEXT
        # -------------------------------------------------
        # Colorbar maximum :
        self.cbmaxW = Text(text='', color=self._fontcolor,
                           font_size=self._fontsize-2, pos=(4.5, 20),
                           anchor_x='left', anchor_y='center')
        self.cbmaxW.parent = self._cbNode

        # Colorbar minimum :
        self.cbminW = Text(text='', color=self._fontcolor,
                           font_size=self._fontsize-2, pos=(4.5, -20-0.5),
                           anchor_x='left', anchor_y='center')
        self.cbminW.parent = self._cbNode

        # Colorbar label :
        self.cblabelW = Text(text='', color=self._fontcolor,
                             font_size=self._fontsize, pos=(6, 0),
                             rotation=-90, anchor_y='center',
                             anchor_x='center')
        self.cblabelW.parent = self._cbNode

    def cbcolor(self, data=None, length=10):
        """Set the color of the colorbar.

        Kargs:
            data: ndarray, optional, (def: None)
                Array of data. This array is used to automatically set the
                minimum and maximum of the colorbar.

            length: int, optional, (def: 10)
                Length of the colorbar lines.

        Return:
            cmap: vispy colormap
                The vispy colormap to use to create the colorbar.
        """
        # Define a vector of linearly spaced values :
        if data is None:
            colval = np.linspace(self['clim'][0], self['clim'][1], num=length)
        else:
            colval = np.linspace(np.min(data), np.max(data))
        # Turn the colval vector into a RGB array of colors. The clim parameter
        # is not usefull here :
        colorbar = array2colormap(colval, vmin=self['vmin'], vmax=self['vmax'],
                                  under=self['under'], over=self['over'],
                                  cmap=self['cmap'], clim=None)
        # Use the Colormap function of vispy to create a colormap :
        cmap = Colormap(np.flipud(colorbar))

        return cmap

    # ==================================================================
    # OBJECT CONTROL
    # ==================================================================
    def add_object(self, name, cmap='viridis', clim=(0., 1.), vmin=None,
                   vmax=None, under='gray', over='red', label='',
                   minmax=(0., 0.), fcn=None):
        """Add a colorbar object."""
        # Create a dictionnary with all arguments :
        obj = {'cmap': cmap, 'clim': clim, 'vmin': vmin, 'vmax': vmax,
               'under': under, 'over': over, 'label': label, 'minmax': minmax,
               'fcn':fcn}
        # Add the object to the list of surrent objects :
        self._obj[name] = obj

    def set_default(self, name, update=True):
        """Define the colorbar object in name as the default."""
        if self._cname != name:
            self.current = name
            if update:
                self.update()

    def update(self):
        """Update the name object from the main colorbar.

        This function do the opposite to the set_default method.
        """
        # Update the name dict :
        self.current = self._cname
        # Update cbar elemtens :
        if self['cmap'] is not None:
            self.cbW.cmap = self.cbcolor()
        if self['clim'] is not None:
            self.cbminW.text = str(self['clim'][0])
            self.cbmaxW.text = str(self['clim'][1])
        if self['label'] is not None:
            self.cblabelW.text = self['label']
        if self['fcn'] is not None:
            self['fcn']()

    def objects_defined(self):
        """Get the list of names of the currently defined objects."""
        defined = list(self._obj.keys())
        defined.pop(defined.index('default'))
        defined.sort()

        return defined

    def cb_kwargs(self, name):
        """Return a compatible dictionnary."""
        kwargs = {k: self._obj[name][k] for k in ['cmap', 'clim', 'vmin',
                                                  'vmax', 'under', 'over']}
        return kwargs


    # ==================================================================
    # PROPERTIES
    # ==================================================================
    # ----------- CURRENT ----------
    @property
    def current(self):
        """Get the current colorbar object."""
        return self._obj[self._cname]

    @current.setter
    def current(self, name):
        """Set current value."""
        self.maincb = self._obj[name]
        self._cname = name

    # ----------- CLIM -----------
    @property
    def clim(self):
        """Get the colormap."""
        return self['clim']

    @clim.setter
    def clim(self, value):
        """Set clim value."""
        # Check clim :
        if not isinstance(value, (list, tuple)):
            raise ValueError("clim must be a tuple or a list.")
        else:
            value = [float(k) for k in value]
        # Update clim :
        self.maincb['clim'] = value

    # ----------- CMAP -----------
    @property
    def cmap(self):
        """Get the colormap."""
        return self['cmap']

    @cmap.setter
    def cmap(self, value):
        """Set cmap value."""
        # Check cmap :
        if not isinstance(value, str):
            raise ValueError("cmap must be a string of a matplolib colormap.")
        # Set cmap :
        self.maincb['cmap'] = value

    # ----------- VMIN -----------
    @property
    def vmin(self):
        """Get the colormap."""
        return self['vmin']

    @vmin.setter
    def vmin(self, value):
        """Set vmin value."""
        if not isinstance(value, (float, int)):
            raise ValueError("vmin must either be a integer or a float.")
        else:
            value = float(value)
        # Set vmin :
        self.maincb['vmin'] = value

    # ----------- UNDER -----------
    @property
    def under(self):
        """Get the colormap."""
        return self['under']

    @under.setter
    def under(self, value):
        """Set under value."""
        self.maincb['under'] = np.ndarray.tolist(textline2color(value)[1])[0][:-1]

    # ----------- VMAX -----------
    @property
    def vmax(self):
        """Get the colormap."""
        return self['vmax']

    @vmax.setter
    def vmax(self, value):
        """Set vmax value."""
        if not isinstance(value, (float, int)):
            raise ValueError("vmax must either be a integer or a float.")
        else:
            value = float(value)
        # Set vmax :
        self.maincb['vmax'] = value

    # ----------- OVER -----------
    @property
    def over(self):
        """Get the colormap."""
        return self['over']

    @over.setter
    def over(self, value):
        """Set over value."""
        self.maincb['over'] = np.ndarray.tolist(textline2color(value)[1])[0][:-1]

    # ----------- LABEL -----------
    @property
    def label(self):
        """Get the colormap."""
        return self['label']

    @label.setter
    def label(self, value):
        """Set label value."""
        # Check label :
        if not isinstance(value, str):
            raise ValueError("label must be a string of a matplolib colormap.")
        # Set label :
        self.maincb['label'] = value
