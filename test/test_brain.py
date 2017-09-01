"""Test Brain module and related methods."""
import os
import shutil
from warnings import warn

from PyQt5 import QtWidgets
import numpy as np
from itertools import product

from visbrain import Brain


# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))

# Create empty argument dictionary :
kwargs = {}

# ---------------- Sources ----------------
# Define some random sources :
kwargs['s_xyz'] = np.random.randint(-20, 20, (10, 3))
kwargs['s_data'] = 100 * np.random.rand(10)
kwargs['s_color'] = ['blue'] * 3 + ['white'] * 3 + ['red'] * 4
kwargs['s_mask'] = np.array([True + False] + [True] * 9)

# ---------------- Connectivity ----------------
# Connectivity array :
c_connect = np.random.randint(-10, 10, (10, 10)).astype(float)
c_connect[np.tril_indices_from(c_connect)] = 0
c_connect = np.ma.masked_array(c_connect, mask=True)
nz = np.where((c_connect > -5) & (c_connect < 5))
c_connect.mask[nz] = False
kwargs['c_connect'] = c_connect

# ---------------- Time-series ----------------
kwargs['ts_data'] = 100. * np.random.rand(10, 100)
kwargs['ts_select'] = np.ones((10,), dtype=bool)
kwargs['ts_select'][[3, 4, 7]] = False

# ---------------- Pictures ----------------
kwargs['pic_data'] = 100. * np.random.rand(10, 20, 17)

# ---------------- Application  ----------------
app = QtWidgets.QApplication([])
vb = Brain(**kwargs)


class TestBrain(object):
    """Test brain.py."""

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

    ###########################################################################
    #                                 BRAIN
    ###########################################################################
    def test_scene_rotation(self):
        """Test scene rotations/."""
        rotations = ['axial', 'coronal', 'sagittal',
                     'axial_0', 'coronal_0', 'sagittal_0',
                     'axial_1', 'coronal_1', 'sagittal_1']
        customs = [(90., 0.), (-90, 90.), (180., 180.)]
        # Fixed rotations :
        for k in rotations:
            vb.rotate(fixed=k)
        for k in customs:
            vb.rotate(custom=k)

    def test_brain_control(self):
        """Test method brain_control."""
        template = ['B1', 'B2', 'B3']
        hemi = ['left', 'right', 'both']
        transparent = [False, True]
        alpha = [.1, 1.]
        color = [(1., 1., 1.), 'white', '#ab4642']
        visible = [True, False]
        # Test brain template / hemisphere :
        for k in product(template, hemi):
            vb.brain_control(*k)
        # TEst transparency / alpha / color / visible :
        for k in product(transparent, alpha, color, visible):
            vb.brain_control(None, None, *k)

    def test_brain_list(self):
        """Test method brain_list."""
        assert vb.brain_list() == ['B1', 'B2', 'B3']

    ###########################################################################
    #                                 VOLUME
    ###########################################################################
    def test_add_volume(self):
        """Test method add_volume."""
        warn('add_volume() not tested')

    def test_volume_list(self):
        """Test method volume_list."""
        assert vb.volume_list() == ['Brodmann', 'AAL']

    def test_cross_sections_control(self):
        """Test method cross_sections_control."""
        vb.cross_sections_control()
        vb.cross_sections_control(pos=(10.8, 12.1, 11.))
        vb.cross_sections_control(center=(90, 90, 90), visible=False)
        vb.cross_sections_control(volume='AAL', split_view=False,
                                  transparent=False, cmap='Spectral',
                                  show_text=False)

    def test_volume_control(self):
        """Test method volume_control."""
        vb.volume_control()
        for k in ['mip', 'translucent', 'additive', 'iso']:
            vb.volume_control(rendering=k, threshold=0.95)

    ###########################################################################
    #                                 SOURCES
    ###########################################################################
    @staticmethod
    def _get_projection_cmap():
        skw = {'vmin': .1, 'vmax': .8, 'isvmin': True, 'isvmax': True,
               'under': 'gray', 'over': 'red', 'clim': (0., 1.),
               'cmap': 'Spectral_r'}
        return skw

    def test_sources_control(self):
        """Test method sources_control."""
        s_kwargs = {'data': np.random.rand(10), 'color': 'orange',
                    'symbol': 'square', 'radiusmax': 50., 'radiusmin': 20.,
                    'edgecolor': 'white', 'edgewidth': .6, 'scaling': True,
                    'alpha': .1, 'mask': None, 'maskcolor': 'gray'}
        for item, value in s_kwargs.items():
            vb.sources_control(**{item: value})

    def test_sources_opacity(self):
        """Test method sources_opacity."""
        vb.sources_opacity(alpha=.4, show=False)
        vb.sources_opacity(alpha=1., show=True)
        warn("Merge source_control(), source_opacity() and potentially "
             "source_display()")

    def test_sources_display(self):
        """Test method sources_display."""
        for k in ['outside', 'none', 'left', 'right', 'inside', 'all']:
            vb.sources_display(k)

    def test_sources_fit(self):
        """Test method sources_fit."""
        vb.sources_fit()

    def test_cortical_projection(self):
        """Test method cortical_projection."""
        vb.cortical_projection(contribute=False)
        vb.cortical_projection(contribute=True, **self._get_projection_cmap())

    def test_cortical_repartition(self):
        """Test method cortical_repartition."""
        vb.cortical_repartition(contribute=False)
        vb.cortical_repartition(contribute=True, **self._get_projection_cmap())

    def test_sources_colormap(self):
        """Test method sources_colormap."""
        vb.sources_colormap(**self._get_projection_cmap())

    def test_sources_to_convex_hull(self):
        """Test method sources_to_convex_hull."""
        s_xyz = 20 * np.random.randn(10, 3)
        vb.sources_to_convex_hull(s_xyz)

    def test_add_sources(self):
        """Test method add_sources."""
        s_xyz = 20 * np.random.randn(10, 3)
        s_data = np.random.rand(10)
        vb.add_sources('NewSources', s_xyz=s_xyz, s_data=s_data)

    ###########################################################################
    #                              TIME-SERIES
    ###########################################################################
    def test_time_series_control(self):
        """Test method time_series_control."""
        vb.time_series_control('green', 1., 10., 20., (1., 2., 3.), True)

    def test_add_time_series(self):
        """Test method add_time_series."""
        ts_xyz = np.random.rand(20, 3)
        ts_data = np.random.rand(20, 200)
        vb.add_time_series('NewTimeSeries', ts_xyz, ts_data)

    ###########################################################################
    #                              PICTURES
    ###########################################################################
    def test_pictures_control(self):
        """Test method pictures_control."""
        vb.pictures_control(20., 10., (1., 2., 3.))

    def test_add_pictures(self):
        """Test method add_pictures."""
        pic_xyz = np.random.rand(20, 3)
        pic_data = np.random.rand(20, 7, 8)
        vb.add_pictures('NewPictures', pic_xyz, pic_data)

    ###########################################################################
    #                                 CONNECTIVITY
    ###########################################################################
    def test_connect_control(self):
        """Test method connect_control."""
        colorby = ['strength', 'count', 'density']
        for k in colorby:
            vb.connect_control(k)
        vb.connect_control(dynamic=(.4, .95), show=False,
                           **self._get_projection_cmap())

    def test_add_connect(self):
        """Test method add_connect."""
        vb.add_connect('NewConnect', c_xyz=np.random.rand(7, 3))

    ###########################################################################
    #                                 ROI
    ###########################################################################
    def test_roi_control(self):
        """Test method roi_control."""
        vb.roi_control([7, 11], 'AAL', 7, 'Roi_7-11_AAL')
        vb.roi_control([3, 5], 'Brodmann', 5, 'Roi_3-5_Brodmann')

    def test_roi_fit(self):
        """Test method roi_fit."""
        vb.sources_fit('Roi_7-11_AAL')

    def test_roi_repartition(self):
        """Test method roi_repartition."""
        vb.cortical_repartition(project_on='Roi_3-5_Brodmann')

    def test_roi_projection(self):
        """Test method roi_projection."""
        vb.cortical_projection(project_on='Roi_3-5_Brodmann')

    def test_roi_light_reflection(self):
        """Test method roi_light_reflection."""
        vb.roi_light_reflection('external')
        vb.roi_light_reflection('internal')
        warn('Merge roi_light_reflection() and roi_opacity()')

    def test_roi_opacity(self):
        """Test method roi_opacity."""
        vb.roi_opacity(alpha=.8, show=False)

    def test_roi_list(self):
        """Test function roi_list."""
        vb.roi_list('Brodmann')
        vb.roi_list('AAL')

    ###########################################################################
    #                                 COLORBAR
    ###########################################################################
    def test_cbar_select(self):
        """Test method cbar_select."""
        for k in ['Projection', 'Connectivity', 'Pictures']:
            vb.cbar_select(k)

    def test_cbar_list(self):
        """Test method cbar_list."""
        vb.cbar_list()

    def test_cbar_autoscale(self):
        """Test method cbar_autoscale."""
        for k in ['Projection', 'Connectivity', 'Pictures']:
            vb.cbar_autoscale(k)

    def test_colorbar_control(self):
        """Test method colorbar_control."""
        for k in ['Projection', 'Connectivity', 'Pictures']:
            vb.cbar_control(k, **self._get_projection_cmap())

    def test_add_mesh(self):
        """Test method add_mesh."""
        vertices = np.array([[0., 1., 0.],
                             [0., 2., 0.],
                             [0., 3., 1.],
                             [1., 4., 0.]])
        faces = np.array([[0, 1, 2], [0, 1, 3], [1, 2, 3]])
        vb.add_mesh('Test', vertices, faces)

    ###########################################################################
    #                                 GUI
    ###########################################################################
    def test_background_color(self):
        """Test method background_color."""
        vb.background_color('green')
        vb.background_color('#ab4642')
        vb.background_color((.1, .1, .1))

    def test_screenshot(self):
        """Test method screenshot."""
        # On travis, test failed fo jpg figures only.
        canvas = ['main', 'colorbar', 'cross-sections']
        formats = ['.png', '.jpg', '.tiff']
        print_size = [(5, 5), (50, 50), (1000, 1000), (2, 2)]
        unit = ['centimeter', 'millimeter', 'pixel', 'inch']
        # Standard screenshot :
        for k, i in zip(canvas, formats):
            name = self._path_to_tmp(k + '_transparent_' + i)
            try:
                vb.screenshot(name, canvas=k, transparent=True)
            except:
                warn("Screenshot failed for " + k + " transparent canvas")
        # Test print_size and unit at 300 dpi :
        for k, i in zip(print_size, unit):
            name = self._path_to_tmp('main_' + i + '.png')
            try:
                vb.screenshot(name, print_size=k, unit=i)
            except:
                warn("Screenshot failed for print size" + k + " and unit"
                     " " + i + " transparent canvas")
        # Test factor :
        name = self._path_to_tmp('main_factor.png')
        vb.screenshot(name, factor=2., region=(100, 100, 1000, 1000),
                      bgcolor='#ab4642')

    def test_save_config(self):
        """Test method save_config."""
        vb.save_config(self._path_to_tmp('config.txt'))

    def test_load_config(self):
        """Test method load_config."""
        vb.load_config(self._path_to_tmp('config.txt'))

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)
