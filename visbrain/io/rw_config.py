"""Load and save configurations."""

__all__ = ['save_config_json', 'load_config_json']


def save_config_json(filename, config):
    """Save configuration file as JSON.

    Parameters
    ----------
    filename : string
        Name of the configuration file to save.
    config : dict
        Dictionary of arguments to save.
    """
    import json
    if filename:
        with open(filename, 'w') as f:
            json.dump(config, f)


def load_config_json(filename):
    """Load configuration file as JSON.

    Parameters
    ----------
    filename : string
        Name of the configuration file to load.

    Returns
    -------
    config : dict
        Dictionary of config.
    """
    import json
    with open(filename) as f:
        # Load the configuration file :
        config = json.load(f)
    return config
