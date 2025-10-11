"""
Matplotlib plot of an hypnogram
===============================

Plot a hypnogram using matplotlib.
"""

from visbrain.io import write_fig_hyp, read_hypno, download_file

###############################################################################
# Plotting properties
###############################################################################
# Define plotting properties

grid = True     # display the grid
ascolor = True  # plt as color or in black and white

###############################################################################
# Hypnogram data
###############################################################################
# For the illustration, a hypnogram is downloaded

path_to_hypno = download_file("s101_jbe.hyp", astype='example_data',
                               allow_download=True)
data, sf = read_hypno(path_to_hypno)

###############################################################################
# Plot the hypnogram
###############################################################################
# Plot the hypnogram. If file is None, the window is displayed otherwise the
# figure is saved


def _build_example():
    fig = write_fig_hyp(data, sf, grid=grid, ascolor=ascolor, file=None,
                        show=False)

    def _save(path: str) -> None:
        write_fig_hyp(data, sf, grid=grid, ascolor=ascolor, file=path,
                      show=False)

    setattr(fig, "_example_save", _save)
    return fig


if __name__ == "__main__":
    from visbrain.examples._runner import run_example

    raise SystemExit(run_example(_build_example))
