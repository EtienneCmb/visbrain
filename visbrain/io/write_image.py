"""Export graphical components as figures.

- write_fig_hyp : Export the hypnogram as a figure
- write_fig_canvas : Export a canvas as a figure
- write_fig_pyqt : Export a GUI window as a figure
"""
import os
import logging
import numpy as np

from .path import path_to_tmp, clean_tmp
from ..utils.color import color2vb

logger = logging.getLogger('visbrain')

__all__ = ('write_fig_hyp', 'write_fig_spindles', 'write_fig_canvas',
           'write_fig_pyqt', 'mpl_preview')


def write_fig_hyp(data, sf, file=None, start_s=0, grid=False, ascolor=False,
                  dpi=300, colors={-1: '#8bbf56', 0: '#56bf8b', 1: '#aabcce',
                                   2: '#405c79', 3: '#0b1c2c', 4: '#bf5656'}):
    """Export hypnogram to a high-res png figure.

    Parameters
    ----------
    data : array_like
        Hypnogram vector
    sf : float
        The sampling frequency of displayed elements (could be the
        down-sampling frequency)
    file : string | None
        Output filename (with full path). If None, the plot is displayed.
    start_s : float | 0.
        Record starting time given in seconds.
    grid : bool | False
        Plot X and Y grid.
    ascolor : bool | False
        Plot in color
    dpi : int | 600
        Dots per inches
    color : dict | {}
        Color for each sleep stage. Default is : {-1: '#8bbf56', 0: '#56bf8b',
        1: '#aabcce', 2: '#405c79', 3: '#0b1c2c', 4: '#bf5656'}
    """
    import matplotlib.pyplot as plt
    import datetime

    # Internal copy :
    hypno = data.copy()

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
    fig, ax = plt.subplots(figsize=(8, 3), edgecolor='k')
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
    xlabels = (xticks + start_s).astype(int)
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
            plt.plot(np.ma.masked_array(hypno, mask=mask), i, ls='steps',
                     linewidth=lw)

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

    plt.tick_params(axis='both', which='both', bottom=True, top=False,
                    labelbottom=True, left=True, right=False, labelleft=True,
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
    if isinstance(file, str):
        plt.savefig(file, format='png', dpi=dpi, bbox_inches='tight')
        logger.info('Image successfully saved (%s)' % file)
        plt.close()
    else:
        plt.show()


def write_fig_spindles(data, sf, hypno=None, file=None, start_s=0.,
                       window_s=10., thr=3., nrem_only=False, dpi=300):
    """Show steps of the spindles detection for a specific time window.

    Parameters
    ----------
    data : array_like
        Data vector
    sf : float
        The sampling frequency of displayed elements (could be the
        down-sampling frequency)
    hypno : array_like | None
        Hypnogram vector
    file : string | None
        Output filename (with full path). If None, the plot is displayed.
    start_s : float | 0.
        Starting point in sec of the window to plot
    window_s : float | 10.
        Window duration in seconds
    thresh : float | 3
        Hard threshold for the spindles detection
    dpi : int | 300
        Dots per inches
    """
    import matplotlib.pyplot as plt
    from ..utils.sleep import spindlesdetect
    from ..utils.filtering import filt

    # Define an empty hypno hypnogram if None :
    hypno = np.zeros_like(data) if hypno is None else hypno

    # Run spindles detection on the selected channel
    (idx_spindles, _, _, dur, pwr, idx_start, idx_stop, hard_thr, soft_thr,
     idx_sigma, fmin, fmax, sigma_nfpow, amplitude,
     sigma_thr) = spindlesdetect(data, sf, thr, hypno, nrem_only,
                                 return_full=True)

    # Define plotting range
    start_sf = int(start_s * sf)
    x = range(start_sf, start_sf + int(window_s * sf))

    # Bandpass filter of the window
    elec_filt = filt(sf, [12., 14.], data[x], order=4)

    # Find beginning and end of spindle within the window
    idx_start_win = idx_start[(idx_start >= min(x)) & (idx_start <= max(x))]
    idx_stop_win = idx_stop[(idx_stop >= min(x)) & (idx_stop <= max(x))]
    sp_in_win = np.in1d(idx_start, idx_start_win)
    sp_power = pwr[sp_in_win]
    sp_duration = dur[sp_in_win]

    # Find indices of spindles within the window
    idx_spindles_win = idx_spindles[
        (idx_spindles >= min(x)) & (idx_spindles <= max(x))]

    # Find indices of sigma power > supra-threshold within window
    idx_sigma_win = idx_sigma[(idx_sigma > min(x)) & (idx_sigma < max(x))]
    # Find indices of wavelet amplitude > supra-threshold within window
    with np.errstate(divide='ignore', invalid='ignore'):
        idx_hard = np.where(amplitude > hard_thr)[0]

    idx_hard_win = idx_hard[(idx_hard > min(x)) & (idx_hard < max(x))]

    # Initialize Y vector
    y_sigma, y_spindles, y_wlt, y_hard = np.empty(len(x)), np.empty(len(x)), \
        np.empty(len(x)), np.empty(len(x))
    y_sigma[:], y_spindles[:], y_wlt[:], y_hard[:] = np.nan, np.nan, np.nan, \
        np.nan

    # Fill Y vector
    y_sigma[idx_sigma_win - start_sf] = sigma_nfpow[idx_sigma_win]
    y_spindles[idx_spindles_win - start_sf] = data[idx_spindles_win]
    y_wlt[idx_spindles_win - start_sf] = amplitude[idx_spindles_win]
    y_hard[idx_hard_win - start_sf] = amplitude[idx_hard_win]

    # Start plot
    f, axarr = plt.subplots(4, figsize=(10, 6), sharex=True)
    f.subplots_adjust(hspace=0.6)

    # Plot original signal
    axarr[0].plot(x, data[x], 'darkslategrey', lw=1.5)
    axarr[0].plot(x, y_spindles, 'brown', lw=1.5)
    axarr[0].set_title('Original signal (' + str(window_s) + ' sec)')
    axarr[0].set_xlim([min(x), max(x)])

    if sp_power.size >= 1:
        text = 'power = ' + str(np.round(sp_power, 2)) + \
            ' - duration = ' + str(sp_duration) + ' ms'
        axarr[0].annotate(text, xy=(min(x), min(data[x])), fontsize=9,
                          xycoords='data')

    # Plot filtered signal
    axarr[1].plot(x, elec_filt, 'darkslategrey', linewidth=1.5)
    axarr[1].set_title('Filtered')

    # Plot wavelet envelope
    axarr[2].plot(x, amplitude[x], 'darkslategrey', linewidth=2)
    axarr[2].plot(x, y_wlt, 'coral', lw=3)
    # axarr[2].plot(x, y_hard, 'indianred', lw=3)
    axarr[2].scatter(idx_start_win, amplitude[idx_start_win], 60, 'coral')
    axarr[2].scatter(idx_stop_win, amplitude[idx_stop_win], 60, 'coral')
    axarr[2].set_title('Wavelet')
    axarr[2].axhline(y=hard_thr, color='grey', linestyle=':', lw=1.5)
    axarr[2].axhline(y=soft_thr, color='grey', linestyle=':', lw=1.5)

    # Plot sigma normalized power
    axarr[3].plot(x, sigma_nfpow[x], 'darkslategrey', linewidth=2)
    axarr[3].set_title('Sigma power')
    axarr[3].plot(x, y_sigma, lw=3, color='lightcoral')
    axarr[3].axhline(y=sigma_thr, color='grey', linestyle=':', lw=1.5)

    # Despine
    for ax in range(4):
        axarr[ax].axis('off')

    # Save as .png
    if isinstance(file, str):
        plt.savefig(file, format='png', dpi=dpi, bbox_inches='tight')
        logger.info('Image successfully saved (%s)' % file)
        plt.close()
    else:
        plt.show()


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

    # dpi checking :
    if print_size is None:
        logger.warning("dpi parameter is not active if `print_size` is None. "
                       "Use for example `print_size=(5, 5)`")

    # User select a desired print size with at a specific dpi :
    if print_size is not None:
        # Type checking :
        if not isinstance(print_size, (tuple, list)):
            raise TypeError("The print_size must either be a tuple or a list "
                            "describing the (width, height) of the"
                            " image in %s" % unit)
        # Check print size :
        if not all([isinstance(k, (int, float)) for k in print_size]):
            raise TypeError("print_size must be a tuple describing the "
                            "(width, height) of the image in %s" % unit)

        print_size = np.asarray(print_size)
        # If the user select the auto-croping option, the canvas must be render
        # before :
        if autocrop:
            img = canvas.render()
            s_output = piccrop(img)[:, :, 0].shape
            logger.info("Image cropped to closest non-backround pixels")
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

    # Remove alpha for files that are not png or tiff :
    if os.path.splitext(filename)[1] not in ['.png', '.tiff']:
        img = img[..., 0:-1]

    # Apply auto-cropping to the image :
    if autocrop:
        img = piccrop(img)
        logger.info("Image cropped to closest non-backround pixels")
    # Save it :
    imsave(filename, img)
    px = tuple(img[:, :, 0].T.shape)
    logger.info("Image of size %rpx successfully saved (%s)" % (px, filename))

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
        logger.info('Image successfully saved (%s)' % filename)
    # Take screenshot if filename :
    if filename:
        # Timer (avoid shooting the saving window)
        self.timerScreen = QtCore.QTimer()
        # self.timerScreen.setInterval(100)
        self.timerScreen.setSingleShot(True)
        self.timerScreen.timeout.connect(_take_screenshot)
        self.timerScreen.start(500)


def mpl_preview(canvas, **kw):
    """Preview canvas using Matplotlib."""
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    save_as = os.path.join(path_to_tmp(), 'mpl_render.jpg')
    write_fig_canvas(save_as, canvas, **kw)

    img = mpimg.imread(save_as)
    fig = plt.figure(figsize=(12, 8))
    ax = plt.subplot(111)
    ax.imshow(img, interpolation='bicubic')
    ax.set_xticklabels(())
    ax.set_yticklabels(())
    plt.axis('off')
    fig.tight_layout(pad=0., h_pad=0., w_pad=0.)
    plt.show()
    clean_tmp()
