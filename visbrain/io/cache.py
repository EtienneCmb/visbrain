"""Centralized cache and data directory management for Visbrain."""
from __future__ import annotations

import threading
import uuid
from collections import defaultdict
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
)

import shutil


__all__ = ["CacheManager", "cache_manager"]


PathFactory = Callable[[bool], Path]
_OwnerRegistry = MutableMapping[str, set[Tuple[str, Path]]]


class CacheManager:
    """Manage cache directories and allow scoped cleanup policies.

    Parameters
    ----------
    roots : Mapping[str, Callable[[bool], Path]]
        Mapping of cache *category* names to callables returning the base
        directory for the category. Each callable receives a boolean *create*
        flag indicating whether the caller intends to create the directory.
    default_category : str
        Category used when one is not explicitly supplied.
    """

    def __init__(
        self,
        roots: Mapping[str, PathFactory],
        *,
        default_category: str = "tmp",
    ) -> None:
        if default_category not in roots:
            raise ValueError(
                f"Default category '{default_category}' is not defined in roots"
            )
        self._roots: Dict[str, PathFactory] = dict(roots)
        self._default_category = default_category
        self._lock = threading.Lock()
        self._owners: _OwnerRegistry = defaultdict(set)

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------
    def _resolve_root(
        self, *, category: Optional[str] = None, create: bool = False
    ) -> Path:
        name = category or self._default_category
        factory = self._roots.get(name)
        if factory is None:
            raise KeyError(f"Unknown cache category: {name}")
        root = factory(create)
        if create:
            root.mkdir(parents=True, exist_ok=True)
        return root

    def _register_owner(self, owner: str, category: str, path: Path) -> None:
        with self._lock:
            self._owners.setdefault(owner, set()).add((category, path))

    def _iter_owner_entries(self, owner: str) -> Iterable[Tuple[str, Path]]:
        with self._lock:
            entries = self._owners.pop(owner, set())
        return tuple(entries)

    def _cleanup_path(
        self,
        path: Path,
        *,
        category: str,
        missing_ok: bool = True,
    ) -> None:
        root = self._resolve_root(category=category, create=False)
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            raise ValueError(
                f"Refusing to clean path outside the '{category}' cache: {path}"
            ) from None

        if not path.exists():
            if missing_ok:
                return
            raise FileNotFoundError(path)

        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_path(
        self,
        *,
        folder: Optional[Sequence[str] | str] = None,
        file: Optional[str] = None,
        create: bool = False,
        category: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> Path:
        """Return a path inside the cache, optionally creating it."""

        root = self._resolve_root(
            category=category,
            create=create or bool(folder),
        )
        parts: tuple[str, ...]
        if folder is None:
            parts = ()
        elif isinstance(folder, str):
            parts = (folder,)
        else:
            parts = tuple(folder)
        target = root.joinpath(*parts)
        if file:
            target = target / file

        if create:
            parent = target.parent if file else target
            parent.mkdir(parents=True, exist_ok=True)
            if file:
                target.touch(exist_ok=True)

        if owner:
            self._register_owner(
                owner,
                category or self._default_category,
                target,
            )
        return target

    def new_session(
        self,
        owner: str,
        *,
        prefix: str = "session",
        category: Optional[str] = None,
    ) -> Path:
        """Reserve and return a unique subdirectory owned by *owner*."""

        base = self.get_path(folder=prefix, create=True, category=category)
        while True:
            candidate = base / uuid.uuid4().hex
            try:
                candidate.mkdir(parents=False, exist_ok=False)
            except FileExistsError:  # pragma: no cover - extremely unlikely
                continue
            break
        self._register_owner(
            owner,
            category or self._default_category,
            candidate,
        )
        return candidate

    def cleanup_owner(self, owner: str, *, missing_ok: bool = True) -> None:
        """Remove all cache entries registered to *owner*."""

        for category, path in self._iter_owner_entries(owner):
            self._cleanup_path(path, category=category, missing_ok=missing_ok)

    def cleanup_path(
        self,
        path: Path,
        *,
        category: Optional[str] = None,
        missing_ok: bool = True,
    ) -> None:
        """Remove *path* inside the cache, bypassing ownership tracking."""

        self._cleanup_path(
            path,
            category=category or self._default_category,
            missing_ok=missing_ok,
        )

    def cleanup_all(self, *, category: Optional[str] = None) -> None:
        """Remove the entire cache tree for *category*."""

        name = category or self._default_category
        root = self._resolve_root(category=name, create=False)
        if root.exists():
            shutil.rmtree(root)
        with self._lock:
            for owner, entries in list(self._owners.items()):
                self._owners[owner] = {
                    entry for entry in entries if entry[0] != name
                }
                if not self._owners[owner]:
                    del self._owners[owner]

    def root_path(
        self,
        *,
        category: Optional[str] = None,
        create: bool = False,
    ) -> Path:
        """Return the base directory for *category*."""

        return self._resolve_root(category=category, create=create)


# The concrete manager is instantiated in :mod:`visbrain.io.path` so that the
# platform specific helpers remain centralized in one module.
cache_manager: Optional[CacheManager] = None
"""Module level placeholder to be populated by :mod:`visbrain.io.path`."""
