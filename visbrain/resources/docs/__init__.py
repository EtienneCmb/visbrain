"""Doc build assets packaged with Visbrain."""
from __future__ import annotations

from importlib import resources

__all__ = ["package_path"]


def package_path(*parts: str) -> str:
    """Return the filesystem path for a packaged documentation asset."""
    traversable = resources.files(__name__)
    for part in parts:
        traversable = traversable.joinpath(part)
    return str(traversable)
