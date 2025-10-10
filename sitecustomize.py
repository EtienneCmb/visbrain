"""Site customizations for Visbrain's development environment."""
from __future__ import annotations

import os

# Disable third-party plugin autoloading in pytest by default. GUI-focused test
# suites opt in explicitly by exporting ``VISBRAIN_ENABLE_PYTEST_QT=1``.
if not os.environ.get("VISBRAIN_ENABLE_PYTEST_QT"):
    os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
