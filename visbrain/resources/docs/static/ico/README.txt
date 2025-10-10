This directory should contain the Visbrain logo PNGs and favicon used by the
Sphinx documentation. The binary assets are not tracked in the repository to
keep the Git history text-only; copy the following files into this folder when
building the docs locally:

- visbrain.png
- visbrain_128x128.png
- favicon.ico
- brain_ico.png
- figure_ico.png
- signal_ico.png
- sleep_ico.png

The documentation configuration resolves these files from the package's static
resources via ``visbrain.resources.docs``.
