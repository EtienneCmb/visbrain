Visbrain documentation
======================

.. badges::
   :columns: 3

   .. badge:: CI
      :image: https://github.com/EtienneCmb/visbrain/actions/workflows/ci.yml/badge.svg?branch=master
      :target: https://github.com/EtienneCmb/visbrain/actions/workflows/ci.yml

   .. badge:: Wheels
      :image: https://github.com/EtienneCmb/visbrain/actions/workflows/wheels.yml/badge.svg?branch=master
      :target: https://github.com/EtienneCmb/visbrain/actions/workflows/wheels.yml

   .. badge:: Coverage
      :image: https://codecov.io/gh/EtienneCmb/visbrain/branch/master/graph/badge.svg
      :target: https://codecov.io/gh/EtienneCmb/visbrain

   .. badge:: PyPI
      :image: https://badge.fury.io/py/visbrain.svg
      :target: https://badge.fury.io/py/visbrain

   .. badge:: Downloads
      :image: https://pepy.tech/badge/visbrain
      :target: https://pepy.tech/project/visbrain

   .. badge:: Community chat
      :image: https://badges.gitter.im/visbrain-python/chatroom.svg
      :target: https://gitter.im/visbrain-python/chatroom?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge

Visbrain is a GPU-accelerated suite for visualising brain signals, anatomical
surfaces and advanced electrophysiology. The documentation gathers installation
guides, tutorials, runnable examples and contributor roadmaps so you can explore
the project from multiple entry points.

Key pathways
------------

.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: Install Visbrain
      :link: introduction
      :link-type: doc
      :class-card: sd-text-center sd-shadow-sm

      Follow platform-specific instructions, dependency notes and optional data
      downloads to configure the toolkit for local development or production
      deployments.

   .. grid-item-card:: Tutorials & user guide
      :link: documentation
      :link-type: doc
      :class-card: sd-text-center sd-shadow-sm

      Learn each GUI module and object workflow through step-by-step guides and
      reference material bundled with Visbrain.

   .. grid-item-card:: Example gallery
      :link: auto_examples/index
      :link-type: doc
      :class-card: sd-text-center sd-shadow-sm

      Run executable scripts that reproduce the figures featured throughout the
      documentation and demonstrate Visbrain's visualisation primitives.

   .. grid-item-card:: Diagnostics & troubleshooting
      :link: development
      :link-type: doc
      :class-card: sd-text-center sd-shadow-sm

      Inspect health checks, gallery execution tips and the ``python -m visbrain
      info`` report to debug environments and continuous integration builds.

   .. grid-item-card:: Modernization roadmap
      :link: modernization/index
      :link-type: doc
      :class-card: sd-text-center sd-shadow-sm

      Track ongoing architectural work, packaging milestones and the plan for
      future releases across each modernization phase.

Contents
********

.. toctree::
   :caption: Core guides
   :maxdepth: 2

   introduction
   documentation
   auto_examples/index
   development
   modernization/index

.. toctree::
   :caption: Reference
   :maxdepth: 1

   api
   faq
   community
   governance
   release
   citation
