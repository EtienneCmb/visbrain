# THE IMPORT ARE VERY UGLY, BUT IT'S TESTING!!!!
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot
import sys
from PyQt4.QtGui import *

import sys

from vispy import app, scene, io, geometry, gloo
from vispy.visuals import MeshVisual
from vispy.visuals.transforms import STTransform
from vispy.geometry import create_sphere
import vispy as vp
import numpy as np

import ui.main_visbrain as visui  # This is where we import our ui


class ExampleApp(QtGui.QMainWindow, visui.Ui_MainWindow, app.Canvas):
    def __init__(self, parent=None):
        # Instantiate the ui :
        super(ExampleApp, self).__init__(parent)
        self.w = visui.QtGui.QMainWindow()
        self.setupUi(self)

        # Assign to the pushbuton "tstB" the method "onclick"
        self.tstB.clicked.connect(self.onclick)

        # Load atlas :
        atlas = np.load('./atlas/atlas_b1.npz')
        coord, tri = atlas['coord'], atlas['tri']
        self.coord = coord
        self.tri = tri

        # Define a canvas:
        self.canvas = scene.SceneCanvas(keys='interactive', show=True,
                                        bgcolor=(1, 1, 1), fullscreen=True,
                                        resizable=True, position=(50, 50))

        self.view = self.canvas.central_widget.add_view()

        # Define a camera :
        cam2 = scene.cameras.TurntableCamera(parent=self.view.scene, fov=60.,
                                             azimuth=60)
        self.view.camera = cam2

        # Use this to change the color//opacity of the vertex :
        nv = self.coord.size//3
        vcolor = 0.1*np.ones((nv, 4))  # color type rgba

        # Mesh brain :
        self.mesh = scene.visuals.Mesh(vertices=coord, faces=tri,
                                       shading='smooth', vertex_colors=vcolor)

        # Create sphere:
        mdata = create_sphere(20, 40, radius=7.0)
        verts = mdata.get_vertices()
        faces = mdata.get_faces()
        sphere = scene.visuals.Mesh(verts, faces, shading='smooth',
                                    parent=self.view.scene)

        # Translate sphere :
        sphere.transform = STTransform(translate=[5, 10, 20])

        # Add a text (center of the brain) :
        txt = scene.visuals.Text('You are here', font_size=50,
                                 parent=self.view.scene)

        # Add random lines :
        lines = scene.visuals.LinePlot(np.random.rand(1000, 3), width=20,
                                       color=(1, 0, 0), parent=self.view.scene)

        # Finally add elements to our canvas:
        self.view.add(lines)
        self.view.add(self.mesh)
        self.view.add(txt)
        self.view.add(sphere)

        # self.canvas = canvas
        # self.mesh = mesh
        # self.view = view

    def onclick(self):
        """This function is to try to update the color of the brain
        by pressing the push button. But it's not working. I think I
        know why, but not sure...
        """
        nv = self.coord.size//3
        vcolor = 0.5*np.ones((nv, 4))
        vcolor[:, 0] = np.linspace(1, 0, nv)
        vcolor[:, 1] = np.random.normal(size=nv)
        vcolor[:, 2] = np.linspace(0, 1, nv)
        self.mesh.mesh_data.set_vertex_colors(vcolor)
        self.mesh.update()
        self.canvas.update()
        self.canvas.show()
        app.process_events()
        # self.view = self.canvas.central_widget.add_view()
        # self.view.add(self.mesh)

        # self.view[0] = self.mesh

        # self.view.canvas.update()
        # self.view.add(self.mesh)
        # # self.mesh.update()
        # self.canvas.central_widget.update()
        self.view.update()
        self.update()
        print('ok')


def main():
    app = QtGui.QApplication(sys.argv)
    visui = ExampleApp()

    # Plot the brain in the visui canvas define in visui.py
    visui.vBrain.addWidget(visui.canvas.native)

    visui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
