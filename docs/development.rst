Development workflow
====================

Tooling setup
-------------

Install the shared development toolchain before running any of the
automation described below::

   python -m pip install -r requirements/dev.txt

When authoring documentation, install the optional Sphinx toolchain with
either::

   python -m pip install .[docs]

or::

   python -m pip install -r requirements/docs.txt

Build the HTML preview with::

   tox -e docs

Continuous documentation publishing
-----------------------------------

Pull requests and pushes to the ``main`` branch execute the
``.github/workflows/docs.yml`` automation.  The job provisions Python 3.11,
installs the project with the ``.[docs]`` extras, and runs ``tox -e docs`` to
build the Sphinx HTML output.  Reviewers can download a ``docs-html`` artifact
on pull requests to preview the rendered site before merging.  Successful builds
on ``main`` upload the HTML bundle through ``actions/deploy-pages`` so GitHub
Pages stays in sync with the latest default-branch state.

See the `Documentation workflow`_ for the full job definition and a direct link
to the HTML artifacts that GitHub Actions uploads on every run.

The workflow relies on the repository ``GITHUB_TOKEN`` (also available as
``GH_TOKEN``) with ``contents: read`` and ``pages: write`` permissions to push
the published site.  Forks without Pages enabled can either disable the deploy
job or provide a personal access token with the same scopes via the
``GH_TOKEN`` secret.

Documentation troubleshooting
-----------------------------

Nitpicky references
~~~~~~~~~~~~~~~~~~~

The Sphinx configuration enables ``nitpicky = True`` so unresolved cross
references fail the build.  When ``tox -e docs`` reports ``nitpicky`` errors,
first confirm that the role target is spelled correctly and available in the
referenced package's inventory.  Use ``python -m sphinx.ext.intersphinx
<object-inventory>`` to inspect cached inventories under ``docs/_build``.  If
the reference intentionally points to a name that Sphinx cannot resolve (for
example, Qt types exposed only at runtime), add an entry to the
``nitpick_ignore`` list in ``docs/conf.py`` to silence the warning for that
identifier.

Gallery execution failures
~~~~~~~~~~~~~~~~~~~~~~~~~~

Gallery examples execute as part of ``tox -e docs``.  Failures usually indicate
missing optional dependencies or a GUI trying to open in a headless
environment.  Confirm that ``pip install .[docs]`` completed successfully and
re-run the builder with ``VISBRAIN_SHOW_GUI=0 QT_QPA_PLATFORM=offscreen tox -e
docs`` to force headless rendering.  Individual examples can be debugged by
invoking the generated script from ``docs/auto_examples`` with
``--visbrain-show=False`` to match the gallery runtime behaviour.

.. _Documentation workflow: https://github.com/EtienneCmb/visbrain/actions/workflows/docs.yml

Pre-commit workflow
-------------------

The repository uses :mod:`pre_commit` to run Ruff, Black, MyPy, end-of-file
fixes, and a packaging smoke test. Install the git hook locally so changes are
validated automatically::

   pre-commit install

Invoke the checks manually when rebasing or editing historic commits::

   pre-commit run --all-files

Hook execution mirrors the ``tox -e lint`` and ``tox -e lint-format`` targets,
so keeping the hook active ensures that the CI style jobs stay green. Run
``pre-commit run --all-files`` before pushing when you edit code outside the
usual workflow or after an interactive rebase.

Tox environments
----------------

``tox`` drives the canonical automation entry points. The most common
environments are:

* ``lint`` – runs Ruff in linting mode.
* ``lint-format`` – enforces the Ruff/Black formatting profile.
* ``type`` – executes MyPy with the repository configuration.
* ``tests`` – launches the headless pytest suite.
* ``docs`` – builds the Sphinx documentation with warnings treated as errors.
* ``tests-gui`` – runs the GUI-focused pytest markers that require an X server
  (the CI container provisions Xvfb automatically).
* ``tests-screenshot`` – executes the deterministic screenshot comparisons.
* ``package`` – builds the source distribution and wheel artefacts.

``tox`` is the supported entry point for these tasks; legacy Makefile targets
remain available but are no longer documented.

Qt interface regeneration
-------------------------

The Brain, Sleep, Signal, and Figure GUIs rely on Qt Designer assets stored
under ``visbrain/gui/*/interface``.  After adjusting a ``.ui`` file in any of
those modules, regenerate the corresponding Python wrappers with::

   python -m tools.generate_qt_ui

The command wraps :mod:`PySide6`'s ``pyside6-uic`` and ``pyside6-rcc`` tools and
touches every generated module under ``visbrain/gui/*/interface``.  Continuous
integration now executes ``python tools/generate_qt_ui.py --check`` inside
``tox -e lint``, so linting fails whenever committed artifacts are stale.  Run
``python -m tools.generate_qt_ui`` immediately after editing Qt resources and
then re-run ``tox -e lint`` to verify that everything is up to date before
sending a pull request.

Background loading service
--------------------------

Controllers that perform blocking IO must dispatch the work to the shared
loader executor exposed by :mod:`visbrain.io.background`.  Submit callables via
``run_in_loader_thread`` (or the higher level
:class:`~visbrain.gui.sleep.loader.AsyncSleepLoader`) and attach completion
callbacks that push the results back to the GUI thread with
:func:`visbrain.gui.threading.invoke_in_gui_thread`.  The executor honours the
``VISBRAIN_BACKGROUND_WORKERS`` environment toggle, so test suites can disable
threads deterministically.  Always call ``shutdown_loader_threads`` when your
controller is torn down to avoid dangling workers.

Dialog threading contract
-------------------------

Qt dialogs opened from background callbacks must cross back to the GUI thread.
Use :func:`visbrain.gui.threading.invoke_in_gui_thread` or
``visbrain.io.background.call_on_main_thread`` before invoking
``QtWidgets.QFileDialog`` helpers.  :mod:`visbrain.io.dialog` already wraps the
Qt APIs and should be preferred over hand-rolled dialogs because it performs
the thread hop automatically and falls back to synchronous behaviour when Qt is
unavailable.  Bypassing these wrappers risks deadlocks when futures complete
while the main event loop is busy.

Cache directory conventions
---------------------------

Writable artefacts now flow through :class:`visbrain.io.cache.CacheManager`
which is initialised in :mod:`visbrain.io.path`.  ``cache_manager.get_path``
creates namespaced directories under two categories:

* ``data`` — durable assets stored alongside bundled datasets.  The root
  follows the ``VISBRAIN_DATA_DIR`` override or the platform defaults (``%APPDATA%/Visbrain`` on
  Windows, ``~/Library/Application Support/Visbrain`` on macOS and
  ``~/.local/share/visbrain`` on Linux).
* ``tmp`` — short-lived scratch space.  Allocate per-session directories with
  ``cache_manager.new_session`` and release them via ``cleanup_owner`` when the
  operation completes.

Utilities such as ``path_to_visbrain_data`` and the download CLI already use
these helpers; new code should avoid hard-coding paths so clean-up policies
remain centralised.


Screenshot regression harness
-----------------------------

The automated screenshot comparisons under
``visbrain/gui/tests/test_regressions.py`` verify that the Qt and VisPy front
ends render deterministically. Baseline PNGs live in
``visbrain/gui/tests/baseline`` and should be treated as fixtures:

* ``brain.png`` — the full Brain GUI.
* ``signal.png`` — the Signal GUI waveform browser.
* ``sleep.png`` — the Sleep scoring interface.
* ``brain-visual-canvas.png`` — a minimal :class:`~visbrain.visuals.brain_visual.BrainVisual`
  hosted in a :class:`~visbrain.objects.scene_obj.VisbrainCanvas` scene.
* ``figure.png`` — the matplotlib-backed Figure GUI.

Run the harness through ``tox`` during feature development::

   tox -e tests-screenshot

Regenerate the images locally with::

   VISBRAIN_UPDATE_SCREENSHOTS=1 tox -e tests-screenshot

New screenshots should be documented in this list so reviewers understand which
component each baseline represents and committed alongside the code that
changes the visuals.
