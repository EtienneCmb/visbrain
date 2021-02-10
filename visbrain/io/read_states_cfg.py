"""Load and check states config dictionary."""

import os.path

import yaml

DF_STATES_CFG = {
    "Art": {
        "color": 'red',
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
        "color": '#bf5656',
        "shortcut": "r",
        "value": 4,
        "display_order": 2,
    },
    "N1": {
        "color": '#aabcce',
        "shortcut": "1",
        "value": 1,
        "display_order": 3,
    },
    "N2": {
        "color": '#405c79',
        "shortcut": "2",
        "value": 2,
        "display_order": 4,
    },
    "N3": {
        "color": '#0b1c2c',
        "shortcut": "3",
        "value": 3,
        "display_order": 5,
    },
}


def load_states_cfg(states_cfg_file):
    if states_cfg_file is None:
        return DF_STATES_CFG
    if not os.path.exists(states_cfg_file):
        raise FileNotFoundError(
            f"No state cfg file found at {states_cfg_file}"
        )
    with open(states_cfg_file, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.SafeLoader)
    return check_states_cfg(cfg)


def check_states_cfg(states_cfg):

    bad = False
    msg = ("Incorrect formatting/values for user-specified states config "
           "dictionary:\n\n")

    if not len(states_cfg):
        bad = True
        msg += f"- States cfg dict can't be empty\n"

    # States are unique:
    if not len(set(states_cfg.keys())) == len(states_cfg.keys()):
        bad = True
        msg += f"- There are duplicate keys in states cfg dict\n"

    # Some keys are mandatory and allow no ties
    mandatory = ['shortcut', 'value', 'display_order']
    for key in mandatory:
        # Mandatory
        if not all([key in d for d in states_cfg.values()]):
            bad = True
            msg += ("- Mandatory key `{key}` is missing. The following keys "
                    f"are mandatory for each state: {mandatory}\n")
        else:
            # No ties
            key_values = [d[key] for d in states_cfg.values()]
            if not len(set(key_values)) == len(key_values):
                bad = True
                msg += (f"- Value across states should be unique for "
                        f"the following key: `{key}.\n")

    # Default color is black:
    for state_dict in states_cfg.values():
        if "color" not in state_dict:
            state_dict["color"] = 'black'

    if bad:
        msg = msg + f"\n\nLoaded states cfg: {states_cfg}"
        raise ValueError(msg)

    return states_cfg
