"""
"""

__all__ = ['write_config_json']


def write_config_json(filename, vars={}):
    """Save configuration file as JSON.

    Args:
        filename: string
            Filename for saving.

    Kargs:
        vars: dict, optional, (def: {})
            Variables to save.
    """
    import json
    if filename:
        with open(filename, 'w') as f:
            json.dump(vars, f)


def load_config_json(filename):
    """Load configuration file as JSON."""
    pass
