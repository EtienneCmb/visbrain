import numpy as np

from .visbrain_obj import VisbrainObject
from ..utils import load_predefined_roi, mni2tal
from ..io import is_pandas_installed


class RoiObj(VisbrainObject):
    """docstring for RoiObj"""

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, vol=None, index=None, label=None, hdr=None,
                 system='mni', parent=None):
        """Init."""
        # Test if pandas is installed :
        if not is_pandas_installed():
            raise ImportError("In order to work properly, pandas package "
                              "should be installed using *pip install pandas*")
        import pandas as pd
        # Init Visbrain object base class :
        VisbrainObject.__init__(self, name, parent)
        # _______________________ PREDEFINED _______________________
        if name in ['brodmann', 'talairach', 'aal']:
            vol, label, index, hdr, system = load_predefined_roi(name)
        self._offset = -1 if name == 'talairach' else 0

        # _______________________ CHECKING _______________________
        # vol :
        assert vol.ndim == 3
        # Index and label :
        assert len(index) == len(label)
        index = np.asarray(index).astype(int)
        label = np.asarray(label)
        self.vol = vol
        self._n_roi = len(index)
        # hdr :
        self.hdr = np.eye(4) if hdr is None else hdr
        assert self.hdr.shape == (4, 4)
        # System :
        assert system in ['mni', 'tal']
        self.system = system

        # _______________________ REFERENCE _______________________
        label_dict = self._unpack_struct_array(label)
        columns = ['index'] + list(label_dict.keys())
        self.ref = pd.DataFrame({'index': index, **label_dict},
                                columns=columns)
        self.analysis = pd.DataFrame({}, columns=columns)

    def __len__(self):
        """Return the number of ROI."""
        return self._n_roi

    def __getitem__(self, index):
        """Get the ref item at index."""
        if isinstance(index, (int, list, np.ndarray, slice)):
            return self.ref.iloc[index]

    def __ge__(self, idx):
        """Test if x >= idx."""
        assert len(idx) == 3
        sh = self.vol.shape
        return (sh[0] >= idx[0]) and (sh[1] >= idx[1]) and (sh[2] >= idx[2])

    def __gt__(self, idx):
        """Test if x > idx."""
        assert len(idx) == 3
        sh = self.vol.shape
        return (sh[0] > idx[0]) and (sh[1] > idx[1]) and (sh[2] > idx[2])

    def __le__(self, idx):
        """Test if x <= idx."""
        assert len(idx) == 3
        sh = self.vol.shape
        return (sh[0] <= idx[0]) and (sh[1] <= idx[1]) and (sh[2] <= idx[2])

    def __lt__(self, idx):
        """Test if x < idx."""
        assert len(idx) == 3
        sh = self.vol.shape
        return (sh[0] < idx[0]) and (sh[1] < idx[1]) and (sh[2] < idx[2])

    def localize_sources(self, xyz, source_name=None, replace_bad=True,
                         bad_patterns=[-1, 'undefined', 'None'],
                         replace_with='Not found'):
        """Localize source's using this ROI object.

        Parameters
        ----------
        xyz : array_like
            Array of source's coordinates of shape (n_sources, 3)
        source_name : array_like/list | None
            List of source's names.
        replace_bad : bool | True
            Replace bad values (True) or not (False).
        bad_patterns : list | [None, -1, 'undefined', 'None']
            Bad patterns to replace if replace_bad is True.
        replace_with : string | 'Not found'
            Replace bad patterns with this string.
        """
        # Check xyz :
        assert (xyz.ndim == 2) and (xyz.shape[1] == 3)
        n_sources = xyz.shape[0]
        if self.system == 'tal':
            xyz = mni2tal(xyz)
        # Check source_name :
        if source_name is None:
            source_name = ['s' + str(k) for k in range(n_sources)]
        assert len(source_name) == n_sources
        # Loop over sources :
        xyz = np.c_[xyz, np.ones((n_sources,), dtype=xyz.dtype)].T
        for k in range(n_sources):
            # Apply HDR transformation :
            pos = np.linalg.lstsq(self.hdr, xyz[:, k])[0][0:-1]
            sub = np.round(pos).astype(int)
            # Find where is the point if inside the volume :
            if self >= sub:  # use __ge__ of RoiObj
                idx_vol = self.vol[sub[0], sub[1], sub[2]] + self._offset
                location = self.find_label(idx_vol)
            else:
                location = None
            self.analysis.loc[k] = location
        self.analysis['name'] = source_name
        self.analysis['x'] = xyz[0]
        self.analysis['y'] = xyz[1]
        self.analysis['z'] = xyz[2]
        if replace_bad:
            # Replace NaN values :
            self.analysis.fillna(replace_with, inplace=True)
            # Replace bad patterns :
            for k in bad_patterns:
                self.analysis.replace(k, replace_with, inplace=True)
        return self.analysis

    def find_label(self, vol_idx):
        ref_index = np.where(self.ref['index'] == vol_idx)[0]
        return self[int(ref_index)] if ref_index.size else None

    @staticmethod
    def _unpack_struct_array(arr):
        try:
            if arr.dtype.names is None:
                return {'label': arr}
            else:
                return {k: arr[k] for k in arr.dtype.names}
        except:
            return {'label': arr}

    def roi_to_mesh(self):
        pass

