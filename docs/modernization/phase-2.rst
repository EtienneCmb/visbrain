Phase 2 – Runtime configuration cleanup
=======================================

The second phase of the modernization plan focuses on removing import-time
side effects from :mod:`visbrain.config` and codifying the way GUI resources
are created.  Earlier releases built Qt and VisPy application instances as soon
as the module was imported, which complicated headless automation and made it
hard to reason about global state.  The refactor introduces an explicit
``VisbrainConfig`` facade that keeps track of runtime flags and lazy factories
for GUI backends.

Key changes
-----------

* ``VisbrainConfig`` exposes the active Qt backend, Matplotlib render flag and
  any instantiated GUI handles through attributes instead of the previous
  mutable dictionary.
* ``configure_from_environ`` reads ``VISBRAIN_SHOW_GUI`` so automation can flip
  headless mode via environment variables instead of mutating globals.
* ``ensure_qt_app()`` and ``ensure_vispy_app()`` lazily create GUI
  applications.  Both respect the ``VisbrainConfig.show_pyqt_app`` flag so tests
  run headless by default while still allowing opt-in GUI execution via the
  ``force`` argument.
* ``configure_from_argv(argv, config=...)`` replaces the import-side CLI parser.  The new
  function accepts an explicit argument vector and returns the updated config
  object so entry points can opt in to CLI overrides without polluting module
  import.
* ``parse_cli`` and ``init_config`` remain as thin wrappers around
  ``configure_from_argv`` for legacy consumers and now emit a deprecation
  warning.

Running headless
----------------

Test runners and automation harnesses should continue to set
``QT_QPA_PLATFORM=offscreen`` (see :mod:`conftest`) and opt into headless mode
by calling :func:`visbrain.config.configure_headless` or exporting
``VISBRAIN_SHOW_GUI=0``.  The helper only sets a default when the variable is
missing, so local runs can still override it with
``VISBRAIN_SHOW_GUI=1``.  The lazy GUI helpers return ``None`` in headless
mode, so call sites must guard against ``None`` before touching GUI handles.
When a test genuinely needs an application instance it can request it with
``ensure_qt_app(force=True)`` or ``ensure_vispy_app(force=True)``.

CLI integration
---------------

Entry points should no longer rely on :data:`sys.argv` being consumed during
module import.  Instead they should call
``configure_from_argv(sys.argv[1:], config=get_config())`` before bootstrapping
their UI.  The parser now validates GUI-visibility options without mutating the
stored state.  ``configure_from_environ`` can be called ahead of CLI parsing so
deployment scripts can respect ``VISBRAIN_SHOW_GUI`` alongside command line
overrides.

Enabling interactive launches
-----------------------------

Local runs that should always display the GUI can export
``VISBRAIN_SHOW_GUI=1`` before invoking the façade.  The environment variable
continues to update :class:`~visbrain.config.VisbrainConfig` so automated jobs
can default to headless execution while local contributors opt into
interactive windows.

Practical examples
------------------

* Tests that previously patched ``CONFIG['SHOW_PYQT_APP']`` now use
  ``get_config().show_pyqt_app``.
* GUI code should request the Qt and VisPy handles via ``ensure_qt_app()`` and
  ``ensure_vispy_app()`` rather than touching module-level globals.  Both
  helpers are safe to call in headless environments.
* Documentation builders can enable Matplotlib rendering explicitly by setting
  ``get_config().mpl_render = True`` in ``docs/conf.py``.

These changes make the runtime state explicit and defer heavyweight resources
until they are genuinely needed, unlocking deterministic behaviour across both
interactive launches and automated tests.


Sleep module testing strategy
-----------------------------

The Sleep GUI now exposes dedicated pytest fixtures that assemble the
``SleepDataset`` model, ``SleepView`` widget and ``SleepController`` without
launching the top-level façade.  The fixtures generate deterministic synthetic
signals so detection routines, annotation helpers and save/load commands can be
validated in isolation.  An additional ``sleep_facade`` fixture wires the full
stack together with the shared arrays, allowing integration tests to exercise
the MVC boundary while still running against an offscreen Qt configuration.

Controller-focused tests patch Qt slots via ``monkeypatch``/``qtbot`` to assert
that signals are connected instead of calling private helpers directly.  The
integration suite reuses the headless façade to drive detection workflows and
file exports without blocking on the Qt event loop, providing confidence that
the modernization work remains compatible with automated CI environments.

