"""Manage colorbar of multiple objects."""
from .CbarBase import CbarBase
from ...io import save_config_json, load_config_json

__all__ = ['CbarObjetcs']


class CbarObjetcs(object):
    """Create and manage multiple colorbar objects."""

    def __init__(self):
        """Init."""
        self._objs = {}
        self._selected = None

    def __getitem__(self, key):
        """Get item in the curently selected colorbar object."""
        return self._objs[self._selected][key]

    def __setitem__(self, key, value):
        """Set item in the curently selected colorbar object."""
        exec("self._objs[self._selected]._" + key + " = value")

    def __iter__(self):
        """Iterate over the selected colorbar object."""
        for key, val in self._objs[self._selected].to_dict().items():
            yield key, val

    def __bool__(self):
        """Test if it's not empty."""
        return self._objs and self._selected

    def select(self, name):
        """Select an object.

        Parameters
        ----------
        name : string
            Object name.
        """
        if name in self._objs.keys():
            self._selected = name
        else:
            raise ValueError(name + " not in the object list.")

    def add_object(self, name, obj, overwrite=True):
        """Add a colorbar object.

        Parameters
        ----------
        name : string
            Name of the object.
        obj : CbarBase
            The CbarBase object to add.
        overwrite : bool | True
            If a colorbar object already has the same name, define if it
            should be overwritten.
        """
        # Test if name is a string :
        if not isinstance(name, str):
            raise ValueError("name must be a string.")
        # Test if the name is free :
        if not overwrite and (name in self._objs.keys()):
            raise ValueError("The colorbar object '" + name + "' already "
                             "exist. Use an other name")
        if isinstance(obj, CbarBase):
            self._selected = name
            self._objs[name] = obj
        else:
            raise ValueError("The object to add must be a CbarBase type.")

    def to_kwargs(self):
        """Return a dictionary for input arguments."""
        return self._objs[self._selected].to_kwargs()

    def to_dict(self, alldicts=False):
        """Return a dictionary of all colorbar args."""
        if alldicts:
            return {k: i.to_dict() for k, i in self._objs.items()}
        else:
            return self._objs[self._selected].to_dict()

    def keys(self):
        """Return the list of entries in the object dict."""
        return list(self._objs.keys())

    def save(self, filename):
        """Save all colorbar configurations.

        Parameters
        ----------
        filename : string
            Name of the file to be saved.
        """
        # Build the configuration file :
        config = {k: i.to_dict() for k, i in self._objs.items()}
        # Save in a txt file :
        save_config_json(filename, config)

    def load(self, filename, clean=True, select=None):
        """Load a colorbar configuration file.

        Parameters
        ----------
        filename: string
            Name of the file to load.
        clean : bool | True
            Specify if all objects have to be clean before.
        select : string | None
            Name of the object to select on load.
        """
        # Load the configuration :
        config = load_config_json(filename)
        # Clean current objects :
        if clean:
            self._objs = {}
        # Load objects :
        for k, i in config.items():
            self.add_object(k, CbarBase(**i))
        # Select the first one :
        if (select is None) or (select not in self._objs.keys()):
            self._selected = list(self._objs.keys())[0]

    def from_dict(self, dico, clean=True):
        """Define cbar objects from dictionary."""
        # Clean :
        if clean:
            self._objs = {}
        # Load objects :
        for k, i in dico.items():
            self._objs[k] = CbarBase(**i)

    def update(self):
        """Update function when an attribute change."""
        self._objs[self._selected]._fcn()

    def autoscale(self):
        """Execute autoscale function associated to the object."""
        self._objs[self._selected]._minmaxfcn()

    # ----------- NAME -----------
    @property
    def name(self):
        """Get the name value."""
        return self._selected
