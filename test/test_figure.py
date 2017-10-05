"""Test command lines."""
import os
import shutil

from visbrain import Figure
from visbrain.io import download_file

# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))


class TestFigure(object):
    """Test figure.py."""

    ###########################################################################
    #                                 SETTINGS
    ###########################################################################
    def test_create_tmp_folder(self):
        """Create tmp folder."""
        if not os.path.exists(path_to_tmp):
            os.makedirs(path_to_tmp)

    @staticmethod
    def _path_to_tmp(name):
        return os.path.join(*(path_to_tmp, name))

    def test_download_file(self):
        """Download the EDF dataset."""
        download_file('figure.zip', to_path=path_to_tmp, unzip=True)

    ###########################################################################
    #                                 FIGURE
    ###########################################################################
    def test_figure(self):
        """Test function figure."""
        # Get files :
        _files = ['default.png', 'inside.png', 'count.png', 'density.png',
                  'repartition.jpg', 'roi.jpg']
        files = [self._path_to_tmp(k) for k in _files]

        # Titles :
        titles = ['Default', 'Sources inside', 'Connectivity',
                  'Connectivity', 'Repartition', 'Projection']

        # X-labels / Y-labels :
        xlabels = [None, None, 'Nice', 'Looks good', 'Repartition', 'ROI']
        ylabels = ['Dirty', 'Better', None, None, None, 'BA 4 and 6']

        # Background color of each axis :
        ax_bgcolor = ['slateblue', 'olive', 'black', 'darkgray', None, None]

        f = Figure(files, titles=titles, xlabels=xlabels, ylabels=ylabels,
                   figtitle='Brain module', grid=(3, 2), ax_bgcolor=ax_bgcolor,
                   y=1., fig_bgcolor='white', figsize=(12, 12),
                   text_color='black', subspace={'wspace': 0.1, 'left': 0.})
        # Colorbar to the first connectivity plot :
        f.colorbar_to_axis(2, (1, 5), 'viridis', title='Color by count',
                           ticks='minmax', fz_ticks=12)
        # Colorbar to the second connectivity plot :
        f.colorbar_to_axis(3, (0., 35.), 'magma', title='Color by density',
                           ticks='complete', vmax=30, over='darkred',
                           fz_ticks=12, vmin=10., under='gray')
        # Colorbar to the first projection plot :
        f.colorbar_to_axis(4, (1, 6), 'viridis', title='Contributing sources',
                           ticks=1., fz_ticks=10, orientation='horizontal',
                           vmin=2, under='gray', vmax=4, over='#ab4642')
        # Colorbar to the second projection plot :
        f.colorbar_to_axis(5, (.1, .5), 'inferno', title='ROI projection',
                           ticks=[.2, .3], fz_ticks=10,
                           orientation='horizontal')
        # Add a vertical shared colormap :
        f.shared_colorbar((-10, 10), 'inferno', fz_title=30, vmin=-7, vmax=6,
                          under='olive', over='firebrick', position='right',
                          title='Shared vertical colorbar', fz_ticks=20,
                          pltmargin=.1, figmargin=.1)
        # Add a horizontal shared colormap :
        f.shared_colorbar(cmap='magma', clim=(-17, 17), fz_title=25, vmin=-11,
                          vmax=12, under='olive', over='firebrick',
                          position='bottom', title='Shared horizontal',
                          fz_ticks=15, pltmargin=.1)

        # Save the picture :
        f.save(self._path_to_tmp('figure.png'), dpi=100)

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)
