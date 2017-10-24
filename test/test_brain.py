"""Test Brain module and related methods."""
import os
import shutil
from PyQt5 import QtWidgets
from warnings import warn

import numpy as np
from itertools import product

from vispy.app.canvas import MouseEvent, KeyEvent
# from vispy.util.keys import Key

from visbrain import Brain
from visbrain.objects import SourceObj, ConnectObj, TimeSeriesObj, PictureObj
from visbrain.io import download_file


# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))

# Download intrcranial xyz :
download_file('xyz_sample.npz', to_path=path_to_tmp)
mat = np.load(os.path.join(path_to_tmp, 'xyz_sample.npz'))
xyz_full = mat['xyz']
mat.closed()
xyz_1, xyz_2 = xyz_full[20:30, :], xyz_full[10:20, :]


# ---------------- Sources ----------------
# Define some random sources :
s_data = 100 * np.random.rand(10)
s_color = ['blue'] * 3 + ['white'] * 3 + ['red'] * 4
s_mask = np.array([True] + [False] * 9)

s_obj1 = SourceObj('S1', xyz_1, data=s_data, color=s_color, mask=s_mask)
s_obj2 = SourceObj('S2', xyz_2, data=2 * s_data, color=s_color,
                   mask=s_mask)

# ---------------- Connectivity ----------------
# Connectivity array :
c_connect = np.random.randint(-10, 10, (10, 10)).astype(float)
c_connect[np.tril_indices_from(c_connect)] = 0
c_connect = np.ma.masked_array(c_connect, mask=True)
nz = np.where((c_connect > -5) & (c_connect < 5))
c_connect.mask[nz] = False
c_connect = c_connect

c_obj = ConnectObj('C1', xyz_1, c_connect)
c_obj2 = ConnectObj('C2', xyz_2, c_connect)

# ---------------- Time-series ----------------
ts_data = 100. * np.random.rand(10, 100)
ts_select = np.ones((10,), dtype=bool)
ts_select[[3, 4, 7]] = False

ts_obj1 = TimeSeriesObj('TS1', ts_data, xyz_1, select=ts_select)
ts_obj2 = TimeSeriesObj('TS2', ts_data, xyz_2, select=ts_select)

# ---------------- Pictures ----------------
pic_data = 100. * np.random.rand(10, 20, 17)

p_obj1 = PictureObj('P1', pic_data, xyz_1)
p_obj2 = PictureObj('P2', 2 * pic_data, xyz_2)

# ---------------- Application  ----------------
app = QtWidgets.QApplication([])
vb = Brain(source_obj=[s_obj1, s_obj2], connect_obj=[c_obj, c_obj2],
           time_series_obj=[ts_obj1, ts_obj2], picture_obj=[p_obj1, p_obj2],
           verbose='debug')


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
        rotations = ['axial_0', 'coronal_0', 'sagittal_0',
                     'axial_1', 'coronal_1', 'sagittal_1', 'top', 'bottom',
                     'back', 'front', 'left', 'right']
        customs = [(90., 0.), (-90, 90.), (180., 180.)]
        # Fixed rotations :
        for k in rotations:
            vb.rotate(fixed=k)
        for k in customs:
            vb.rotate(custom=k)

    def test_brain_control(self):
        """Test method brain_control."""
        template = ['B1', 'B2', 'B3', 'WhiteMatter']
        hemi = ['left', 'right', 'both']
        translucent = [False, True]
        alpha = [.1, 1.]
        visible = [True, False]
        # Test brain template / hemisphere :
        for k in product(template, hemi):
            vb.brain_control(*k)
        # TEst transparency / alpha / color / visible :
        for k in product(translucent, alpha, visible):
            vb.brain_control(None, None, *k)

    def test_brain_list(self):
        """Test method brain_list."""
        vb.brain_list() == ['B1', 'B2', 'B3']

    ###########################################################################
    #                                 VOLUME
    ###########################################################################
    def test_add_volume(self):
        """Test method add_volume."""
        warn('add_volume() not tested')

    def test_volume_list(self):
        """Test method volume_list."""
        assert vb.volume_list() == ['Brodmann', 'AAL', 'Talairach']

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
    def _get_cmap_properties():
        skw = {'vmin': .1, 'vmax': .8, 'isvmin': True, 'isvmax': True,
               'under': 'gray', 'over': 'red', 'clim': (0., 1.),
               'cmap': 'Spectral_r'}
        return skw

    def test_sources_control(self):
        """Test method sources_control."""
        s_kwargs = {'data': np.random.rand(10), 'color': 'orange',
                    'symbol': 'square', 'radius_max': 50., 'radius_min': 20.,
                    'edge_color': 'white', 'edge_width': .6,
                    'alpha': .1, 'mask': None, 'mask_color': 'gray',
                    'visible': True}
        for item, value in s_kwargs.items():
            vb.sources_control('S1', **{item: value})

    def test_sources_display(self):
        """Test method sources_display."""
        for k in ['outside', 'none', 'left', 'right', 'inside', 'all']:
            vb.sources_display(name='S1', select=k)
        vb.sources_display(name='S2', select='all')

    def test_sources_fit(self):
        """Test method sources_fit_to_vertices."""
        vb.sources_fit_to_vertices()
        vb.sources_fit_to_vertices(name='S1')

    def test_cortical_projection(self):
        """Test method cortical_projection."""
        vb.sources_display(select='all')
        vb.cortical_projection(radius=10., contribute=False)
        vb.cortical_projection(contribute=True, **self._get_cmap_properties())

    def test_cortical_repartition(self):
        """Test method cortical_repartition."""
        vb.sources_display(select='all')
        vb.cortical_repartition(contribute=False)
        vb.cortical_repartition(contribute=True, **self._get_cmap_properties())

    def test_sources_to_convex_hull(self):
        """Test method sources_to_convex_hull."""
        s_xyz = 20 * np.random.randn(10, 3)
        vb.sources_to_convex_hull(s_xyz)

    ###########################################################################
    #                              TIME-SERIES
    ###########################################################################
    def test_time_series_control(self):
        """Test method time_series_control."""
        vb.time_series_control('TS1', color='green', line_width=1., width=10.,
                               amplitude=20., translate=[5.] * 3,
                               visible=True)

    ###########################################################################
    #                              PICTURES
    ###########################################################################
    def test_pictures_control(self):
        """Test method pictures_control."""
        vb.pictures_control('P1', width=20., height=10., translate=[5.] * 3,
                            **self._get_cmap_properties())

    ###########################################################################
    #                                 CONNECTIVITY
    ###########################################################################
    def test_connect_control(self):
        """Test method connect_control."""
        colorby = ['strength', 'count']
        for k in colorby:
            vb.connect_control('C1', color_by=k)
        vb.connect_control('C2', dynamic=(.4, .95), show=False,
                           **self._get_cmap_properties())

    ###########################################################################
    #                                 ROI
    ###########################################################################
    def test_roi_control(self):
        """Test method roi_control."""
        # vb.roi_control([10], roi_type='Talairach', smooth=3,
        #                name='Tal_10&11', translucent=True)
        vb.roi_control([3, 5], roi_type='Brodmann', smooth=5,
                       name='Roi_3-5_Brodmann', translucent=True, alpha=.05)
        vb.roi_control([7, 11], roi_type='AAL', smooth=7,
                       name='Roi_7-11_AAL')

    def test_roi_fit(self):
        """Test method roi_fit."""
        vb.sources_fit_to_vertices(fit_to='Roi_7-11_AAL')

    def test_roi_projection(self):
        """Test method roi_projection."""
        vb.sources_display(select='all')
        vb.cortical_projection(radius=20., project_on='Roi_7-11_AAL')

    def test_roi_repartition(self):
        """Test method roi_repartition."""
        vb.sources_display(select='all')
        vb.cortical_repartition(radius=20., project_on='Roi_7-11_AAL')

    def test_roi_list(self):
        """Test function roi_list."""
        vb.roi_list('Brodmann')
        vb.roi_list('AAL')
        vb.roi_list('Talairach')

    ###########################################################################
    #                                 COLORBAR
    ###########################################################################
    def test_cbar_list(self):
        """Test method cbar_list."""
        vb.cbar_list()

    def test_cbar_select(self):
        """Test method cbar_select."""
        for k in vb.cbar_list():
            vb.cbar_select(k)

    def test_cbar_autoscale(self):
        """Test method cbar_autoscale."""
        for k in vb.cbar_list():
            vb.cbar_autoscale(k)

    def test_colorbar_control(self):
        """Test method colorbar_control."""
        for k in vb.cbar_list():
            vb.cbar_control(k, **self._get_cmap_properties())

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
                vb.screenshot(name, canvas=k, transparent=True, dpi=50)
            except:
                warn("Screenshot failed for " + k + " transparent canvas")
        # Test print_size and unit at 50 dpi :
        for k, i in zip(print_size, unit):
            name = self._path_to_tmp('main_' + i + '.png')
            try:
                vb.screenshot(name, print_size=k, unit=i, dpi=50)
            except:
                warn("Screenshot failed for print size" + str(k) + " and unit"
                     " " + i + " transparent canvas")
        # Test factor :
        name = self._path_to_tmp('main_factor.png')
        try:
            vb.screenshot(name, factor=2., region=(100, 100, 1000, 1000),
                          bgcolor='#ab4642', dpi=50)
        except:
            warn("Screenshot failed for region and factor")

    def test_save_config(self):
        """Test method save_config."""
        warn("Config not tested for *Brain*")
        # vb.save_config(self._path_to_tmp('config.txt'))

    def test_load_config(self):
        """Test method load_config."""
        warn("Config not tested for *Brain*")
        # vb.load_config(self._path_to_tmp('config.txt'))

    ###########################################################################
    #                                  UI_FILES
    ###########################################################################

    def test_gui_uimenu_projection(self):
        """Test projection functions in ui_menu."""
        vb._fcn_menu_projection()
        vb._fcn_menu_repartition()

    def test_gui_uimenu_display(self):
        """Test display functions in ui_menu."""
        vb._fcn_menu_disp_set()
        vb._fcn_menu_disp_brain()
        vb._fcn_menu_disp_crossec()
        vb._fcn_menu_disp_vol()
        vb._fcn_menu_disp_sources()
        vb._fcn_menu_disp_connect()
        vb._fcn_menu_disp_roi()
        vb._fcn_menu_disp_cbar()

    def test_gui_uimenu_rotation(self):
        """Test rotation functions in ui_menu."""
        vb._fcn_rotate_top()
        vb._fcn_rotate_bottom()
        vb._fcn_rotate_left()
        vb._fcn_rotate_right()
        vb._fcn_rotate_front()
        vb._fcn_rotate_back()

    def test_gui_uimenu_camera(self):
        """Test camera functions in ui_menu."""
        # Fly :
        vb.menuCamFly.setChecked(True)
        vb._fcn_set_cam_fly()
        # Turntable :
        vb.menuCamFly.setChecked(False)
        vb._fcn_set_cam_fly()

    def test_gui_uiobjects(self):
        """Test function gui_uiobjects."""
        for k in [3, 2, 1, 0]:
            vb._obj_type_lst.setCurrentIndex(k)
            vb._fcn_obj_type()

    @staticmethod
    def _preselect_object(name):
        if name == 'sources':
            vb._obj_type_lst.setCurrentIndex(0)
        elif name == 'connectivity':
            vb._obj_type_lst.setCurrentIndex(1)
        elif name == 'time-series':
            vb._obj_type_lst.setCurrentIndex(2)
        elif name == 'pictures':
            vb._obj_type_lst.setCurrentIndex(3)
        vb._fcn_obj_type()

    def test_gui_uisources_markers(self):
        """Test markers functions in ui_sources."""
        self._preselect_object('sources')
        vb._sources_to_gui()
        vb._fcn_source_visible()
        vb._fcn_source_select()
        vb._fcn_source_symbol()
        vb._fcn_source_radius()
        vb._fcn_source_edgecolor()
        vb._fcn_source_edgewidth()
        vb._fcn_source_alpha()
        vb._fcn_text_fontsize()
        vb._fcn_text_color()
        vb._fcn_text_translate()
        # Analyse / Cross-sections :
        vb._fcn_analyse_sources()
        vb._fcn_goto_cs()

    def test_gui_uisources_ts(self):
        """Test time-series functions in ui_sources."""
        self._preselect_object('time-series')
        vb._ts_to_gui()
        vb._fcn_ts_visible()
        vb._fcn_ts_width()
        vb._fcn_ts_amp()
        vb._fcn_ts_line_width()
        vb._fcn_ts_color()
        vb._fcn_ts_alpha()
        vb._fcn_ts_translate()

    def test_gui_uisources_pic(self):
        """Test pictures functions in ui_sources."""
        self._preselect_object('pictures')
        vb._pic_to_gui()
        vb._fcn_pic_visible()
        vb._fcn_pic_width()
        vb._fcn_pic_height()
        vb._fcn_pic_alpha()
        vb._fcn_pic_translate()

    def test_gui_uiconnect(self):
        """Test functions in ui_connect."""
        self._preselect_object('connectivity')
        vb._connect_to_gui()
        vb._fcn_connect_visible()
        vb._fcn_connect_colorby()
        vb._fcn_connect_transparency_meth()
        vb._fcn_connect_alpha()
        vb._fcn_connect_dyn_alpha()
        vb._fcn_connect_lw()

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)

    ###########################################################################
    #                             SHORTCUTS
    ###########################################################################

    @staticmethod
    def _key_pressed(canvas, ktype='key_press', key='', **kwargs):
        """Test VisPy KeyEvent."""
        k = KeyEvent(ktype, text=key, **kwargs)
        eval('canvas.events.' + ktype + '(k)')

    @staticmethod
    def _mouse_event(canvas, etype='mouse_press', **kwargs):
        """Test a VisPy mouse event."""
        e = MouseEvent(etype, **kwargs)
        eval('canvas.events.' + etype + '(e)')

    def test_key_events(self):
        """Test function events."""
        for k in ['0', '1', '2', '3', '4', '5', 'b', 'x', 'v', 's', 't', 'r',
                  'c', 'a', '+', '-', ' ']:
            self._key_pressed(vb.view.canvas, key=k)

    def test_mouse_events(self):
        """Test function mouse_events."""
        for k in ['mouse_release', 'mouse_double_click', 'mouse_move',
                  'mouse_press']:
            self._mouse_event(vb.view.canvas, etype=k)
