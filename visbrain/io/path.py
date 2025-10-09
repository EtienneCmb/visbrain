"""Utilities for locating Visbrain data resources."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from importlib import resources

from visbrain.data import bundled_path
from . import cache as _cache_module

logger = logging.getLogger('visbrain')


__all__ = ['cache_manager', 'path_to_visbrain_data', 'get_files_in_folders',
           'path_to_tmp', 'clean_tmp', 'get_data_url_path']


_ENV_DATA_HOME = "VISBRAIN_DATA_DIR"


def _platform_data_home() -> Path:
    """Return the default writable data directory for Visbrain."""

    home = Path.home()
    if sys.platform.startswith("win"):
        root = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return root / "Visbrain"
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "Visbrain"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else home / ".local" / "share"
    return base / "visbrain"


def _data_home(create: bool = False) -> Path:
    """Return the writable data directory, honoring the override env var."""

    root = Path(os.environ.get(_ENV_DATA_HOME, "")).expanduser()
    if not root:
        root = _platform_data_home()
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def _path_from_home(file: Optional[str] = None, folder: Optional[str] = None,
                    create: bool = False) -> Path:
    """Build a path inside the writable data directory."""

    base = _data_home(create=create or bool(folder))
    if folder:
        base = base / folder
        if create:
            base.mkdir(parents=True, exist_ok=True)
    if file:
        target = base / file
        if create:
            target.parent.mkdir(parents=True, exist_ok=True)
        return target
    return base


_cache_module.cache_manager = _cache_module.CacheManager(
    {
        'tmp': lambda create: _path_from_home(folder='tmp', create=create),
        'data': lambda create: _path_from_home(create=create),
    },
    default_category='tmp',
)
cache_manager = _cache_module.cache_manager


def _path_from_bundle(file: Optional[str] = None,
                      folder: Optional[str] = None) -> Optional[Path]:
    """Resolve a path from bundled resources if present."""

    parts = []
    if folder:
        parts.append(folder)
    if file:
        parts.append(file)
    if not parts:
        return None
    try:
        return bundled_path(*parts)
    except FileNotFoundError:
        return None


def path_to_visbrain_data(file=None, folder=None, *, create=False,
                          allow_bundled=True):
    """Get the path to visbrain resources or writable storage.

    Parameters
    ----------
    folder : string | None
        Folder name.
    file : string | None
        File name. If None, only the path to the visbrain_data folder is
        returned.
    create : bool | False
        Create the folder on the filesystem if it does not already exist.
    allow_bundled : bool | True
        Allow returning a path to a packaged resource if available.

    Returns
    -------
    path : string
        Path to the file or directory.
    """
    file = None if not isinstance(file, str) else file
    folder = None if not isinstance(folder, str) else folder

    if allow_bundled:
        bundled = _path_from_bundle(file=file, folder=folder)
        if bundled is not None:
            return str(bundled)

    path = cache_manager.get_path(
        folder=folder,
        file=file,
        create=create,
        category='data',
    )
    if not path.exists() and not create and file:
        logger.debug("Requested visbrain data file missing: %s", path)
    return str(path)


def get_data_url_path():
    """Get the path to the data_url JSON file."""
    traversable = resources.files('visbrain').joinpath('data_url.json')
    if not traversable.exists():  # pragma: no cover - packaging error
        raise FileNotFoundError('visbrain/data_url.json resource missing')
    with resources.as_file(traversable) as path:
        return str(path)


def get_files_in_folders(*args, with_ext=False, with_path=False, file=None,
                         exclude=None, sort=True, unique=True):
    """Get all files in several folders.

    Parameters
    ----------
    args : string
        Path to folders.
    with_ext : bool | False
        Specify if returned files should contains extensions.
    with_path : bool | False
        Specify if returned files should contains full path to it.
    file : string | None
        Specify if a specific file name is needed.
    exclude : list | None
        List of patterns to exclude
    sort : bool | True
        Sort the resulting list of files.
    unique : bool | True
        Get a unique list of files.

    Returns
    -------
    files : list
        List of files in selected folders if no file is provided. If file is a
        string, return the path to it, None if the file doesn't exist.
    """
    # Search the file :
    files = []
    if isinstance(file, str):
        import glob
        for k in args:
            if os.path.exists(k):
                files += glob.glob(os.path.join(k, file))
        return files
    # Get the list of files :
    for k in args:
        if os.path.exists(k):
            if with_path:
                files += [os.path.join(k, i) for i in os.listdir(k)]
            else:
                files += os.listdir(k)
    # Keep only a selected file :
    if isinstance(file, str) and (file in files):
        files = [files[files.index(file)]]
    # Return either files with full path or only file name :
    if not with_ext:
        files = [os.path.splitext(k)[0] for k in files]
    # Patterns to exclude :
    if isinstance(exclude, (list, tuple)):
        from itertools import product
        files = [k for k, i in product(files, exclude) if i not in k]
    # Unique :
    if unique:
        files = list(set(files))
    # Sort list :
    if sort:
        files.sort()
    return files


def path_to_tmp(file=None, folder=None):
    """Get the path to the tmp folder."""
    tmp_path = _path_from_home(folder='tmp', create=True)
    folder = None if not isinstance(folder, str) else folder
    file = None if not isinstance(file, str) else file
    path = cache_manager.get_path(folder=folder, file=file, create=True)
    return str(path)


def clean_tmp():
    """Clean the tmp folder."""
    tmp_path = cache_manager.root_path(create=False)
    cache_manager.cleanup_all()
    return str(tmp_path)
