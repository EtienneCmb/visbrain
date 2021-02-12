"""Test functions in read_states_cfg.py."""

import pytest

import yaml
from visbrain.io.read_states_cfg import load_states_cfg
from visbrain.tests._tests_visbrain import _TestVisbrain

cfgs = [
    (
        {
            'N1': {'value': 1, 'shortcut': 1, 'display_order': 1},
            'N2': {'value': 2, 'shortcut': 2, 'display_order': 2},
        },
        None
    ),
    (
        {},
        ValueError  # Empty
    ),
    # (
    #     {
    #         'N1': {'value': 1, 'shortcut': 1, 'display_order': 1},
    #         'N1': {'value': 1, 'shortcut': 2, 'display_order': 2},
    #     },
    #     ValueError  # Non=unique states
    # ),
    (
        {
            'N1': {'value': 1, 'shortcut': 1, },
        },
        ValueError  # Missing key
    ),
    (
        {
            'N1': {'value': 1, 'display_order': 1},
        },
        ValueError  # Missing key
    ),
    (
        {
            'N1': {'shortcut': 1, 'display_order': 1},
        },
        ValueError  # Missing key
    ),
    (
        {
            'N1': {'value': 1, 'shortcut': 1, 'display_order': 1},
            'N2': {'value': 1, 'shortcut': 2, 'display_order': 2},
        },
        ValueError  # Ties
    ),
    (
        {
            'N1': {'value': 1, 'shortcut': 1, 'display_order': 1},
            'N2': {'value': 2, 'shortcut': 1, 'display_order': 2},
        },
        ValueError  # Ties
    ),
    (
        {
            'N1': {'value': 1, 'shortcut': 1, 'display_order': 1},
            'N2': {'value': 2, 'shortcut': 2, 'display_order': 1},
        },
        ValueError  # Ties
    ),
]


@pytest.fixture(params=cfgs)
def cfg_expected(request):
    return request.param


class TestStatesConfig(_TestVisbrain):
    """Test functions in read_states_cfg.py."""

    def _filepath(self, cfg):
        path = self.to_tmp_dir('tmp_cfg.yml')
        with open(path, 'w') as f:
            yaml.dump(cfg, f)
        return path

    def test_load_configs(self, cfg_expected):
        """Test function load_states_cfg.py"""
        cfg, expected = cfg_expected
        path = self._filepath(cfg)
        if expected is None:
            load_states_cfg(path)
        else:
            with pytest.raises(expected):
                load_states_cfg(path)
