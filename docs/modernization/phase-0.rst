Phase 0 — Planning and Environment Baseline
===========================================

Overview
--------

Phase 0 formalizes the modernization targets before any large-scale refactors
begin. The goals are:

* identify the supported execution environments that future code must target;
* select the Qt binding that will drive the GUI overhaul; and
* deliver a reproducible development environment so contributors share a common
  toolchain.

Target platforms
----------------

The following baseline reflects current support in upstream dependencies while
remaining realistic for the team to test:

* **Python**: 3.9 through 3.12 (dropping 3.8 keeps pace with NumPy/Qt support).
* **Operating systems**: Windows 10/11, macOS 12 Monterey or newer (arm64 and
  x86_64), and Ubuntu 22.04 LTS or newer.
* **Qt binding**: PySide6 is adopted as the official GUI backend. It ships
  wheels for all target platforms, has an LGPL-friendly license, and maps
  closely onto Qt 6 API expectations. Shipping with the Qt 6 stack keeps the
  modernization roadmap focused on the end-state platform rather than
  maintaining compatibility shims for the legacy PyQt line.

These targets will guide dependency minimums, CI matrices, and documentation
updates in later phases.

Development environment baseline
--------------------------------

To make the project installable on the new baseline without waiting for the
packaging overhaul, Phase 0 introduces a pinned requirements set. The files in
``requirements/`` capture the exact versions the team validated locally. They
are a temporary bridge until the project migrates to ``pyproject.toml`` during
Phase 1.

Usage::

   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   python -m pip install --upgrade pip
   pip install -r requirements/dev.txt

The dev requirements extend the runtime pins with tooling for linting, testing,
and packaging. Contributors can rely on this environment while modernizing the
code base and standing up new CI jobs.

For contributors who prefer containerized tooling, the repository also ships a
``.devcontainer`` configuration compatible with VS Code and other editors that
understand the Dev Containers specification. Reopening the workspace in that
container builds on the Python 3.11 baseline image and automatically runs
``pip install -r requirements/dev.txt`` so the Phase 0 toolchain is ready
without additional manual setup. Forwarded ports cover common notebook and app
servers used when iterating on visualization examples.

Next steps
----------

* Track early compatibility issues with PySide6 and Qt 6 APIs while preparing
  broader refactors.
* Document environment quirks as they surface so future contributors have
  up-to-date guidance.
* Begin auditing modules that rely on legacy PyQt-only behavior so they can be
  replaced with PySide6-compatible patterns ahead of Phase 2 refactors.
* Refresh contributor docs when the dependency baselines move so that setup
  guidance always points to the PySide6 toolchain.
