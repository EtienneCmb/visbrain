"""Manage objects opacity and slices and link the GUI with deep functions.

This class is used to control the opacity either for each object independantly
or for all objects. Opacity is managed via the slider in the GUI. Then, the
user can control the X, Y and Z slices tu cut apropriates parts of different
objects.
"""

import numpy as np

from ....utils import slider2opacity


__all__ = ['uiOpacity']


class uiOpacity(object):
    """Main class for objects slices / opacity managment."""

    def __init__(self,):
        """Init."""
        # Opacity slider :
        self.OpacitySlider.setValue(self.atlas.opacity * 100)
        self.OpacitySlider.sliderMoved.connect(self._fcn_opacity)
        self._slmin = self.OpacitySlider.minimum()
        self._slmax = self.OpacitySlider.maximum()

        # ============================ Slice ============================
        # Set maximum / minimum for each slice :
        self._fcn_minmax_slice()
        # Set functions :
        # Across x-axis :
        self.xSlices.sliderMoved.connect(self._fcn_xyz_slice)
        self.xSlices_2.sliderMoved.connect(self._fcn_xyz_slice)
        # Across y-axis :
        self.ySlices.sliderMoved.connect(self._fcn_xyz_slice)
        self.ySlices_2.sliderMoved.connect(self._fcn_xyz_slice)
        # Across z-axis :
        self.zSlices.sliderMoved.connect(self._fcn_xyz_slice)
        self.zSlices_2.sliderMoved.connect(self._fcn_xyz_slice)

    def _fcn_minmax_slice(self):
        """Set minimum / maximum of slices."""
        minfact = 1.2
        vert = vert = self.atlas.mesh._vertFaces
        # X-axis :
        self.xSlices.setMinimum(vert[..., 0].min() * minfact)
        self.xSlices.setMaximum(vert[..., 0].max() * minfact)
        self.xSlices_2.setMinimum(vert[..., 0].min() * minfact)
        self.xSlices_2.setMaximum(vert[..., 0].max() * minfact)
        # Y-axis :
        self.ySlices.setMinimum(vert[..., 1].min() * minfact)
        self.ySlices.setMaximum(vert[..., 1].max() * minfact)
        self.ySlices_2.setMinimum(vert[..., 1].min() * minfact)
        self.ySlices_2.setMaximum(vert[..., 1].max() * minfact)
        # Z-axis :
        self.zSlices.setMinimum(vert[:, 2].min() * minfact)
        self.zSlices.setMaximum(vert[:, 2].max() * minfact)
        self.zSlices_2.setMinimum(vert[:, 2].min() * minfact)
        self.zSlices_2.setMaximum(vert[:, 2].max() * minfact)

    def _fcn_opacity(self):
        """Change opacity of objects using the slider.

        This function can be used to assign the opacity slider value to
        different objects (brain / sources / text / connectivity / areas). Then
        every value under 0.05 or over 0.95 will respectively peak to 0 / 1.
        """
        # Get slider value :
        sl = float(self.OpacitySlider.value())
        sl_01 = (sl - self._slmin) / (self._slmax - self._slmin)
        if sl_01 < 0.05:
            sl_01, visible, deep_test = 0., False, False
        elif sl_01 > 0.95:
            sl_01, visible, deep_test = 1., True, True
        else:
            visible, deep_test = True, True

        # =================== Brain opacity ===================
        # Get vertices and color :
        if self.o_Brain.isChecked():
            self.atlas.mesh.set_alpha(sl_01, index=~self.atlas.mask)
            self.atlas.mesh.visible = visible

        # =================== Sources opacity ===================
        if self.o_Sources.isChecked():
            self.sources.sColor[:, 3] = sl_01
            self.sources.edgecolor[:, 3] = sl_01
            self.sources.mesh.visible = visible
            self.sources.mesh.set_gl_state('translucent', depth_test=deep_test)
            self.sources.update()

        # =================== Text opacity ===================
        if self.o_Text.isChecked():
            self.sources.stextcolor[:, 3] = sl_01
            self.sources.stextmesh.opacity = sl_01
            self.sources.stextmesh.visible = visible
            self.sources.stextmesh.set_gl_state('translucent',
                                                depth_test=deep_test)
            self.sources.text_update()

        # =================== Connectivity opacity ===================
        if self.o_Connect.isChecked():
            self.connect.mesh.color[:, 3] = sl_01
            self.connect.mesh.update()
            self.connect.mesh.visible = visible
            self.connect.mesh.set_gl_state('translucent', depth_test=deep_test)

        # =================== Areas opacity ===================
        if self.o_Areas.isChecked():
            self.volume.set_roi_alpha(sl_01)
            self.volume.mesh.visible = visible

        self.view.canvas.update()

    def _fcn_xyz_slice(self):
        """Define slices over x, y and z axis and over different objects.

        The slices can be used to isolate some part of an object. Slices are
        effective on the brain / sources / connectivity / areas.
        """
        # Get slide positions :
        xsl1, xsl2 = - self.xSlices.value(), self.xSlices_2.value()
        ysl1, ysl2 = - self.ySlices.value(), self.ySlices_2.value()
        zsl1, zsl2 = - self.zSlices.value(), self.zSlices_2.value()

        # Define a default string for all objects :
        formatstr = "np.array(" + \
            "({obj}[..., 0] > xsl1) | ({obj}[..., 0] < xsl2) | " + \
            "({obj}[..., 1] > ysl1) | ({obj}[..., 1] < ysl2) | " + \
            "({obj}[..., 2] > zsl1) | ({obj}[..., 2] < zsl2))"

        # =================== Brain slice ===================
        if self.o_Brain.isChecked():
            # Reset mask :
            self.atlas.mask = np.zeros_like(self.atlas.mask)
            # Find vertices to remove :
            tohide = eval(formatstr.format(obj='self.atlas.mesh._vertFaces'))
            # Update mask :
            self.atlas.mask[tohide] = True
            # Get vertices and color :
            vcolor = self.atlas.mesh.get_color
            # Update opacity for non-hide vertices :
            vcolor[self.atlas.mask, 3] = self.view.minOpacity
            sl = float(self.OpacitySlider.value())
            sl_01 = (sl - self._slmin) / (self._slmax - self._slmin)
            vcolor[~self.atlas.mask, 3] = sl_01
            self.atlas.mesh.set_color(vcolor)

        # =================== Sources/Text slice ===================
        if self.o_Sources.isChecked() or self.o_Text.isChecked():
            # Reset mask :
            self.sources.data.mask = np.zeros_like(self.sources.data.mask)
            # Find sources to remove :
            tohide = eval(formatstr.format(obj='self.sources.xyz'))
            # Update mask then sources :
            self.sources.data.mask[tohide] = True
            if self.o_Sources.isChecked():
                self.sources.update()
            if self.o_Text.isChecked():
                self.sources.text_update()

        # =================== Connectivity slice ===================
        if self.o_Connect.isChecked():
            # Reset mask :
            self.connect.connect.mask = self.connect._maskbck
            # Find sources to remove :
            tohide = eval(formatstr.format(obj='self.sources.xyz'))
            # Update mask :
            self.connect.connect.mask[tohide, :] = True
            self.connect.connect.mask[:, tohide] = True
            self.connect.select[tohide, :] = 0
            self.connect.select[:, tohide] = 0
            if len(self.connect.connect.compressed()) <= 1:
                self.connect.mesh.visible = False
            else:
                self.connect.mesh.visible = True
                # self.connect.mesh.set_data(self.connect.connect)
                self.connect.update()

        # =================== Areas slice ===================
        if self.o_Areas.isChecked():
            raise ValueError("NOT CONFIGURED")  # <--------------------------

        self.view.canvas.update()
