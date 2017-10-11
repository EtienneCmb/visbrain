import numpy as np

from .visbrain_obj import VisbrainObject
from ..utils import load_predefined_roi


class RoiObj(VisbrainObject):
    """docstring for RoiObj"""

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, vol=None, index=None, label=None, hdr=None,
                 parent=None):
        """Init."""
        # Init Visbrain object base class :
        VisbrainObject.__init__(self, name, parent)
        # _______________________ PREDEFINED _______________________
        if name in ['brodmann', 'talairach', 'aal']:
            vol, label, index, hdr = load_predefined_roi(name)

        # _______________________ CHECKING _______________________
        # vol :
        assert vol.ndim == 3
        assert len(index) == len(label)
        self.vol = vol
        self._n_roi = len(index)
        # hdr :
        self.hdr = np.eye(4) if hdr is None else hdr
        assert self.hdr.shape == (4, 4)

        # _______________________ REFERENCE _______________________
        self.ref = np.zeros(len(self), dtype=[('number', np.int, 1),
                                              ('index', np.int, 1),
                                              ('label', object, 1)])
        self.ref['number'] = np.arange(len(self)).astype(np.int)
        self.ref['index'] = index.astype(np.int)
        self.ref['label'] = label

    def __len__(self):
        """Return the number of ROI."""
        return self._n_roi

    def __getitem__(self, index):
        """Get the ref item at index."""
        if isinstance(index, (int, list, np.ndarray, slice)):
            return self.ref[index]

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

    def find_label(self, vol_idx):
        ref_index = np.where(self.ref['index'] == vol_idx)[0]
        return self[ref_index] if ref_index.size else None


    def roi_to_mesh(self):
        pass

    # ----------- DTYPE -----------
    @property
    def dtype(self):
        """Get the dtype value."""
        return self.ref.dtype

