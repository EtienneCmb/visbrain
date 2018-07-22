"""Test methods in path."""
import os

from visbrain.io.path import (path_to_visbrain_data, get_data_url_path,
                              path_to_tmp, clean_tmp, get_files_in_folders)


class TestPath(object):
    """Test path."""

    def test_get_data_url_path(self):
        """Test function get_data_url_path."""
        assert os.path.isfile(get_data_url_path())

    def test_path_to_visbrain_data(self):
        """Test function path_to_visbrain_data."""
        path = path_to_visbrain_data()
        assert os.path.isdir(path)

    def test_path_to_tmp(self):
        """Test function path_to_tmp."""
        assert os.path.isdir(path_to_tmp())

    def test_clean_tmp(self):
        """Test function clean_tmp."""
        path = path_to_tmp()
        assert os.path.isdir(path)
        clean_tmp()
        assert not os.path.isdir(path)

    def test_get_files_in_folders(self):
        """Test function get_files_in_folders."""
        vb_path = path_to_visbrain_data(folder='templates')
        # Test with / without extension :
        lst = get_files_in_folders(vb_path, with_ext=False)
        lst_ext = get_files_in_folders(vb_path, with_ext=True, exclude=['npy'])
        assert (len(lst) > 1) and all(['.npz' not in k for k in lst])
        assert all(['.npz' in k for k in lst_ext])
        # Test exclude :
        lst_exc = get_files_in_folders(vb_path, exclude=['B1'])
        assert all(['B1' not in k for k in lst_exc])
        # Test with / without path :
        lst_no_path = get_files_in_folders(vb_path, with_path=False)[0]
        lst_path = get_files_in_folders(vb_path, with_path=True)[0]
        assert os.path.split(lst_path)[1] == lst_no_path
        # Sort :
        get_files_in_folders(vb_path, sort=True)
