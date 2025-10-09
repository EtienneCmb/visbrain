========
Visbrain
========

**Visbrain** was an open-source python 3 package dedicated to brain signals visualization. It was based on top of `VisPy <http://vispy.org/>`_ and the Qt 6 stack exposed through PySide6 and was distributed under the 3-Clause BSD license. With an on line `documentation <http://visbrain.org>`_, `examples and datasets <http://visbrain.org/auto_examples/>`_ and can also be downloaded from `PyPi <https://pypi.python.org/pypi/visbrain/>`_.

This is not so true nowdays, as time goes by, eons come and go, links phades into history, and in to stories an mythology.

This is a heaviliy AI-based attempt at re-awake this project (as in - first we'll let the ai loose in the system, and then try to fix what it did, if needed), it will take time, and maybe, or even probably, fail. But should it succede, it could be nice.

Modernization roadmap
---------------------

Visbrain is currently undergoing a multi-phase modernization effort. Phase 0
has established the target execution environments and the development workflow
used by contributors while the code base is updated. The detailed plan lives in
``docs/modernization/phase-0.rst`` within the repository.

For day-to-day development work on this modernization track we recommend
either opening the repository in the provided development container or
creating a virtual environment that matches the Phase 0 baseline:

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

These pins align with Python 3.9–3.12 on Windows, macOS, and Linux and will be
revisited during the packaging overhaul in Phase 1.

With the toolchain installed, ``tox`` orchestrates the main contributor
workflows:

.. code-block:: console

   tox -e lint     # run Ruff
   tox -e tests    # run the pytest suite headlessly
   tox -e package  # build sdist/wheel artifacts

The ``Makefile`` exposes matching shortcuts (``make lint``, ``make test`` and
``make build_dist``) for projects that rely on the historical targets.

Important links
---------------

* Official source code repository : https://github.com/EtienneCmb/visbrain
* Online documentation : http://visbrain.org
* Visbrain `chat room <https://gitter.im/visbrain-python/chatroom?utm_source=share-link&utm_medium=link&utm_campaign=share-link>`_


Installation
------------

Dependencies
++++++++++++

Visbrain requires :

* NumPy >= 1.26.4
* SciPy >= 1.11.4
* VisPy >= 0.13.0
* Matplotlib >= 3.8.4
* PySide6 >= 6.7.1 (preferred Qt binding; installs ``shiboken6`` automatically)
* Pillow >= 10.3.0
* PyOpenGL >= 3.1.7

User installation
+++++++++++++++++

Install Visbrain :

.. code-block:: console

    pip install -U visbrain

Sample data and optional downloads
+++++++++++++++++++++++++++++++++

The Visbrain wheel bundles small reference datasets so common workflows run
offline: core brain templates, ROI atlases, an EEG montage and a short
hypnogram are available through ``visbrain.io.path_to_visbrain_data`` without
creating ``~/visbrain_data``. Heavier assets (extended sleep recordings, large
surface meshes, etc.) stay optional and are fetched explicitly with the
``visbrain.io.download`` helper::

    python -m visbrain.io.download --list
    python -m visbrain.io.download sleep_rec.zip --type example_data

Downloads land in a platform-specific cache or the location configured via the
``VISBRAIN_DATA_DIR`` environment variable. The command exposes ``--dest`` and
``--use-pwd`` switches to override the target directory when integrating with
project-specific storage.

