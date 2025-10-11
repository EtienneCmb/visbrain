.. _Release:

Changelog
=========

.. contents:: Contents
   :local:
   :depth: 1

Automation
----------

The continuous integration and release checks now run through GitHub Actions.
The :doc:`development <development>` workflow triggers the ``ci`` pipeline
(``.github/workflows/ci.yml``) on every pull request and push to ``master`` to
exercise the lint and test suites across the supported platforms. Publishing a
release tag activates ``wheels`` (``.github/workflows/wheels.yml``), which
builds and verifies the installation artifacts before they land on PyPI. Ensure
both workflows are green before drafting release notes or promoting a build.

Automated changelog
-------------------

Workstream 4 publishes release notes automatically from the aggregated
fragments collected during development. The rendered output is available in the
documentation and mirrored on the GitHub Releases page.

.. toctree::
   :maxdepth: 1

   changelog/index

.. include:: _generated/changelog-latest.rst

Release checklist
-----------------

#. Confirm the ``ci`` workflow succeeds on the release branch or tag by
   checking the `GitHub Actions dashboard <https://github.com/EtienneCmb/visbrain/actions/workflows/ci.yml>`_.
   Rerun failed jobs and address regressions before continuing.
#. Review the automated changelog above and decide on the semantic version
   bump. Follow the `Semantic Versioning specification <https://semver.org/>`_:
   breaking changes require a major version, new features a minor version, and
   fixes only a patch version.
#. Create a signed git tag that matches the chosen version number and push it
   to ``origin``.
#. Monitor the ``wheels`` workflow (`workflow definition <https://github.com/EtienneCmb/visbrain/actions/workflows/wheels.yml>`_)
   to ensure artifacts build successfully for all supported platforms.
#. Download the generated wheels and source distribution from the workflow run,
   verify their SHA256 checksums, and perform a local install test in a clean
   environment before publishing to PyPI.
#. Publish the release on GitHub, attach the validated artifacts if needed, and
   notify the community channels.
