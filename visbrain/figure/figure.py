"""Docstring."""

import numpy as np
import os

from scipy.misc import imread
import matplotlib.pyplot as plt
import matplotlib as mpl

from ..utils import color2tuple, piccrop, picresize


__all__ = ['Figure']


class Figure(object):
    """Automatically arange pictures in a grid and save a paper ready figure.

    This class can be used to generate figures to be then used in a paper. For
    example, if you export 10 pictures, you may want to concatenate them in a
    (5, 2) grid and add a colorbar.

    Parameters
    ----------
    files : str/list/tuple
        Files to load. If it's a string, only one file will be loaded.
        Otherwise, if files is a iterable object of strings (list, tuple)
        all the files will be loaded.
    path : str | None
        Specify where files are located. If all files are in separate
        folders, use the files variable : files = ['path1/file1.png',
        'path2/file2.jpg', ...]. If all pictures are in the same folder,
        use path='path2myfolder/' and files=['file1.png', 'file2.jpg', ...]
    grid : tuple | None
        Tuple of integers describing how to arange figures. The grid
        describe (n_rows, n_columns) of the final figure. If grid is None
        all pictures will be displayed on a line. For example, if 12
        pictures are loaded, grid could be (6, 2), (4, 3)...
    figtitle : str | None
        Title of the entire figure.
    y : float | 1.02
        Distance between top and title of each axis (if title displayed).
    titles : str/list/tuple | None
        Specify the title of each figure. If titles is None, no title will
        be added. If titles is a string, the same title will be applied to
        all figures. If titles is a list/tuple of strings, the strings
        inside will be used to set the title of each picture independantly
        (must have the same length as files.)
    xlabels : str/list/tuple | None
        Specify the x-axis label of each figure. If xlabels is None,
        no label will be added. If xlabels is a string, the same label will
        be applied to all figures. If xlabels is a list/tuple of strings,
        the strings inside will be used to set the label of each picture
        independantly (must have the same length as files.)
    ylabels : str/list/tuple | None
        Specify the y-axis label of each figure. If ylabels is None,
        no label will be added. If ylabels is a string, the same label will
        be applied to all figures. If ylabels is a list/tuple of strings,
        the strings inside will be used to set the label of each picture
        independantly (must have the same length as files.)
    figsize : tuple | None
        The size of the figure. Should be a tuple of integers.
    subspace : dict | {'left': 0., 'right': 1., 'bottom': 0., 'top': .9,
                       'wspace': 0., 'hspace': 0.05}
        Control margins and the distance between subplots. Use:

            * 'left' : The left side of the subplots of the figure
            * 'right' : The right side of the subplots of the figure
            * 'bottom' : The bottom of the subplots of the figure
            * 'top' : The top of the subplots of the figure
            * 'hspace' : The amount of height reserved for white space
              between subplots, expressed as a fraction of the average axis
              height.
            * 'wspace' : The amount of width reserved for blank space
              between subplots, expressed as a fraction of the average axis
              width.

    rmax : bool | True
        Remove borders of each axis.
    fig_bgcolor : str/tuple/list | None
        Background color of the figure. By default, no background is used.
    ax_bgcolor : str/tuple/list | None
        Background color of each axis. If None, no background will be used.
        If ax_bgcolor is a string, the same background will be used for all
        axes. Finally, use a list of colors to control the background color
        of each axis. This is a very important parameter for transparent
        pictures (like png or tiff files).
    text_color : str/tuple/list | 'black'
        Color of text elements (figure title, axes titles, x and y labels.)
    autocrop : bool | False
        Specify if each picture has to be automatically cropped.
    autoresize : bool | False
        Specify if all pictures have to be resized. If True, all pictures
        will be resized according to the minimum size along row axis. For
        further controls, define autoresize as a dictionary. Use the
        key 'axis' to specify if pictures have to share the same height (0)
        or width (1). Use 'extend' if the smallest (False) or the largest
        have to be considered as the reference.
    """

    def __init__(self, files, path=None, grid=None, figtitle=None, y=1.02,
                 titles=None, xlabels=None, ylabels=None, figsize=None,
                 subspace={'left': 0.05, 'right': 1., 'bottom': 0.1, 'top': .9,
                           'wspace': 0., 'hspace': 0.3}, rmax=True,
                 fig_bgcolor=None, ax_bgcolor=None, text_color='black',
                 autocrop=False, autoresize=False):
        """Init."""
        self._data = []
        self._im = []
        self._ax = []
        self._figure = None
        self._figtitle = figtitle
        self._figsize = figsize
        self._subspace = subspace
        self._y = y
        self._rmax = rmax
        self._autocrop = autocrop
        self._autoresize = autoresize

        # ================ CHECKING ================
        # Files / path :
        if isinstance(files, str):
            files = [files]
        if path is not None:
            files = [os.path.join(path, k) for k in files]
        for k in files:
            if not os.path.isfile(k):
                raise ValueError(k + " is not a file.")
        self._files = files

        # Grid :
        if grid is None:
            grid = (1, len(self))
        else:
            # Type checking :
            if not isinstance(grid, (list, tuple)):
                raise ValueError("The grid parameter must be a list/tuple of"
                                 "integers.")
            else:
                ngrid = np.product(grid)
                if ngrid < len(self):
                    raise ValueError("The number of subplots is n_rows x "
                                     "n_columns = " + str(ngrid) + ". But "
                                     "there's " + str(len(self)) + " pictures"
                                     " loaded so it can not be aranged in a"
                                     " " + str(grid) + " grid.")
        self._grid = grid
        self._index = np.arange(np.product(grid)).reshape(*grid)

        # Color :
        self._figcol = color2tuple(fig_bgcolor)
        self._tcol = color2tuple(text_color)
        if ax_bgcolor is None:
            ax_bgcolor = [None] * len(self)
        elif isinstance(ax_bgcolor, (str, tuple)):
            ax_bgcolor = [color2tuple(ax_bgcolor)] * len(self)
        elif isinstance(ax_bgcolor, list):
            if len(ax_bgcolor) != len(self):
                raise ValueError("The length of the ax_bgcolor parameter must "
                                 "be the same as the number of loaded files.")
            else:
                ax_bgcolor = [color2tuple(k) for k in ax_bgcolor]
        self._axcol = ax_bgcolor

        # Titles / xlabels / ylabels :
        self._titles = self._replicate(titles, 'titles')
        self._xlabels = self._replicate(xlabels, 'xlabels')
        self._ylabels = self._replicate(ylabels, 'ylabels')

        # ================ MAKE ================
        self._make()

    def __len__(self):
        """Get the number of loaded pictures."""
        return len(self._files)

    def __iter__(self):
        """Loop over loaded pictures."""
        for k in self._data:
            yield k

    ##########################################################################
    # METHODS
    ##########################################################################
    def show(self):
        """Display the figure."""
        plt.show()

    def save(self, saveas, dpi=300):
        """Save the figure.

        Parameters
        ----------
        saveas : string
            Name of the saved figure.
        dpi : int | 300
            The resolution of the exported figure.
        """
        self._fig.savefig(saveas, bbox_inches='tight', dpi=dpi,
                          facecolor=self._figcol)

    def colorbar_to_axis(self, toaxis, clim, cmap, vmin=None, under='gray',
                         vmax=None, over='red', title=None, ycb=10.,
                         fz_title=15, ticks='complete', fz_ticks=10,
                         outline=False, orientation='vertical'):
        """Add a colorbar to a particular axis.

        Parameters
        ----------
        toaxis : int
            Integer to specify the axis to which add the colorbar.
        clim : tuple/list
            A tuple of float/int describing the limit of the colorbar.

        cmap : str
            The colormap to use ('viridis', 'jet', 'Spectral'...)
        vmin : float | None
            Minimum threshold. See the under parameter for further details.
        under : string/tuple/list | 'gray'
            Every values bellow vmin will be set to the under color.
        vmax : float | None
            Maximum threshold. See the over parameter for further details.
        over : string/tuple/list | 'red'
            Every values over vmax will be set to the over color.
        title : string | None
            Title of the colorbar.
        ycb : float | 10.
            Distance between the colorbar and it title (if defined).
        fz_title : int/float | 15
            The fontsize of colorbar title.
        ticks : string/int/float/np.ndarray | 'complete'
            Ticks of the colorbar. This parameter is only active if clim
            is defined. Use 'complete' to see only the minimum,
            maximum, vmin and vmax (if defined). Use 'minmax' to only see
            the maximum and minimum. If ticks is a float, an linear
            interpolation between the maximum and minimum will be used.
            Finally, if ticks is a NumPy array, it will be used as colorbar
            ticks directly.
        fz_ticks : int/float | 10
            Fontsize of tick labels.
        outline : bool | False
            Specify if the box arround the colorbar have to be displayed.
        orientation : string | 'vertical'
            Colorbar orientation. Use either 'vertical' or 'horizontal'.

        See also
        --------
        shared_colorbar : colorbar shared by multiple subplots.
        """
        # ----------------- CHECKING -----------------
        if orientation not in ['vertical', 'horizontal']:
            raise ValueError("Colorbar orientation must either be 'vertical' "
                             "or 'horizontal'")

        # ----------------- CURRENT AXIS -----------------
        cim = self._im[toaxis]
        plt.sca(self._ax[toaxis])

        # ----------------- COLORMAP -----------------
        # Manually create the colormap :
        cmap = self._customcmap(cmap, clim, vmin, under, vmax, over)
        cim.set_cmap(cmap)

        # ----------------- COLORBAR -----------------
        cb = plt.colorbar(cim, shrink=0.7, pad=0.01, aspect=10,
                          orientation=orientation)

        # # ----------------- CLIM -----------------
        cim.set_clim(*clim)
        cb.set_clim(*clim)

        # ----------------- CBAR -----------------
        self._cbar(cb, cmap, clim, vmin, under, vmax, over, title, ycb,
                   fz_title, ticks, fz_ticks, outline, orientation, self._tcol)

    def shared_colorbar(self, clim, cmap, position='right', height=.5,
                        width=.02, pltmargin=.02, figmargin=.07, vmin=None,
                        under='gray', vmax=None, over='red', title=None,
                        ycb=10., fz_title=15, ticks='complete', fz_ticks=10,
                        outline=False):
        """Add a colorbar to a particular axis.

        Parameters
        ----------
        toaxis : int
            Integer to specify the axis to which add the colorbar.
        clim : tuple/list
            A tuple of float/int describing the limit of the colorbar.
        cmap : str
            The colormap to use ('viridis', 'jet', 'Spectral'...)
        position : str | 'right'
            Position of the shared colorbar. Use either 'left', 'right',
            or 'bottom'.
        height : float | .5
            Height of the colorbar.
        width : float | .02
            Width of the colorbar.
        pltmargin : float | .05
            Margin between plots and the colorbar.
        figmargin : float | .07
            Margin between the edge of the figure and the colorbar.
        vmin : float | None
            Minimum threshold. See the under parameter for further details.
        under : string/tuple/list | 'gray'
            Every values bellow vmin will be set to the under color.
        vmax : float | None
            Maximum threshold. See the over parameter for further details.
        over : string/tuple/list | 'red'
            Every values over vmax will be set to the over color.
        title : string | None
            Title of the colorbar.
        ycb : float | 10.
            Distance between the colorbar and it title (if defined).
        fz_title : int/float | 15
            The fontsize of colorbar title.
        ticks : string/int/float/np.ndarray | 'complete'
            Ticks of the colorbar. This parameter is only active if clim
            is defined. Use 'complete' to see only the minimum,
            maximum, vmin and vmax (if defined). Use 'minmax' to only see
            the maximum and minimum. If ticks is a float, an linear
            interpolation between the maximum and minimum will be used.
            Finally, if ticks is a NumPy array, it will be used as colorbar
            ticks directly.
        fz_ticks : int/float | 10
            Fontsize of tick labels.
        outline : bool | False
            Specify if the box arround the colorbar have to be displayed.

        See also
        --------
        colorbar_to_axis : add a specific colorbar to an axis.
        """
        # ================ POSITION ================
        if position == 'right':
            plt.subplots_adjust(right=1. - width - figmargin - pltmargin)
            cax = plt.axes([1. - width - figmargin, height / 2, width, height])
            orientation = 'vertical'
        elif position == 'left':
            plt.subplots_adjust(left=figmargin + width + pltmargin)
            cax = plt.axes([figmargin, height / 2, width, height])
            orientation = 'vertical'
        elif position == 'bottom':
            plt.subplots_adjust(bottom=figmargin + width + pltmargin)
            cax = plt.axes([height / 2, figmargin, height, width])
            orientation = 'horizontal'

        cmap = self._customcmap(cmap, clim, vmin, under, vmax, over)
        cb = mpl.colorbar.ColorbarBase(cax, cmap=cmap, orientation=orientation,
                                       norm=mpl.colors.Normalize(*clim))

        # ----------------- CBAR -----------------
        self._cbar(cb, cmap, clim, vmin, under, vmax, over, title, ycb,
                   fz_title, ticks, fz_ticks, outline, orientation, self._tcol)

    ##########################################################################
    # SUB-METHODS
    ##########################################################################
    def _replicate(self, arg, name):
        """Replicate a argument if string."""
        if arg is None:
            arg = [None] * len(self)
        elif isinstance(arg, str):
            arg = [arg] * len(self)
        elif isinstance(arg, (list, tuple)):
            if len(arg) != len(self):
                raise ValueError("The '" + name + "' must have the same length"
                                 " as the number of loaded files")
        return arg

    def _make(self):
        """Make the figure."""
        # ================ LOAD / RESIZE ================
        # Load files :
        for k in self._files:
            _dat = imread(k) if not self._autocrop else piccrop(imread(k))
            self._data.append(_dat)
        # Resize :
        if isinstance(self._autoresize, bool) and self._autoresize:
            self._data = picresize(self._data)
        elif isinstance(self._autoresize, dict):
            self._data = picresize(self._data, **self._autoresize)

        # ================ FIGURE ================
        # Figure creation :
        if self._figcol is not None:
            plt.rcParams['figure.facecolor'] = self._figcol
        self._fig = plt.figure(figsize=self._figsize)
        if self._figtitle is not None:
            self._fig.suptitle(self._figtitle, fontsize=14, fontweight='bold',
                               color=self._tcol)
        if self._subspace:
            self._fig.subplots_adjust(**self._subspace)

        # ================ SUBPLOTS ================
        for num, k in enumerate(self):
            # --------- Display ---------
            plt.subplot(self._grid[0], self._grid[1], num + 1)
            im = plt.imshow(k)
            self._im.append(im)
            ax = plt.gca()
            self._ax.append(ax)
            # --------- Background color ---------
            if self._axcol[num] is not None:
                ax.patch.set_facecolor(self._axcol[num])
            # --------- Labels / title ---------
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels('')
            ax.set_yticklabels('')
            if self._xlabels[num]:
                ax.set_xlabel(self._xlabels[num], color=self._tcol)
            if self._ylabels[num]:
                ax.set_ylabel(self._ylabels[num], color=self._tcol)
            if self._titles[num]:
                ax.set_title(self._titles[num], y=self._y, color=self._tcol)
            # --------- Remove borders ---------
            if self._rmax:
                for loc, spine in ax.spines.items():
                    if loc in ['left', 'right', 'top', 'bottom']:
                        spine.set_color('none')
                        ax.tick_params(**{loc: 'off'})

    @staticmethod
    def _cbar(cb, cmap, clim, vmin, under, vmax, over, title, ycb, fz_title,
              ticks, fz_ticks, outline, orientation, tcol):
        """Colorbar creation."""
        # ----------------- TITLE -----------------
        if title is not None:
            cb.set_label(title, labelpad=ycb, color=tcol,
                         fontsize=fz_title)

        # ----------------- TICKS -----------------
        if clim is not None:
            # Display only (min, max) :
            if ticks == 'minmax':
                ticks = [clim[0], clim[1]]
            # Display (min, vmin, vmax, max) :
            elif ticks == 'complete':
                ticks = [clim[0]]
                if vmin:
                    ticks.append(vmin)
                if vmax:
                    ticks.append(vmax)
                ticks.append(clim[1])
            # Use linearly spaced ticks :
            elif isinstance(ticks, (int, float)):
                ticks = np.arange(clim[0], clim[1] + ticks, ticks)
            # Set ticks and ticklabels :
            cb.set_ticks(ticks)
            cb.set_ticklabels(ticks)
            cb.ax.tick_params(labelsize=fz_ticks)
            # Change ticks color :
            tic = 'y' if (orientation == 'vertical') else 'x'
            cbytick_obj = plt.getp(cb.ax.axes, tic + 'ticklabels')
            plt.setp(cbytick_obj, color=tcol)

        # ----------------- OUTLINE -----------------
        cb.outline.set_visible(outline)

    @staticmethod
    def _customcmap(cmap, clim, vmin=None, under='gray', vmax=None,
                    over='red', n=1000):
        # Generate linearly spaced data :
        data = np.linspace(clim[0], clim[1], n)
        # Create the colormap and apply to data :
        sc = mpl.cm.ScalarMappable(cmap=cmap)
        data_sc = np.array(sc.to_rgba(data))[:, 0:-1]
        # Vmin / Vmax :
        if vmin is not None:
            data_sc[data < vmin] = color2tuple(under)
        if vmax is not None:
            data_sc[data > vmax] = color2tuple(over)
        # Generate the colormap :
        return mpl.colors.ListedColormap(data_sc, N=n)
