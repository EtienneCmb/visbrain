Phase 4 — IO resilience and diagnostics hardening
=================================================

Overview
--------

Phase 4 consolidates the lower-level infrastructure that keeps Visbrain
responsive while it moves larger assets around.  The focus is on the IO stack,
which now exposes thread-safe primitives for loading data in the background,
normalised cache management so temporary artefacts stay contained, and GPU
probing utilities that spot unsupported environments before a rendering failure
occurs.  These foundations land before the packaging refresh so teams can rely
on predictable directories, failure-handling semantics and diagnostics when
shipping the regenerated Qt interfaces from Phase 3.

IO service upgrades
-------------------

The :mod:`visbrain.io.background` helpers wrap a single shared
:class:`~concurrent.futures.ThreadPoolExecutor` that controllers use when they
need to move blocking work off the GUI thread.  ``run_in_loader_thread`` submits
callables to the pool while honouring the ``VISBRAIN_BACKGROUND_WORKERS``
environment toggle, and ``call_on_main_thread`` marshals callbacks back to Qt's
GUI thread.  Consumers such as :class:`~visbrain.gui.sleep.controller.SleepController`
rely on :class:`~visbrain.gui.sleep.loader.AsyncSleepLoader` to feed the sleep
viewer without freezing its controls, registering completion callbacks that
hydrate the models via :func:`visbrain.gui.threading.invoke_in_gui_thread`.

The background layer formalises the dialog contract as well: the loaders hand
results back to the GUI thread so :mod:`visbrain.io.dialog` can safely open
native file pickers from worker callbacks.  The Qt-aware ``invoke_in_gui_thread``
wrapper enforces this policy across all controllers so even ad-hoc dialogs
opened from futures run on the correct thread.

Cache management
----------------

The new :class:`visbrain.io.cache.CacheManager` anchors all writable state under
platform-specific directories exposed by :mod:`visbrain.io.path`.  ``tmp``
entries live under a session-specific namespace while durable ``data`` artefacts
share the ``VISBRAIN_DATA_DIR`` hierarchy.  ``CacheManager`` tracks ownership to
make bulk cleanup predictable via ``cleanup_owner`` and exposes
``root_path``/``get_path`` helpers so call sites can create scoped subdirectories
without replicating platform heuristics.  ``path_to_visbrain_data`` now routes
writes through the manager which keeps bundled resources separate from mutable
content.

GPU diagnostics
---------------

``python -m visbrain info`` surfaces the VisPy/OpenGL diagnostics introduced in
:mod:`visbrain.config`.  The CLI emits structured JSON for automation or a
human-friendly report that highlights the resolved backend, GL limits, shader
status and any headless fallback attempts.  Configuration objects keep the raw
payload via ``vispy_diagnostics_payload`` so GUI front-ends can present the
same guidance when a context fails to initialise.

Rollout checkpoints
-------------------

* Audit controllers that still spin up bespoke worker threads and migrate them
  to :mod:`visbrain.io.background` so loader shutdown remains centralised.
* Update dataset downloaders and exporters to register cache ownership before
  writing temporary files, allowing ``cache_manager.cleanup_owner`` to free
  space after tests and demos finish.
* Extend contributor documentation with diagnostics triage steps so QA teams can
  capture ``python -m visbrain info --json`` in bug reports alongside the
  ``visbrain.config`` payload.
* Ship gallery examples that exercise ``SleepController.load_dataset_async`` and
  include GPU diagnostics in their narratives, ensuring the runtime checks land
  alongside the regenerated Qt 6 widgets from Phase 3.
