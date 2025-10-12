Phase 3 — macOS GUI life signs
==============================

Goal
----

Bring the regenerated Qt 6 stack to a point where the Visbrain GUIs open on
modern macOS releases (Intel and Apple Silicon) without crashing, showing a
working window and drawing the default scenes. Success is defined as launching
the Brain, Signal, Sleep and Figure façades on macOS 12+ with an accelerated
OpenGL/Metal backend and no fatal Qt warnings.

Milestone outcomes
------------------

* ``python -m visbrain`` reports a viable VisPy backend and the GUI façades
  launch on macOS without manual backend overrides.【F:visbrain/__main__.py†L10-L73】【F:visbrain/config.py†L382-L413】
* VisPy canvases render through Qt 6 on Metal-backed GPUs without shader
  compilation errors or context initialisation failures.【F:visbrain/objects/scene_obj.py†L87-L146】【F:visbrain/gui/brain/interface/ui_init.py†L134-L173】
* Module controllers and shortcuts wire up using the regenerated PySide6
  bindings with no PyQt5 compatibility shims required.【F:visbrain/qt.py†L1-L118】【F:visbrain/_pyqt_module.py†L1-L140】

Task matrix
-----------

Environment and dependency audit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Validate the macOS wheels for the GUI stack by pinning supported binaries in
  ``pyproject.toml`` (PySide6, shiboken6, vispy, PyOpenGL) and documenting any
  universal2 requirements or Rosetta fallbacks.【F:pyproject.toml†L1-L65】
* Exercise ``python -m visbrain info`` on macOS Intel and arm64 hosts to confirm
  the diagnostics capture Metal-backed OpenGL availability and surface useful
  remediation guidance when the context is missing.【F:visbrain/__main__.py†L10-L84】【F:visbrain/config.py†L382-L413】
* Extend the requirements notes to cover Xcode command-line tools and the
  ``QT_QPA_PLATFORM=xcb`` avoidance needed on macOS so contributors can prepare
  machines before running the façades.【F:docs/development.rst†L1-L160】

Qt/VisPy bootstrap fixes
^^^^^^^^^^^^^^^^^^^^^^^^

* Drop the legacy PyQt5 fallback from ``visbrain.qt`` and require PySide6 so the
  Qt namespace matches Qt 6 behaviour across macOS builds.【F:visbrain/qt.py†L1-L118】
* Update ``guard_qapp_lifecycle`` and the Qt application helpers so they no
  longer rely on stub bindings, ensuring ``_PyQtModule.show()`` can request and
  hold a single ``QApplication`` on macOS without double-instantiation
  warnings.【F:visbrain/_pyqt_module.py†L1-L120】
* Ensure ``VisbrainConfig.apply_headless_backend_policy()`` prefers the Qt/VisPy
  combination that maps to the macOS Metal backend (``pyqt6``/``pyside6`` +
  ``vispy.app.backends.qt6``) and downgrade gracefully when the platform lacks a
  hardware OpenGL layer.【F:visbrain/config.py†L398-L513】

Canvas lifecycle and retina support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Refactor ``VisbrainCanvas`` to build canvases through
  ``visbrain.visuals.context`` so the lazy ``ensure_vispy_app()`` guard executes
  before constructing ``SceneCanvas`` instances, preventing "no GL context"
  errors on macOS.【F:visbrain/objects/scene_obj.py†L63-L158】【F:visbrain/visuals/context.py†L17-L120】
* Audit the canvas creation flags (size, dpi, fullscreen) used by the Brain and
  Signal GUIs so windows honour macOS retina scaling and avoid forcing
  ``fullscreen=True`` during initialisation, which currently produces empty
  windows under Metal.【F:visbrain/gui/brain/interface/ui_init.py†L134-L173】【F:visbrain/gui/signal/ui_elements/ui_init.py†L155-L199】
* Route all canvas parenting through Qt's ``createWindowContainer`` equivalents
  when embedding VisPy widgets so focus traversal and accessibility metadata map
  correctly to Cocoa widgets.【F:visbrain/gui/brain/interface/ui_init.py†L134-L200】

Visual modernisation for Metal compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Replace the custom GLSL 1.20 shaders in ``BrainVisual`` with VisPy's
  ``MeshVisual`` (or a modern ``gloo`` program targeting GLSL 3.30+) to satisfy
  the Metal backend's shader compiler. The current ``#version 120`` programs fail
  to compile on macOS Ventura and newer.【F:visbrain/visuals/brain_visual.py†L22-L153】
* Apply the same shader refresh to the grid, hypnogram and picture visuals so
  they use VisPy scene graph primitives or Metal-compatible shaders instead of
  ported ``gloo`` examples that rely on deprecated features.【F:visbrain/visuals/grid_signal_visual.py†L19-L152】【F:visbrain/visuals/hypno_visual.py†L20-L160】【F:visbrain/visuals/pic_visual.py†L1-L160】
* Introduce automated diagnostics that probe shader compilation for each visual
  when running on Metal, capturing meaningful errors before the GUI shows a blank
  canvas.【F:visbrain/config.py†L382-L413】

GUI shell stabilisation
^^^^^^^^^^^^^^^^^^^^^^^

* Verify that module controllers (Brain, Signal, Sleep, Figure) initialise their
  VisPy canvases only after the Qt window is shown, deferring expensive GPU work
  until macOS has attached a NSOpenGLContext. This requires auditing the façade
  constructors that currently create canvases in ``__init__`` without checking
  visibility flags.【F:visbrain/gui/brain/brain.py†L63-L134】【F:visbrain/gui/signal/ui_elements/ui_init.py†L130-L200】
* Replace direct event bindings that depend on ``vispy.app.canvas.MouseEvent``
  with the scene event dispatcher exposed by VisPy 0.13 so the handlers remain
  stable across Qt backends and Metal gesture support.【F:visbrain/gui/brain/tests/test_brain.py†L7-L124】
* Audit shortcuts registered through ``BrainShortcuts`` and similar helpers to
  ensure they do not depend on deprecated key names or modifiers that changed in
  Qt 6 (for example, ``CTRL`` vs ``Qt.ControlModifier`` on macOS).【F:visbrain/gui/brain/interface/ui_init.py†L16-L76】

Testing and diagnostics
^^^^^^^^^^^^^^^^^^^^^^^

* Extend the OpenGL diagnostics pytest suite to exercise the macOS backend,
  mocking Metal availability so failures surface as actionable guidance instead
  of cryptic import errors.【F:visbrain/tests/test_opengl_diagnostics.py†L89-L305】
* Add headless smoke tests that instantiate each façade with ``VISBRAIN_SHOW_GUI``
  disabled but still create canvases, ensuring ``ensure_vispy_app()`` works under
  the macOS CI builder (GitHub Actions macOS-14 runners).【F:visbrain/config.py†L719-L839】【F:visbrain/gui/tests/_screenshot.py†L151-L486】
* Capture manual QA steps for Apple Silicon (native and under Rosetta) so
  contributors can reproduce the "life signs" milestone locally before the full
  feature parity push.【F:docs/modernization/phase-3-inventory.rst†L1-L190】

Documentation and support material
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Document the macOS setup path in the contributor guide, including Homebrew
  recipes for Python, Qt platform plugins, and troubleshooting steps for Metal
  validation failures reported by ``visbrain config`` diagnostics.【F:docs/development.rst†L1-L160】【F:visbrain/config.py†L382-L413】
* Update the modernization roadmap index to point to this milestone so future
  phases can build on the macOS bring-up plan.【F:docs/modernization/index.rst†L1-L17】
* Prepare support snippets (FAQ entries or release notes) explaining the removal
  of PyQt5 support and the requirement for Metal-compatible GPUs on macOS 12+.
  This should cover fallbacks for users stuck on legacy hardware.【F:visbrain/qt.py†L1-L118】【F:visbrain/__main__.py†L10-L84】
