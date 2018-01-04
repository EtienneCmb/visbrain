"""Test functions in guitools.py."""
import pytest
from PyQt5 import QtWidgets, QtCore

from visbrain.utils.guitools import (slider2opacity, textline2color,
                                     color2json, ndsubplot,
                                     combo, is_color, MouseEventControl,
                                     disconnect_all, extend_combo_list,
                                     get_combo_list_index, safely_set_cbox,
                                     safely_set_spin, safely_set_slider,
                                     toggle_enable_tab, get_screen_size,
                                     set_widget_size)


class TestGuitools(object):
    """Test functions in guitools.py."""

    @staticmethod
    def _get_connect_function():
        def f1():
            pass
        return f1

    def test_slider2opacity(self):
        """Test function slider2opacity."""
        slider2opacity(-20.)
        slider2opacity(200.)
        slider2opacity(20.)

    def test_textline2color(self):
        """Test function textline2color."""
        textline2color("'green'")
        textline2color('green')
        textline2color('(.1, .1, .1)')
        textline2color('#ab4642')
        textline2color(None)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_color2json(self):
        """Test function color2json."""
        app = QtWidgets.QApplication([])  # noqa
        line = QtWidgets.QLineEdit()
        line.setText('green')
        color2json(line)

    def test_ndsubplot(self):
        """Test function ndsubplot."""
        ndsubplot(10, line=30)
        ndsubplot(10, force_col=5)
        ndsubplot(50)

    def test_combo(self):
        """Test function combo."""
        combo(['oki', 1, 2, 1, 'ok', 'oki'], [0, 1, 2, 3, 4, 5])

    def test_is_color(self):
        """Test function is_color."""
        is_color('green')
        is_color('bad_color')
        is_color("'green'", comefrom='textline')
        is_color('(.1, .1, .1)', comefrom='textline')

    def test_mouse_event_control(self):
        """Test class MouseEventControl."""
        class Modifier(object):
            def __init__(self):
                self.name = 'ctrl'

        class MouseEvent(object):
            def __init__(self):
                self.button = 1
                self.modifiers = [Modifier()]

        mec = MouseEventControl()
        me = MouseEvent()
        assert mec._is_left_click(me)
        assert mec._is_modifier(me, 'ctrl')
        assert not mec._is_modifier(me, 'alt')

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_disconnect_all(self):
        """Test function disconnect_all."""
        app = QtWidgets.QApplication([])  # noqa
        f1 = self._get_connect_function()
        spin = QtWidgets.QDoubleSpinBox()
        spin.valueChanged.connect(f1)
        disconnect_all(spin)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_extend_combo_list(self):
        """Test function extend_combo_list."""
        app = QtWidgets.QApplication([])  # noqa
        f1 = self._get_connect_function()
        cbox = QtWidgets.QComboBox()
        cbox.currentIndexChanged.connect(f1)
        extend_combo_list(cbox, 'NewItem', f1)
        assert cbox.itemText(0) == 'NewItem'

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_get_combo_list_index(self):
        """Test function get_combo_list_index."""
        app = QtWidgets.QApplication([])  # noqa
        cbox = QtWidgets.QComboBox()
        extend_combo_list(cbox, 'NewItem1')
        extend_combo_list(cbox, 'NewItem2')
        assert get_combo_list_index(cbox, 'NewItem2') == 1

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_safely_set_cbox(self):
        """Test function safely_set_cbox."""
        app = QtWidgets.QApplication([])  # noqa
        f1 = self._get_connect_function()
        cbox = QtWidgets.QComboBox()
        cbox.currentIndexChanged.connect(f1)
        extend_combo_list(cbox, 'NewItem1', f1)
        extend_combo_list(cbox, 'NewItem2', f1)
        safely_set_cbox(cbox, 1, f1)
        assert int(cbox.currentIndex()) == 1

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_safely_set_spin(self):
        """Test function safely_set_spin."""
        app = QtWidgets.QApplication([])  # noqa
        f1 = self._get_connect_function()
        spin = QtWidgets.QDoubleSpinBox()
        spin.valueChanged.connect(f1)
        safely_set_spin(spin, 2., [f1])
        assert float(spin.value()) == 2.

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_safely_set_slider(self):
        """Test function safely_set_slider."""
        app = QtWidgets.QApplication([])  # noqa
        f1 = self._get_connect_function()
        slider = QtWidgets.QSlider()
        slider.valueChanged.connect(f1)
        safely_set_slider(slider, 2., [f1])
        assert float(slider.value()) == 2.

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_toggle_enable_tab(self):
        """Test function toggle_enable_tab."""
        app = QtWidgets.QApplication([])  # noqa
        _translate = QtCore.QCoreApplication.translate
        tab = QtWidgets.QTabWidget()
        tab_2 = QtWidgets.QWidget()
        tab.addTab(tab_2, "")
        tab.setTabText(tab.indexOf(tab_2), _translate("MainWindow", "TabName"))
        toggle_enable_tab(tab, 'TabName', False)
        assert not tab.isTabEnabled(0)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_get_screen_size(self):
        """Test function get_screen_size."""
        app = QtWidgets.QApplication([])
        get_screen_size(app)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_set_widget_size(self):
        """Test function set_widget_size."""
        app = QtWidgets.QApplication([])
        w = QtWidgets.QWidget()
        set_widget_size(app, w)
