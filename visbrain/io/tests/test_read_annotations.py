"""Test functions in read_annotations.py."""
import numpy as np

from visbrain.io.read_annotations import (annotations_to_array,
                                          merge_annotations)
from visbrain.io.write_data import (write_csv, write_txt)
from visbrain.tests._tests_visbrain import _TestVisbrain


class TestReadAnnotations(_TestVisbrain):
    """Test functions in read_annotations.py."""

    @staticmethod
    def _get_annotations(dtype=float, n=10, as_list=False):
        start = np.random.rand(n).astype(dtype)
        end = np.random.rand(n).astype(dtype)
        text = ['Annotation ' + str(k) for k in range(n)]
        if as_list:
            return list(start), list(end), list(text)
        else:
            return start, end, text

    def _get_annotation_type(self):
        from mne import Annotations
        one_d = self._get_annotations(as_list=False)[0]
        one_d_list = self._get_annotations(as_list=True)[0]
        three_d = np.c_[self._get_annotations()]
        csv = self.to_tmp_dir('annotations.csv')
        txt = self.to_tmp_dir('annotations.txt')
        mne = Annotations(*self._get_annotations())
        return one_d, one_d_list, three_d, csv, txt, mne

    def test_write_annotations(self):
        """Test function write_annotations."""
        start, end, text = self._get_annotations(str, as_list=True)
        write_csv(self.to_tmp_dir('annotations.csv'), zip(start, end, text))
        write_txt(self.to_tmp_dir('annotations.txt'), zip(start, end, text))

    def test_annotations_to_array(self):
        """Test function annotations_to_array."""
        for k in self._get_annotation_type():
            annotations_to_array(k)

    def test_merge_annotations(self):
        """Test function merge_annotations."""
        merge_annotations(*(None, *self._get_annotation_type()))
