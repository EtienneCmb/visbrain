"""Export graphical components as figures.

- write_fig_hyp : Export the hypnogram as a figure
- write_fig_canvas : Export a canvas as a figure
- write_fig_pyqt : Export a GUI window as a figure
"""
from os.path import splitext
import numpy as np
from ..utils.color import color2vb


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


def write_fig_canvas(filename, canvas, widget=None, autocrop=False,
                     region=None, print_size=None, unit='centimeter', dpi=300.,
                     factor=1., bgcolor=None, transparent=False):
    """Export a canvas as a figure.

    Parameters
    ----------
    filename : string
        Name of the figure to export.
    canvas : VisPy canvas
        The vispy canvas to export.
    widget : PyQt widget | None
        The widget parent of the canvas.
    autocrop : bool | False
        Auto-cropping argument to remove useless space.
    region : tuple/list | None
        The region to export (x_start, y_start, width, height).
    print_size : tuple | None
        The desired print size. This argument should be used in association
        with the dpi and unit inputs. print_size describe should be a tuple
        of two floats describing (width, height) of the exported image for
        a specific dpi level. The final image might not have the exact
        desired size but will try instead to find a compromize
        regarding to the proportion of width/height of the original image.
    unit : {'centimeter', 'millimeter', 'pixel', 'inch'}
        Unit of the printed size.
    dpi : float | 300.
        Dots per inch for printing the image.
    factor : float | None
        If you don't want to use the print_size input, factor simply
        multiply the resolution of your screen.
    bgcolor : array_like/string | None
        Background color of the canvas.
    transparent : bool | False
        Use transparent background.
    """
    from ..utils import piccrop
    from vispy.io import imsave

    # Get the size of the canvas and backend :
    c_size = canvas.size
    b_size = canvas._backend._physical_size

    # If the GUI is displayed, c_size and b_size should be equals. If not,
    # and if the canvas is resizable, the canvas might have a different size
    # because it hasn't been updated. In that case, we force the canvas to have
    # the same size as the backend :
    if c_size != b_size:
        canvas.size = b_size

    # Backup size / background color :
    backup_size = canvas.physical_size
    backup_bgcolor = canvas.bgcolor

    # User select a desired print size with at a specific dpi :
    if print_size is not None:
        # Type checking :
        if not isinstance(print_size, (tuple, list, np.ndarray)):
            raise TypeError("The print_size must either be a tuple, list or a "
                            "NumPy array describing the (width, height) of the"
                            " image in " + unit)
        # Check print size :
        if not all([isinstance(k, (int, float)) for k in print_size]):
            raise TypeError("print_size must be a tuple describing the "
                            "(width, height) of the image in " + unit)
        print_size = np.asarray(print_size)
        # If the user select the auto-croping option, the canvas must be render
        # before :
        if autocrop:
            img = canvas.render()
            s_output = piccrop(img)[:, :, 0].shape
        else:
            s_output = b_size
        # Unit conversion :
        if unit == 'millimeter':
            mult = 1. / (10. * 2.54)
        elif unit == 'centimeter':
            mult = 1. / 2.54
        elif unit == 'pixel':
            mult = 1. / dpi
        elif unit == 'inch':
            mult = 1.
        else:
            raise ValueError("The unit must either be 'millimeter', "
                             "'centimeter', 'pixel' or 'inch' and not " + unit)
        # Get the factor to apply to the canvas size. This factor is defined as
        # the mean required float to get either the desired width/height.
        # Note that the min or the max can also be used instead.
        factor = np.mean(print_size * dpi * mult / np.asarray(s_output))

    # Multply the original canvas size :
    if factor is not None:
        # Get the new width and height :
        new_width = int(b_size[0] * factor)
        new_height = int(b_size[1] * factor)
        # Set it to the canvas, backend and the widget :
        canvas._backend._vispy_set_physical_size(new_width, new_height)
        canvas.size = (new_width, new_height)
        if widget is not None:
            widget.size = (new_width, new_height)

    # Don't use transparency for jpg files :
    # transparent = transparent if splitext(filename)[1] != '.jpg' else False
    # Background color and transparency :
    if bgcolor is not None:
        canvas.bgcolor = color2vb(bgcolor, alpha=1.)
    if transparent:
        canvas.bgcolor = [0.] * 4

    # Render the canvas :
    try:
        img = canvas.render(region=region)
    except:
        raise ValueError("Can not render the canvas. Try to decrease the "
                         "resolution")

    # Apply auto-cropping to the image :
    if autocrop:
        img = piccrop(img)
    # Save it :
    imsave(filename, img)

    # Set to the canvas it's previous size :
    canvas._backend._physical_size = backup_size
    canvas.size = backup_size
    canvas.bgcolor = backup_bgcolor


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
