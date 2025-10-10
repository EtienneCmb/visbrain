Development workflow
====================

Qt interface regeneration
-------------------------

The Brain, Sleep, Signal, and Figure GUIs rely on Qt Designer assets stored
under ``visbrain/gui/*/interface``.  After adjusting a ``.ui`` file in any of
those modules, regenerate the corresponding Python wrappers with::

   make qt-ui

The command wraps :mod:`PySide6`'s ``pyside6-uic`` and ``pyside6-rcc`` tools and
touches every generated module under ``visbrain/gui/*/interface``.  Continuous
integration now executes ``python tools/generate_qt_ui.py --check`` as part of
:command:`make flake`, so linting fails whenever committed artifacts are
stale.  Run ``make qt-ui`` immediately after editing Qt resources and then
re-run ``make flake`` to verify that everything is up to date before sending a
pull request.

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


Screenshot regression suite
---------------------------

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

Regenerate the images locally with::

   VISBRAIN_UPDATE_SCREENSHOTS=1 pytest -m screenshot

New screenshots should be documented in this list so reviewers understand which
component each baseline represents.
