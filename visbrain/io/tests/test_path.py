"""Test methods in path."""
import os
from pathlib import Path

from visbrain.io.path import (
    cache_manager,
    clean_tmp,
    get_data_url_path,
    get_files_in_folders,
    path_to_tmp,
    path_to_visbrain_data,
)


class TestPath(object):
    """Test path."""

    def _prepare_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("VISBRAIN_DATA_DIR", str(tmp_path))
        cache_manager.cleanup_all()
        cache_manager.cleanup_all(category='data')

    def test_get_data_url_path(self, monkeypatch, tmp_path):
        """Test function get_data_url_path."""
        self._prepare_env(monkeypatch, tmp_path)
        assert os.path.isfile(get_data_url_path())

    def test_path_to_visbrain_data(self, monkeypatch, tmp_path):
        """Test function path_to_visbrain_data."""
        self._prepare_env(monkeypatch, tmp_path)
        path = path_to_visbrain_data(create=True, allow_bundled=False)
        assert os.path.isdir(path)

    def test_path_to_tmp(self, monkeypatch, tmp_path):
        """Test function path_to_tmp."""
        self._prepare_env(monkeypatch, tmp_path)
        tmp_root = Path(path_to_tmp())
        assert tmp_root.is_dir()
        session = cache_manager.new_session('test-case', prefix='session-test')
        assert session.exists()
        cache_manager.cleanup_owner('test-case')
        assert not session.exists()

    def test_clean_tmp(self, monkeypatch, tmp_path):
        """Test function clean_tmp."""
        self._prepare_env(monkeypatch, tmp_path)
        tmp_root = Path(path_to_tmp())
        nested = Path(path_to_tmp(folder='nested'))
        assert tmp_root.is_dir()
        assert nested.is_dir()
        cleaned = Path(clean_tmp())
        assert not cleaned.exists()
        assert not tmp_root.exists()

    def test_get_files_in_folders(self, monkeypatch, tmp_path):
        """Test function get_files_in_folders."""
        self._prepare_env(monkeypatch, tmp_path)
        roi_path = path_to_visbrain_data(folder='roi')
        # Test with / without extension :
        lst = get_files_in_folders(roi_path, with_ext=False)
        lst_ext = get_files_in_folders(roi_path, with_ext=True, exclude=['tmp'])
        assert lst  # at least one file bundled with the wheel
        assert all(['.npz' not in k for k in lst])
        assert all(['.npz' in k for k in lst_ext])
        # Test with / without path :
        lst_no_path = get_files_in_folders(roi_path, with_path=False)[0]
        lst_path = get_files_in_folders(roi_path, with_path=True)[0]
        assert os.path.split(lst_path)[1] == lst_no_path
        # Sort :
        get_files_in_folders(roi_path, sort=True)
