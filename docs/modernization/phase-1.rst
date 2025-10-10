Phase 1 — Packaging and Dependency Overhaul
===========================================

Overview
--------

Phase 1 focuses on modern packaging primitives so the project can build with
current Python toolchains. The guiding principles are:

* publish metadata through ``pyproject.toml`` rather than ``setup.py``;
* raise dependency floors to versions that support Python 3.9+; and
* codify PySide6 as the supported Qt binding across packaging inputs.

Key changes
-----------

``pyproject.toml`` now drives builds with ``setuptools`` >= 68. The
configuration pulls the version from :mod:`visbrain`, exposes extras that mirror
past ``setup.py`` options, and declares a modern Python range. ``setup.py`` is
retained as a thin shim so existing workflows that call ``python setup.py``
continue to function.

The pinned requirement files were refreshed to align with the metadata. PySide6
and its companion ``shiboken6`` package anchor the runtime stack, while the
optional extras mirror the ``pyproject.toml`` extras. ``MANIFEST.in`` will
continue to ship the resource files consumed at runtime. Contributor-facing
documentation now references the PySide6 toolchain so setup guides match the
packaging metadata.

Data management also moved under the packaging umbrella. Frequently-used
resources (ROI atlases, EEG montages and sleep annotations) now live in the
``visbrain.data`` package and are exposed through ``importlib.resources``. The
``path_to_visbrain_data`` helper was updated to return bundled assets without
creating ``~/visbrain_data``; writable caches now follow platform defaults or
the ``VISBRAIN_DATA_DIR`` override. Functions that previously downloaded
archives on demand now raise a ``FileNotFoundError`` with instructions to run
``python -m visbrain.io.download <name> --type <kind>`` so data fetches become
an explicit user workflow instead of an implicit side effect.

The downloader doubles as a small CLI utility: running ``python -m
visbrain.io.download --list`` enumerates all available resources, while options
such as ``--dest`` and ``--use-pwd`` control where the files land. Archives are
extracted automatically unless ``--no-unzip`` is provided, keeping offline
installs self-contained.

Developer workflow
------------------

To build or install from a checkout::

   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements/dev.txt
   
``tox`` wraps the common workflows so contributors do not have to remember the
exact command lines::

   tox -e lint     # Ruff checks
   tox -e tests    # pytest with headless flags
   tox -e tests-screenshot  # screenshot regression harness
   tox -e package  # python -m build

The packaging environment executes ``python -m build`` under the hood and
validates that the ``pyproject.toml`` metadata is self-consistent. Contributors
can also install in editable mode with ``pip install -e .`` when iterating
locally.

Next steps
----------

* Convert continuous integration workflows to rely on ``pyproject.toml`` so
  future jobs no longer invoke ``setup.py`` directly.
* Begin extracting Qt-bound logic into dedicated adapters so Phase 2 can
  standardize on PySide6-friendly abstractions.
* Audit package data requirements and move any implicit resources into explicit
  ``tool.setuptools.package-data`` declarations.
