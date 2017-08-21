"""Export graphical components as figures.

- write_fig_hyp : Export the hypnogram as a figure
- write_fig_canvas : Export a canvas as a figure
- write_fig_pyqt : Export a GUI window as a figure
"""
import numpy as np


__all__ = ('write_fig_hyp', 'write_fig_canvas', 'write_fig_pyqt')


def write_fig_hyp(file, hypno, sf, tstartsec, grid=False, ascolor=False,
                  colors={-1: '#8bbf56', 0: '#56bf8b', 1: '#aabcce',
                          2: '#405c79', 3: '#0b1c2c', 4: '#bf5656'}):
    """Export hypnogram to a 600 dpi png figure.

    Parameters
    ----------
    file : str
        Filename (with full path) to sleep dataset.
    hypno : array_like
        Hypnogram vector
    sf  : float | 100.
        The sampling frequency of displayed elements (could be the
        down-sampling frequency)
    tstartsec: int
        Record starting time given in seconds.
    grid : boolean, optional (def False)
        Plot X and Y grid.
    """
    import matplotlib.pyplot as plt
    import datetime

    # Downsample to get one value per second
    sf = int(sf)
    hypno = hypno[::sf]

    # Put REM between Wake and N1 sleep
    hypno[hypno >= 1] += 1
    hypno[hypno == 5] = 1
    idx_rem = np.where(hypno == 1)[0]
    val_rem = np.zeros(hypno.size)
    val_rem[:] = np.nan
    val_rem[idx_rem] = 1

    # Find if artefacts are present in hypno
    art = True if -1 in hypno else False

    # Start plotting
    fig, ax = plt.subplots(figsize=(10, 4), edgecolor='k')
    lhyp = len(hypno) / 60
    lw = 1.5
    if lhyp < 60:
        xticks = np.arange(0, len(hypno), 10 * 60)
        lw = 2
    elif lhyp < 180 and lhyp > 60:
        xticks = np.arange(0, len(hypno), 30 * 60)
    else:
        xticks = np.arange(0, len(hypno), 60 * 60)

    xticks = np.append(xticks, len(hypno))
    xlabels = (xticks + tstartsec).astype(int)
    xlabels_str = [str(datetime.timedelta(seconds=int(j)))[:-3]
                   for i, j in enumerate(xlabels)]
    xlabels_str = [s.replace('1 day, ', '') for s in xlabels_str]
    plt.xlim(0, len(hypno))
    plt.xticks(xticks, xlabels_str)
    if not ascolor:
        plt.plot(hypno, 'k', ls='steps', linewidth=lw)
    else:
        for k, i in colors.items():
            # Quick and dirty switch :
            if k == 1:
                q = 2
            elif k == 4:
                q = 1
            elif k in [2, 3]:
                q = k + 1
            else:
                q = k
            mask = np.ones((len(hypno),), dtype=bool)
            idxm = np.where(hypno == q)[0] + 1
            idxm[idxm >= len(hypno)] = len(hypno) - 1
            mask[idxm] = False
            plt.plot(np.ma.masked_array(hypno, mask=mask), i, linewidth=lw)

    # Plot REM epochs
    remcol = 'k' if not ascolor else colors[4]
    for i in np.arange(0.6, 1, 0.01):
        plt.plot(np.arange(len(hypno)), i * val_rem, remcol, linewidth=lw)

    # Y-Ticks and Labels
    if art:
        ylabels = ['Art', 'Wake', 'REM', 'N1', 'N2', 'N3']
        plt.yticks([-1, 0, 1, 2, 3, 4], ylabels)
        plt.ylim(-1.5, 4.5)
    else:
        ylabels = ['', 'Wake', 'REM', 'N1', 'N2', 'N3']
        plt.yticks([-0.5, 0, 1, 2, 3, 4], ylabels)
        plt.ylim(-.5, 4.5)

    # X-Ticks and Labels
    plt.xlabel("Time")
    plt.ylabel("Sleep Stage")

    # Grid
    if grid:
        plt.grid(True, 'major', ls=':', lw=.2, c='k', alpha=.3)

    plt.tick_params(axis='both', which='both', bottom='on', top='off',
                    labelbottom='on', left='on', right='off', labelleft='on',
                    labelcolor='k', direction='out')

    # Invert Y axis and despine
    ax.invert_yaxis()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    ax.spines['left'].set_position(('outward', 10))
    ax.spines['bottom'].set_position(('outward', 10))
    ax.spines['bottom'].set_smart_bounds(True)

    # Save as 600 dpi .png
    plt.savefig(file, format='png', dpi=600, bbox_inches='tight')


def write_fig_canvas(filename, canvas, resolution=3000, autocrop=False,
                     region=None):
    """Export a canvas as a figure.

    Parameters
    ----------
    filename : string
        Name of the figure to export.
    canvas : VisPy canvas
        The vispy canvas to export.
    resolution : int | 3000
        Coefficient to multiply the size of the canvas.
    autocrop : bool | False
        Auto-cropping argument to remove useless space.
    region : tuple/list | None
        The region to export.
    """
    from ..utils import piccrop
    import vispy

    # Manage size exportation. The dpi option present when creating a
    # vispy canvas doesn't seems to work. The trick bellow increase the
    # physical size of the canvas so that the exported figure has a
    # high-definition :
    # Get a copy of the actual canvas physical size :
    backp_size = canvas.physical_size

    # Increase the physical size :
    ratio = max((2 * resolution) / backp_size[0], resolution / backp_size[1])
    new_size = (int(backp_size[0] * ratio), int(backp_size[1] * ratio))
    canvas._backend._physical_size = new_size

    # Render and save :
    if region is not None:
        kwargs = {'region': region}
    else:
        kwargs = {'size': new_size}
    img = canvas.render(**kwargs)
    if autocrop:
        img = piccrop(img)
    vispy.io.imsave(filename, img)

    # Set to the canvas it's previous size :
    canvas._backend._physical_size = backp_size


def write_fig_pyqt(self, filename):
    """Export a GUI window as a figure.

    Parameters
    ----------
    self : struct
        The self structure of the GUI window.
    filename : string
        The picture file name.
    """
    from PyQt5 import QtWidgets, QtCore

    # Screnshot function :
    def _take_screenshot():
        """Take the screenshot."""
        screen = QtWidgets.QApplication.primaryScreen()
        p = screen.grabWindow(0)
        p.save(filename)
    # Take screenshot if filename :
    if filename:
        # Timer (avoid shooting the saving window)
        self.timerScreen = QtCore.QTimer()
        # self.timerScreen.setInterval(100)
        self.timerScreen.setSingleShot(True)
        self.timerScreen.timeout.connect(_take_screenshot)
        self.timerScreen.start(500)
