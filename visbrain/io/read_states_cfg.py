"""Load and check states config dictionary."""

from .rw_config import load_config_json


DF_STATES_CFG = {
    "Art": {
        "color": "black",
        "shortcut": "a",
        "value": -1,
        "display_order": 0,
    },
    "Wake": {
        "color": "black",
        "shortcut": "w",
        "value": 0,
        "display_order": 1,
    },
    "REM": {
        "color": "green",
        "shortcut": "r",
        "value": 4,
        "display_order": 2,
    },
    "N1": {
        "color": "red",
        "shortcut": "1",
        "value": 1,
        "display_order": 5,
    },
    "N2": {
        "color": "blue",
        "shortcut": "2",
        "value": 2,
        "display_order": 3,
    },
    "N3": {
        "color": "blue",
        "shortcut": "2",
        "value": 3,
        "display_order": 4,
    },
}


def load_states_cfg(states_config_file):
    if states_config_file is None:
        return DF_STATES_CFG
    cfg = load_config_json(states_config_file)
    return check_states_cfg(cfg)


def check_states_cfg(states_cfg):
    # TODO
    # Unique states:
    if not len(set(states_cfg.keys())) == len(states_cfg.keys()):
        raise ValueError(f"Duplicate keys in states cfg dict: {states_cfg}")
    return states_cfg
