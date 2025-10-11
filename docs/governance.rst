.. _governance:

===========
Governance
===========

Visbrain's modernization programme is coordinated by a small Maintainers group
that steers both the technical roadmap and the community processes needed to
deliver stable releases. The goals of the current governance model are to keep
decision making transparent, ensure the scientific use-cases remain front and
centre, and provide clear escalation paths when contributors need support.

Roles and responsibilities
==========================

Maintainers
-----------

Maintainers act as the final reviewers for architectural changes, release
planning, and roadmap updates. They:

* Triage issues and pull requests to keep the backlog healthy.
* Approve or reject changes that alter the supported platforms, dependency
  stack, or public APIs.
* Nominate release coordinators and track milestones for each modernization
  phase.

Release coordinators
--------------------

Each roadmap phase appoints a release coordinator who focuses on day-to-day
execution. Coordinators:

* Drive the feature work needed for the active phase and keep the milestone
  burndown visible to the community.
* Verify that automation (CI, documentation, and packaging) stays green.
* Prepare release notes and publish artefacts to PyPI and ``conda-forge`` once
  Maintainers sign off.

Working groups
--------------

Module experts form ad-hoc working groups—Brain, Sleep, Signal, Figure, IO, and
infrastructure—to give focused feedback on changes that affect their areas.
Working groups self-organise but are expected to:

* Keep their module documentation and examples accurate.
* Surface breaking changes early so the Maintainers can adjust the modernization
  roadmap when necessary.
* Mentor new contributors as they onboard.

Decision making
===============

We favour consensus in GitHub discussions and pull requests. When agreement
cannot be reached, Maintainers make a final call after weighing the documented
use-cases and technical trade-offs. Major or cross-cutting proposals should
start with an issue labelled ``RFC`` so that the wider community has at least
one review cycle (roughly a week) to comment before the changes are implemented.

Meetings are optional; updates flow primarily through asynchronous channels so
contributors across time zones can participate. When synchronous coordination is
helpful, notes are published in the associated issue or discussion for posterity.

Community interaction
=====================

Visbrain uses GitHub Discussions and the historical Gitter rooms for general
questions. Code of Conduct violations or other urgent concerns can be reported
privately to any Maintainer via email or GitHub direct message. The maintainers
commit to acknowledge reports within three working days and document the
resolution approach once the parties involved are comfortable sharing the
outcome.

Updating this document
======================

Governance documentation evolves alongside the modernization roadmap. Proposed
changes should arrive as pull requests tagged with ``governance`` so reviewers
can confirm the new expectations with the Maintainers group before merging.
