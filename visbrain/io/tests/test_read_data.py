"""Test function in read_data.py."""
# import pytest

from visbrain.io.read_data import (read_mat, read_pickle, read_npy, read_npz,  # noqa
                                   read_txt, read_csv, read_json,
                                   read_stc, read_x3d, read_gii, read_obj)
from visbrain.io.download import download_file


class TestReadData(object):
    """Test functions in read_data.py."""

    @staticmethod
    def _test_mesh(vertices, faces):
        assert (vertices.ndim == 2) and (faces.ndim == 2)
        assert vertices.shape[1] == faces.shape[1] == 3
        assert faces.max() < vertices.shape[0]

    def test_read_stc(self):
        """Test function read_stc."""
        read_stc(download_file("meg_source_estimate-lh.stc",
                               astype='example_data'))

    def test_read_x3d(self):
        """Test function read_x3d."""
        file = download_file('ferret.x3d', astype='example_data')
        vert, faces = read_x3d(file)
        self._test_mesh(vert, faces)

    def test_read_gii(self):
        """Test function read_gii."""
        file = download_file('lh.bert.inflated.gii', astype='example_data')
        vert, faces = read_gii(file)
        self._test_mesh(vert, faces)

    def test_read_obj(self):
        """Test function read_obj."""
        file = download_file('brain.obj', astype='example_data')
        vert, faces = read_obj(file)
        self._test_mesh(vert, faces)

    # @pytest.mark.slow
    # def test_read_nifti(self):
    #     """Test function read_nifti."""
    #     read_nifti(download_file("GG-853-GM-0.7mm.nii.gz",
    #                              astype='example_data'))
