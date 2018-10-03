"""GUI interactions with sources and text."""
import logging
import numpy as np

from .ui_objects import _run_method_if_needed
from visbrain.utils import (textline2color, safely_set_cbox, fill_pyqt_table)
from visbrain.io import dialog_color


logger = logging.getLogger('visbrain')


class UiSources(object):
    """Main class for managing the interaction between the user and sources."""

    def __init__(self,):
        """Init."""
        # ====================== SOURCES ======================
        self._s_grp.clicked.connect(self._fcn_source_visible)
        self._s_select.currentIndexChanged.connect(self._fcn_source_select)
        self._s_symbol.currentIndexChanged.connect(self._fcn_source_symbol)
        self._s_radiusmin.valueChanged.connect(self._fcn_source_radius)
        self._s_radiusmax.valueChanged.connect(self._fcn_source_radius)
        self._s_edge_color.editingFinished.connect(self._fcn_source_edgecolor)
        self._s_edge_color_p.clicked.connect(self._fcn_source_edgecolor_p)
        self._s_edge_width.valueChanged.connect(self._fcn_source_edgewidth)
        self._s_alpha.valueChanged.connect(self._fcn_source_alpha)

        # ====================== TEXT ======================
        self._st_font_size.valueChanged.connect(self._fcn_text_fontsize)
        self._st_color.editingFinished.connect(self._fcn_text_color)
        self._st_color_p.clicked.connect(self._fcn_text_color_p)
        self._st_dx.valueChanged.connect(self._fcn_text_translate)
        self._st_dy.valueChanged.connect(self._fcn_text_translate)
        self._st_dz.valueChanged.connect(self._fcn_text_translate)

        # ====================== TABLE ======================
        if self.sources.name is not None:
            # Get position / text :
            xyz, txt = self.sources._xyz, self.sources._text
            col = np.c_[txt, xyz].T.tolist()
            col_names = ['Text', 'X', 'Y', 'Z']
            fill_pyqt_table(self._s_table, col_names, col)
            self._s_table.setEnabled(True)
        self._s_analyse_run.clicked.connect(self._fcn_analyse_sources)
        self._s_show_cs.clicked.connect(self._fcn_goto_cs)

        # ====================== PROJECTION ======================
        self._s_proj_mask_color.editingFinished.connect(
            self._fcn_proj_mask_color)
        self._s_proj_mask_color_p.clicked.connect(self._fcn_mask_color_p)
        self._s_proj_apply.clicked.connect(self._fcn_source_proj)

    # =====================================================================
    # SOURCES
    # =====================================================================
    def _sources_to_gui(self):
        """Update GUI using a source object."""
        obj = self._get_select_object()
        self._s_grp.setChecked(obj.visible_obj)
        safely_set_cbox(self._s_symbol, obj.symbol)
        self._s_radiusmin.setValue(obj.radius_min)
        self._s_radiusmax.setValue(obj.radius_max)
        self._s_edge_color.setText(str(obj.edge_color))
        self._s_edge_width.setValue(obj.edge_width)
        self._s_alpha.setValue(obj.alpha * 100.)
        self._st_font_size.setValue(obj.text_size)
        self._st_color.setText(str(obj.text_color))
        dxyz = obj.text_translate
        self._st_dx.setValue(dxyz[0])
        self._st_dy.setValue(dxyz[1])
        self._st_dz.setValue(dxyz[2])

    @_run_method_if_needed
    def _fcn_source_visible(self):
        """Display / hide source object."""
        viz = self._s_grp.isChecked()
        self._get_select_object().visible_obj = viz
        self._st_grp.setEnabled(viz)

    def _fcn_source_select(self):
        """Select the source to display."""
        txt = self._s_select.currentText().split(' ')[0].lower()
        self.sources.set_visible_sources(txt, self.atlas.vertices)

    @_run_method_if_needed
    def _fcn_source_symbol(self):
        """Change the source symbol."""
        self._get_select_object().symbol = self._s_symbol.currentText()

    @_run_method_if_needed
    def _fcn_source_radius(self):
        """Change the radius (min, max)."""
        obj = self._get_select_object()
        obj._radius_min = self._s_radiusmin.value()  # don't update
        obj.radius_max = self._s_radiusmax.value()   # update
        self._vbNode.update()
        self.sources.update()

    @_run_method_if_needed
    def _fcn_source_edgecolor(self):
        """Update source edge color."""
        color = textline2color(str(self._s_edge_color.text()))[1]
        self._get_select_object().edge_color = color

    def _fcn_source_edgecolor_p(self):
        """Edge color picker."""
        color = dialog_color()
        self._s_edge_color.setText(color)
        self._fcn_source_edgecolor()

    @_run_method_if_needed
    def _fcn_source_edgewidth(self):
        """Update source edge width."""
        self._get_select_object().edge_width = self._s_edge_width.value()

    @_run_method_if_needed
    def _fcn_source_alpha(self):
        """Update source alpha."""
        self._get_select_object().alpha = self._s_alpha.value() / 100.

    # =====================================================================
    # TEXT
    # =====================================================================
    @_run_method_if_needed
    def _fcn_text_fontsize(self):
        """Update text font size."""
        self._get_select_object().text_size = self._st_font_size.value()

    @_run_method_if_needed
    def _fcn_text_color(self):
        """Update text color."""
        color = textline2color(str(self._st_color.text()))[1]
        self._get_select_object().text_color = color

    def _fcn_text_color_p(self):
        """Text color picker."""
        color = dialog_color()
        self._st_color.setText(color)
        self._fcn_text_color()

    def _fcn_text_translate(self):
        """Translate text."""
        tr = (self._st_dx.value(), self._st_dy.value(), self._st_dz.value())
        self._get_select_object().text_translate = tr

    # =====================================================================
    # GOTO CROSS-SECTIONS
    # =====================================================================
    @_run_method_if_needed
    def _fcn_goto_cs(self):
        """Cross-section at source location."""
        # Get selected row and xyz :
        row = self._s_table.currentRow()
        xyz = self.sources._xyz[row, :]
        # Set menu cross-sections menu checked :
        self._sec_grp.setChecked(True)
        self._fcn_crossec_viz()
        # Get transformation and apply to xyz :
        self.cross_sec.localize_source(xyz)
        # Set it to cross-sections sliders :
        self._csSagit.setValue(self.cross_sec.sagittal)
        self._csCoron.setValue(self.cross_sec.coronal)
        self._csAxial.setValue(self.cross_sec.axial)
        self._fcn_crossec_move(update=True)

    def _fcn_analyse_sources(self):
        """Analyse sources locations."""
        roi = self._s_analyse_roi.currentText()
        logger.info("Analyse source's locations using %s ROI" % roi)
        df = self.sources.analyse_sources(roi.lower())
        fill_pyqt_table(self._s_table, df=df)

    # =====================================================================
    # PROJECTION
    # =====================================================================
    def _fcn_proj_mask_color(self):
        """Change the color for projected masked sources."""
        color = textline2color(str(self._s_proj_mask_color.text()))[1]
        self.atlas.mesh.mask_color = color

    def _fcn_mask_color_p(self):
        """Use color picker to update mask color."""
        color = dialog_color()
        self._s_proj_mask_color.setText(str(color))
        self._fcn_proj_mask_color()

    def _fcn_source_proj(self, _, **kwargs):
        """Apply source projection."""
        project_on = str(self._s_proj_on.currentText())
        b_obj = self.atlas if project_on == 'brain' else self.roi
        radius = self._s_proj_radius.value()
        contribute = self._s_proj_contribute.isChecked()
        mask_color = textline2color(str(self._s_proj_mask_color.text()))[1]
        project = str(self._s_proj_type.currentText())
        self.sources.project_sources(b_obj, project=project, radius=radius,
                                     contribute=contribute,
                                     mask_color=mask_color, **kwargs)
        self.cbqt.setEnabled('roi', hasattr(self.roi, 'mesh'))
