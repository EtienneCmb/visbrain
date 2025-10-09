"""Test functions in download.py."""
from pathlib import Path

from visbrain.io.download import download_file, main as download_main


class TestDownload(object):
    """Test functions in download.py."""

    def test_download_file(self, monkeypatch, tmp_path):
        """Test function download_file."""
        target = tmp_path / 'Px.npy'

        def _fake_urlretrieve(url, filename, reporthook=None):
            Path(filename).write_bytes(b'dummy')
            return filename, None

        monkeypatch.setattr('visbrain.io.download.request.urlretrieve',
                            _fake_urlretrieve)
        path = download_file(
            'Px.npy', astype='example_data', to_path=tmp_path, allow_download=True
        )
        assert Path(path).is_file()
        assert Path(path) == target

    def test_download_custom_url(self, monkeypatch, tmp_path):
        """Test function download_custom_url."""
        name = "https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1"
        dest = tmp_path / 'text.npz'

        def _fake_urlretrieve(url, filename, reporthook=None):
            Path(filename).write_bytes(b'dummy')
            return filename, None

        monkeypatch.setattr('visbrain.io.download.request.urlretrieve',
                            _fake_urlretrieve)
        download_file(
            name,
            filename="text.npz",
            to_path=tmp_path,
            allow_download=True,
        )
        assert dest.is_file()

    def test_cli_list(self, capsys):
        """Ensure the CLI prints the available datasets."""

        download_main(['--list'])
        captured = capsys.readouterr()
        assert 'templates' in captured.out

    def test_cli_download(self, monkeypatch, tmp_path):
        """Exercise the CLI download path without touching the network."""

        created = tmp_path / 'Px.npy'

        def _fake_urlretrieve(url, filename, reporthook=None):
            Path(filename).write_bytes(b'dummy')
            return filename, None

        monkeypatch.setattr('visbrain.io.download.request.urlretrieve',
                            _fake_urlretrieve)
        code = download_main(
            ['Px.npy', '--type', 'example_data', '--dest', str(tmp_path)]
        )
        assert code == 0
        assert created.is_file()

    # @pytest.mark.skip("Test downloading all files is too slow")
    # def test_download_files_from_dropbox(self):
    #     """Test function download_file from dropbox."""
    #     urls = get_data_url_file()
    #     for name in list(urls.keys()):
    #         download_file(name, astype='example_data')
