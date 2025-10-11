"""
Basic configuration
===================

This example demonstrate how to open Sleep.

Two windows will then appear :

* The first one ask a proper dataset (required)
* The second one ask for an hypnogram (optional). If None, an empty one is used

.. image:: ../../_static/examples/ex_basic_sleep.png
"""
from visbrain.gui import Sleep


def _build_example():
    return Sleep()


if __name__ == "__main__":
    from visbrain.examples._runner import run_example

    raise SystemExit(run_example(_build_example))
