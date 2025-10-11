Phase 5 — Quality automation and CI migration
=============================================

Overview
--------

Phase 5 turns the modernization roadmap toward the quality gates that guard
Visbrain's refactored runtime.  Earlier phases introduced stable APIs and IO
infrastructure; this stage reinforces them by expanding the automated tests,
formalising static analysis, and moving the continuous integration (CI)
pipelines to long-term supported services.  The result is a development loop
that surfaces regressions quickly while keeping the cost of maintenance
predictable.

Expanded test coverage
----------------------

Regression tests now exercise the Qt and VisPy front ends alongside the
numerical layers.  The screenshot workflow documented in :doc:`../development`
anchors determinism checks across the Brain, Signal, Sleep, and Figure GUIs so
rendering changes are reviewed intentionally instead of slipping into releases.
The pytest suite gained focused markers for IO caching, threaded loaders, and
GPU diagnostics, making it easier to balance execution time and coverage across
platform-specific runners.  Contributors can regenerate baselines locally and
share them through reviews, keeping front-end behaviour visible to the entire
team.

Static analysis upgrades
------------------------

Phase 5 standardises the :mod:`pre_commit` automation described in
:doc:`../development` so every push receives the same Ruff, Black, MyPy, and
packaging validations that CI enforces.  Repository metadata captures the hook
configuration, and ``pre-commit run --all-files`` is promoted as the canonical
way to audit large refactors.  The static analysis footprint now matches the
runtime's supported Python versions, eliminating drift between local
environments and the shared infrastructure.

Continuous integration migration
--------------------------------

The legacy CI matrix moved onto a unified provider with native support for the
new test markers, screenshot artefact uploads, and the packaging smoke tests
wrapped by ``make flake``.  Workflows now cache dependencies per interpreter,
run the :mod:`pre_commit` hooks in parallel with pytest, and publish the
regenerated documentation previews to unblock reviewer feedback.  The migration
also consolidated credentials management so nightly builds, wheel publishing,
and documentation deployment all reuse the same secret storage policies.

Rollout checkpoints
-------------------

* Track new GUI features by extending the screenshot regression list so changes
  stay auditable in source control.
* Expand platform coverage in pytest markers and update the release checklist
  when critical paths gain deterministic tests.
* Keep CI job definitions aligned with the shared ``Makefile`` targets so local
  and hosted automation evolve together.
