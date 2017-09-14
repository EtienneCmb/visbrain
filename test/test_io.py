import os
import numpy as np

from visbrain.io.dependencies import is_mne_installed, is_nibabel_installed
from visbrain.io.read_annotations import (annotations_to_array,
                                          merge_annotations)
from visbrain.io.write_data import (write_csv, write_txt)


# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))


class TestIO(object):
    """Test function in dependencies.py."""

    ###########################################################################
    #                                 SETTINGS
    ###########################################################################
    def test_create_tmp_folder(self):
        """Create tmp folder."""
        if not os.path.exists(path_to_tmp):
            os.makedirs(path_to_tmp)

    @staticmethod
    def _path_to_tmp(name):
        return os.path.join(*(path_to_tmp, name))

    ###########################################################################
    #                              DEPENDENCIES
    ###########################################################################

    def test_is_mne_installed(self):
        """Test is_mne_installed function."""
        assert is_mne_installed()

    def test_is_nibabel_installed(self):
        """Test function is_nibabel_installed."""
        assert is_nibabel_installed()

    ###########################################################################
    #                              ANNOTATIONS
    ###########################################################################

    def test_write_annotations(self):
        """Test function write_annotations."""
        n = 10
        start = list(np.random.rand(n))
        end = list(np.random.rand(n))
        text = ['Annotation ' + str(k) for k in range(n)]
        write_csv('annotations.csv', zip(start, end, text))
        write_txt('annotations.csv', zip(start, end, text))

    def test_annotations_to_array(self):
        """Test function annotations_to_array."""
        pass
