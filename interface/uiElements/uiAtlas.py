import numpy as np

import vispy.scene.cameras as viscam

from ...utils import slider2opacity

__all__ = ['uiAtlas']

class uiAtlas(object):

    """ui for atlas
    """
    
    def __init__(self,):
        # --------------- MNI ---------------
        # Opacity :
        self.OpacitySlider.sliderMoved.connect(self.fcn_opacity)
        self._slmin = self.OpacitySlider.minimum()
        self._slmax = self.OpacitySlider.maximum()
        if self.atlas.projection is 'internal':self.q_internal.setChecked(True)
        elif self.atlas.projection is 'external':self.q_external.setChecked(True)
        self.q_internal.clicked.connect(self.fcn_internal_external)
        self.q_external.clicked.connect(self.fcn_internal_external)
        # Fixed rotation :
        self.q_coronal.clicked.connect(self.fcn_coronal)
        self.q_axial.clicked.connect(self.fcn_axial)
        self.q_sagittal.clicked.connect(self.fcn_sagittal)
        # Cameras types :
        self.c_Turnable.clicked.connect(self.fcn_switch_camera)
        self.c_Arcball.clicked.connect(self.fcn_switch_camera)
        self.c_Magnify.clicked.connect(self.fcn_switch_camera)
        self.c_Fly.clicked.connect(self.fcn_switch_camera)
        # Slice :
        # Set maximum and minimum for each slice :
        minfact = 1.2
        self.xSlices.setMinimum(self.atlas.vert[:, 0].min()*minfact)
        self.xSlices.setMaximum(self.atlas.vert[:, 0].max()*minfact)
        self.ySlices.setMinimum(self.atlas.vert[:, 1].min()*minfact)
        self.ySlices.setMaximum(self.atlas.vert[:, 1].max()*minfact)
        self.zSlices.setMinimum(self.atlas.vert[:, 2].min()*minfact)
        self.zSlices.setMaximum(self.atlas.vert[:, 2].max()*minfact)
        self.xSlices.sliderMoved.connect(self.fcn_xyzSlice)
        self.ySlices.sliderMoved.connect(self.fcn_xyzSlice)
        self.zSlices.sliderMoved.connect(self.fcn_xyzSlice)


    def fcn_opacity(self):
        """Change opacity using the slider
        """
        # Get vertices and color :
        vcolor = self.atlas.mesh.mesh_data.get_vertex_colors()

        # Get slider value :
        slval = self.OpacitySlider.value()
        slval = slider2opacity(slval, thmin=0.0, thmax=100.0, vmin=self._slmin, vmax=self._slmax,
                               tomin=self.view.minOpacity, tomax=self.view.maxOpacity)

        # Apply either to selected or all vertices :
        if self.opacity_all.isChecked():
            vcolor[:, 3] = slval
        else:
            idx = np.where(vcolor[:, 3] != self.view.minOpacity)
            vcolor[idx, 3] = slval
        self.atlas.mesh.mesh_data.set_vertex_colors(vcolor)
        self.atlas.mesh.mesh_data_changed()


    def fcn_internal_external(self):
        """Internal projection
        """
        if self.q_internal.isChecked():
            self.switch_internal_external('internal')
        elif self.q_external.isChecked():
            self.switch_internal_external('external')
        self.atlas.mesh.update()


    def fcn_coronal(self):
        """Fixed coronal view
        """
        self.view.fixed(vtype='coronal')


    def fcn_axial(self):
        """Fixed axial view
        """
        self.view.fixed(vtype='axial')


    def fcn_sagittal(self):
        """Fixed coronal view
        """
        self.view.fixed(vtype='sagittal')


    def fcn_switch_camera(self):
        """Switch between diffrent types of cameras
        """
        # Get radio buttons values :
        if self.c_Turnable.isChecked():
            self.view.wc.camera = viscam.TurntableCamera(elevation=90, distance=10.0,
                                                                fov=0, azimuth=0)
        if self.c_Arcball.isChecked():
            self.view.wc.camera = viscam.ArcballCamera()
        if self.c_Magnify.isChecked():
            self.view.wc.camera = viscam.MagnifyCamera()
        if self.c_Fly.isChecked():
            self.view.wc.camera = viscam.FlyCamera()


    def fcn_xyzSlice(self):
        """Define x, y and z slices of the brain
        """
        # Get vertices and color :
        vert = self.atlas.mesh.mesh_data.get_vertices()
        vcolor = self.atlas.mesh.mesh_data.get_vertex_colors()
        # Get slide positions :
        xsl = self.xSlices.value()#
        ysl = self.ySlices.value()#
        zsl = self.zSlices.value()#
        # Get checkbox position :
        xch = self.xInvert.isChecked()
        ych = self.yInvert.isChecked()
        zch = self.zInvert.isChecked()
        xsym = '<' if xch else '>'
        ysym = '<' if ych else '>'
        zsym = '<' if zch else '>'
        # Find index to process and not to process :
        formatstr = 'np.where((vert[:, 0] {xsym} xsl) | (vert[:, 1] {ysym} ysl) | (vert[:, 2] {zsym} zsl))[0]'
        allIdx = set(np.arange(0, vert.shape[0]))
        Idx = eval(formatstr.format(xsym=xsym, ysym=ysym, zsym=zsym))
        nIdx = allIdx.difference(set(Idx))
        # Change alpha :
        vcolor[Idx, 3] = self.view.minOpacity
        vcolor[list(nIdx), 3] = self.OpacitySlider.value()/100
        self.atlas.mesh.mesh_data.set_vertex_colors(vcolor)
        self.atlas.mesh.mesh_data_changed()
