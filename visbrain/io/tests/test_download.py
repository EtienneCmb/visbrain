"""Test functions in download.py."""
import pytest
from visbrain.io.download import get_data_url_file, download_file


class TestDownload(object):
    """Test functions in download.py."""

    def test_get_data_url_file(self):
        """Test function get_data_url_file."""
        get_data_url_file()

    def test_download_file(self):
        """Test function download_file."""
        download_file('Px.npy')

    def test_download_custom_url(self):
        """Test function download_custom_url."""
        name = "https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1"
        download_file(name, filename="text.npz")

    @pytest.mark.skip("Test downloading all files is too slow")
    def test_download_files_from_dropbox(self):
        """Test function download_file from dropbox."""
        urls = get_data_url_file()
        for name in list(urls.keys()):
            download_file(name)
