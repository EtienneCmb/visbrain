"""Test functions in rw_config.py."""
from visbrain.io.rw_config import save_config_json, load_config_json
from visbrain.tests._tests_visbrain import _TestVisbrain


class TestRwConfig(_TestVisbrain):
    """Test functions in rw_config.py."""

    @staticmethod
    def _get_config():
        config = {'Button1': True, 'Button2': 1, 'Button3': None}
        return config

    def test_save_config_json(self):
        """Test function save_config_json."""
        save_config_json(self.to_tmp_dir('config.txt'), self._get_config())

    def test_load_config_json(self):
        """Test function load_config_json."""
        config = load_config_json(self.to_tmp_dir('config.txt'))
        assert config == self._get_config()
