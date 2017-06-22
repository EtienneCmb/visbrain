
from .CbarBase import CbarBase

__all__ = ['CbarObjetcs']


class CbarObjetcs(object):
    """Create and manage colorbar objects."""

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

    def select(self, name):
        if name in self._objs.keys():
            self._selected = name
        else:
            raise ValueError(name + " not in the object list.")

    def add_object(self, **kwargs):
        """Add object."""
        self._selected = kwargs['name']
        self._objs[kwargs['name']] = CbarBase(**kwargs)

    def update_from_obj(self, obj, sup='_'):
        for key, val in self:
            if isinstance(val, str):
                exec("obj." + sup + key + "='" + val + "'")
            else:
                exec("obj." + sup + key + "=" + str(val))

    def to_kwargs(self):
        return self._objs[self._selected].to_kwargs()

    def save(self, filename):
        """Save all colorbar configuration."""
        import json
        import os
        file = os.path.splitext(filename)[0] + '.txt'
        with open(file, 'w') as f:
            config = {}
            for k, i in self._objs.items():
                config[k] = i.to_dict()
            json.dump(config, f)

    def load(self, filename):
        """Load configuration file."""
        self._objs = {}
        import json
        with open(filename) as f:
            # Load the configuration file :
            config = json.load(f)

            for k in config.keys():
                self._objs[config[k]['name']] = CbarBase(**config[k])

        self._selected = list(self._objs.keys())[0]

    def list(self):
        return list(self._objs.keys())
