========
Visbrain
========

.. image:: https://github.com/visbrain-dev/visbrain/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/visbrain-dev/visbrain/actions/workflows/ci.yml
   :alt: GitHub Actions CI status

.. image:: https://github.com/visbrain-dev/visbrain/actions/workflows/docs.yml/badge.svg?branch=main
   :target: https://github.com/visbrain-dev/visbrain/actions/workflows/docs.yml
   :alt: Documentation build status

.. image:: https://img.shields.io/pypi/v/visbrain.svg
   :target: https://pypi.org/project/visbrain/
   :alt: Latest release on PyPI

.. image:: https://img.shields.io/conda/vn/conda-forge/visbrain.svg
   :target: https://anaconda.org/conda-forge/visbrain
   :alt: Latest release on conda-forge

**Visbrain** is an open-source neuroinformatics toolkit for interactive brain
signal visualisation. The modernization effort targets Python 3.9–3.12,
leverages Qt 6 through PySide6, and builds 3D rendering pipelines on top of
`VisPy <http://vispy.org/>`_. We are incrementally refreshing the legacy code
base, updating documentation, and aligning packaging so researchers can deploy
the stack on current desktop platforms.

Project status
--------------

Visbrain is in the middle of a major rewrite that has relied heavily on AI
assistance to port large sections of the legacy code base to modern
dependencies. Much of the graphical stack compiles, but end-to-end workflows
remain unstable and key GUIs are still being rebuilt. Expect missing features,
rough edges, and incomplete documentation while we bring the reimplementation
into shape. Community feedback is invaluable—please report breakage and help us
prioritise the next milestones.

* `Modernization roadmap <docs/modernization/index.rst>`_
* `Project governance <docs/governance.rst>`_

The original visbrain.org website has gone offline; this repository now serves
as the canonical source of documentation and examples. Development happens in
the open on GitHub where the automation badges above track CI and docs health.

Quick start
-----------

Check the runtime environment and OpenGL support with::

   python -m visbrain info

Launch the Sleep GUI from a Python shell to explore bundled sample datasets::

   from visbrain.gui import Sleep
   Sleep().show()

Modernization roadmap
---------------------

Visbrain is currently undergoing a multi-phase modernization effort. Phase 0
established the supported operating systems, Python versions, and tooling. The
roadmap has progressed through infrastructure, API, and quality automation
workstreams and is now focused on `Phase 6 <docs/modernization/phase-6.rst>`_,
where release automation and distribution hardening take centre stage. Follow
the detailed milestones in ``docs/modernization/`` for an up-to-date view of
the active workstreams and consult the `release automation guide
<docs/release.rst>`_ for the associated checklists.

For day-to-day development work on this modernization track we recommend
either opening the repository in the provided development container or
creating a virtual environment that matches the baseline environment matrix:

* **Dev Container** — Open the folder in VS Code (or another
  devcontainer-aware editor) and reopen in the container. The image installs
  the Phase 0 toolchain automatically by running ``pip install -r
  requirements/dev.txt`` after the first build and forwards common notebook
  and application ports.

* **Local virtual environment** — Create a virtual environment and install the
  pinned dependencies manually:

  .. code-block:: console

     python -m venv .venv
     source .venv/bin/activate  # On Windows use .venv\\Scripts\\activate
     python -m pip install --upgrade pip
     pip install -r requirements/dev.txt

  .. note::

     Linux contributors need the Mesa/OpenGL runtime for PySide6/VisPy to
     initialize correctly in headless CI containers. Install the packages with::

        sudo apt-get update
        sudo apt-get install -y libgl1 libglu1-mesa libgl1-mesa-dri mesa-utils libxcb-xinerama0

These pins align with Python 3.9–3.12 on Windows, macOS, and Linux and will be
revisited as the modernization roadmap advances.

With the toolchain installed, invoking ``python -m tox`` orchestrates the main
contributor workflows. The module form keeps the commands working even when the
``tox`` console script is not on your ``PATH``:

.. code-block:: console

   python -m tox -e lint           # run Ruff
   python -m tox -e lint-format    # confirm Black and Ruff formatting
   python -m tox -e type           # run the MyPy type checks
   python -m tox -e tests          # run the pytest suite headlessly
   python -m tox -e tests-gui      # run the GUI tests that need a display server
   python -m tox -e tests-screenshot  # compare the Qt/VisPy screenshot baselines
   python -m tox -e package        # build sdist/wheel artifacts

Screenshot baselines live under ``visbrain/gui/tests/baseline``. When a GUI
change legitimately alters the visuals, refresh them locally and include the
updated PNGs in your commit::

   VISBRAIN_UPDATE_SCREENSHOTS=1 tox -e tests-screenshot

The ``Makefile`` exposes matching shortcuts (``make lint``, ``make test`` and
``make build_dist``) for projects that rely on the historical targets.

Important links
---------------

* Source code repository : https://github.com/visbrain-dev/visbrain
* Development documentation : https://github.com/visbrain-dev/visbrain/tree/main/docs
* Modernization roadmap : https://github.com/visbrain-dev/visbrain/blob/main/docs/modernization/index.rst
* Governance overview : https://github.com/visbrain-dev/visbrain/blob/main/docs/governance.rst


Installation
------------

Install from source (recommended)
++++++++++++++++++++++++++++++++

The published wheels on PyPI/conda-forge predate the modernization work and no
longer reflect the rapidly changing code base. For the best experience, clone
the repository and run Visbrain directly from the current sources. We recommend
`uv <https://github.com/astral-sh/uv>`_ for repeatable virtual environments and
fast dependency installs:

.. code-block:: console

   git clone https://github.com/visbrain-dev/visbrain.git
   cd visbrain
   uv venv --python 3.11
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   uv pip install --upgrade pip
   uv pip install -r requirements/dev.txt
   uv pip install -e .

.. note::

   Linux contributors still need the Mesa/OpenGL runtime for PySide6/VisPy to
   initialise correctly. Install the packages with::

      sudo apt-get update
      sudo apt-get install -y libgl1 libglu1-mesa libgl1-mesa-dri mesa-utils libxcb-xinerama0

Legacy packages
+++++++++++++++

``pip install visbrain`` and the conda-forge builds remain available but are no
longer maintained. They track the pre-modernization code base and miss critical
fixes for Python 3.9+ and Qt 6. Prefer the source workflow above unless you are
debugging historical behaviour.

Sample data and optional downloads
+++++++++++++++++++++++++++++++++++++

The Visbrain wheel bundles small reference datasets so common workflows run
offline: core brain templates, ROI atlases, an EEG montage and a short
hypnogram are available through ``visbrain.io.path_to_visbrain_data`` without
creating ``~/visbrain_data``. Heavier assets (extended sleep recordings, large
surface meshes, etc.) stay optional and are fetched explicitly with the
``visbrain.io.download`` helper::

    python -m visbrain.io.download --list
    python -m visbrain.io.download sleep_rec.zip --type example_data

Downloads land in a platform-specific cache managed by
``visbrain.io.cache.CacheManager``. Durable resources use the ``data``
category under ``VISBRAIN_DATA_DIR`` (falling back to ``%APPDATA%/Visbrain`` on
Windows, ``~/Library/Application Support/Visbrain`` on macOS and
``~/.local/share/visbrain`` on Linux). Scratch artefacts (temporary exports,
download staging areas, etc.) flow through the ``tmp`` category so they can be
purged automatically after workflows finish. The downloader exposes ``--dest``
and ``--use-pwd`` switches to override the target directory when integrating
with project-specific storage.

Sample data downloads
++++++++++++++++++++++

.. note::

   Network downloads are opt-in. Set ``VISBRAIN_ALLOW_DOWNLOADS=1`` in the
   environment (or pass ``allow_download=True`` directly) when a workflow needs
   to fetch assets. Examples in ``examples/`` now enable the flag explicitly
   wherever they expect to pull sample datasets.

BIDS-aware sleep loading
------------------------

The ``visbrain.gui.Sleep`` controller understands complete BIDS datasets
through the ``visbrain.io.read_sleep`` helpers. Forward a dataset root while
opting into MNE-based loading and provide entity filters to resolve a specific
recording::

   from visbrain.gui import Sleep

   Sleep(
       data='/path/to/bids_root',
       use_mne=True,
       kwargs_mne={
           'bids_entities': {'subject': '01', 'task': 'rest'},
           'bids_resolve': 'first',
       },
   ).show()

The loader accepts explicit ``mne_bids.BIDSPath`` instances, dictionaries
of entities or relative filenames. When multiple recordings match the filters
you can choose ``bids_resolve="first"``, ``"last"`` or a numeric index to pick
the desired run.

Diagnosing GPU availability
---------------------------

Run ``python -m visbrain info`` to collect the VisPy/OpenGL diagnostics tracked
by ``visbrain.config``. The command prints the resolved backend, GL limits
and shader compilation results alongside actionable guidance, or ``--json`` can
emit the raw payload for automated health checks.

