"""Test function in read_data.py."""
# import pytest

from visbrain.io.read_data import (read_mat, read_pickle, read_npy, read_npz,  # noqa
                                   read_txt, read_csv, read_json,
                                   read_stc)
from visbrain.io.download import download_file


class TestReadData(object):
    """Test functions in read_data.py."""

    def test_read_stc(self):
        """Test function read_stc."""
        read_stc(download_file("meg_source_estimate-lh.stc",
                               astype='example_data'))

    # @pytest.mark.slow
    # def test_read_nifti(self):
    #     """Test function read_nifti."""
    #     read_nifti(download_file("GG-853-GM-0.7mm.nii.gz",
    #                              astype='example_data'))
