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
    import io
    import json

    # Ensure Python version compatibility
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    if filename:
        with io.open(filename, 'w', encoding='utf8') as f:
            str_ = json.dumps(config, indent=4, sort_keys=True,
                              separators=(',', ': '),  # Pretty printing
                              ensure_ascii=False)
            f.write(to_unicode(str_))


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
