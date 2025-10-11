Phase 6 — Release automation and distribution hardening
=======================================================

Overview
--------

Phase 6 connects the modernization roadmap to repeatable releases.  The
refactored codebase now ships through automation that codifies versioning
policy, packaging validation, and artifact publication.  This stage emphasises
keeping contributors in sync with the release machinery so runtime upgrades can
ship safely on the expanded CI matrix.

Goals
-----

* Complete the release automation milestones introduced in
  :doc:`../release`, including consistent changelog generation and signature
  verification.
* Formalise distribution checklists around ``make release`` so core maintainers
  can promote artifacts without manual scripting.
* Document the support boundaries for Python versions, Qt bindings, and GPU
  stacks that Phase 5 stabilised, ensuring downstream packagers inherit the same
  expectations.

Key tasks
---------

* Move the automated changelog into the standard release pipeline so each
  tagged build synchronises documentation and GitHub Releases output.
* Expand the :doc:`../development` guide with wheel validation examples and
  pointers to the packaging smoke tests executed in CI.
* Gate release tags on a green :doc:`../release` checklist outcome by
  integrating status badges and release candidate dry runs.

Status
------

The release automation workflows now mirror the modernization targets for
quality, but final validation relies on broader community testing.  Maintainers
are drafting the wheel verification scripts and adapting the distribution
checklist while the automation lands.  Follow the ``phase-6`` label in the issue
tracker for real-time updates and to help triage packaging regressions that
surface during release candidate cycles.
