"""Manage objects opacity and slices and link the GUI with deep functions.

This class is used to control the opacity either for each object independantly
or for all objects. Opacity is managed via the slider in the GUI. Then, the
user can control the X, Y and Z slices tu cut apropriates parts of different
objects.
"""

import numpy as np

from ...utils import slider2opacity


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

        # Slice :
        # Set maximum / minimum for each slice :
        minfact = 1.2
        self.xSlices.setMinimum(self.atlas.vert[..., 0].min()*minfact)
        self.xSlices.setMaximum(self.atlas.vert[..., 0].max()*minfact)
        self.ySlices.setMinimum(self.atlas.vert[..., 1].min()*minfact)
        self.ySlices.setMaximum(self.atlas.vert[..., 1].max()*minfact)
        self.zSlices.setMinimum(self.atlas.vert[..., 2].min()*minfact)
        self.zSlices.setMaximum(self.atlas.vert[..., 2].max()*minfact)
        self.xSlices.sliderMoved.connect(self._fcn_xyzSlice)
        self.ySlices.sliderMoved.connect(self._fcn_xyzSlice)
        self.zSlices.sliderMoved.connect(self._fcn_xyzSlice)

    def _getOpacitySlider(self, tomin=0., tomax=1.):
        """Get and normalize the opacity slider value.

        Kargs:
            tomin: float, optional, (def: 0)
                Set to tomin if value is under 0.

            tomax: float, optional, (def: 1.)
                Set to tomax if value is over 100.

        Returns:
            slval: float
                The normalized slider value.

            sl: float
                The unprocessed slider value.
        """
        # Get opacity from the slider :
        sl = self.OpacitySlider.value()
        # Normalize this value :
        slval = slider2opacity(sl, thmin=0.0, thmax=100.0, vmin=self._slmin,
                               vmax=self._slmax, tomin=tomin, tomax=tomax)
        return slval, sl

    def _fcn_opacity(self):
        """Change opacity of objects using the slider.

        This function can be used to assign the opacity slider value to
        different objects (brain / sources / text / connectivity / areas). Then
        every value under 0.05 or over 0.95 will respectively peak to 0 / 1.
        """
        # Get slider value :
        sl = self.OpacitySlider.value()
        sl_01 = (sl-self._slmin)/(self._slmax-self._slmin)
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
            self.connect.mesh.set_opacity(sl_01)
            self.connect.mesh.visible = visible
            self.connect.mesh.set_gl_state('translucent', depth_test=deep_test)

        # =================== Areas opacity ===================
        if self.o_Areas.isChecked():
            self.area.set_alpha(sl_01)

        self.view.canvas.update()

    def _fcn_xyzSlice(self):
        """Define slices over x, y and z axis and over different objects.

        The slices can be used to isolate some part of an object. Slices are
        effective on the brain / sources / connectivity / areas.
        """
        # Get invert checkbox position :
        xsym = '<' if self.xInvert.isChecked() else '>'
        ysym = '<' if self.yInvert.isChecked() else '>'
        zsym = '<' if self.zInvert.isChecked() else '>'

        # Get slide positions :
        xsl, ysl, zsl = self.xSlices.value(
        ), self.ySlices.value(), self.zSlices.value()

        # Define a default string for all objects :
        formatstr = "np.array(({obj}[..., 0] {xsym} xsl) | ({obj}[..., 1] " + \
            "{ysym} ysl) | ({obj}[..., 2] {zsym} zsl))"

        # =================== Brain slice ===================
        if self.o_Brain.isChecked():
            # Reset mask :
            self.atlas.mask = np.zeros_like(self.atlas.mask)
            # Find vertices to remove :
            tohide = eval(formatstr.format(obj='self.atlas.vert', xsym=xsym,
                                           ysym=ysym, zsym=zsym))
            # Update mask :
            self.atlas.mask[tohide] = True
            # Get vertices and color :
            vcolor = self.atlas.mesh.get_color
            # Update opacity for non-hide vertices :
            vcolor[self.atlas.mask, 3] = self.view.minOpacity
            vcolor[~self.atlas.mask, 3] = self._getOpacitySlider(
                tomin=self.view.minOpacity, tomax=self.view.maxOpacity)[0]
            self.atlas.mesh.set_color(vcolor)

        # =================== Sources/Text slice ===================
        if self.o_Sources.isChecked() or self.o_Text.isChecked():
            # Reset mask :
            self.sources.data.mask = np.zeros_like(self.sources.data.mask)
            # Find sources to remove :
            tohide = eval(formatstr.format(obj='self.sources.xyz', xsym=xsym,
                                           ysym=ysym, zsym=zsym))
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
            tohide = eval(formatstr.format(obj='self.sources.xyz',
                                           xsym=xsym, ysym=ysym, zsym=zsym))
            # Update mask :
            self.connect.connect.mask[tohide, :] = True
            self.connect.connect.mask[:, tohide] = True
            if len(self.connect.connect.compressed()) <= 1:
                self.connect.mesh.visible = False
            else:
                self.connect.mesh.visible = True
                self.connect.mesh.set_data(self.connect.connect)

        # =================== Areas slice ===================
        if self.o_Areas.isChecked():
            raise ValueError("NOT CONFIGURED")  # <--------------------------

        self.view.canvas.update()
