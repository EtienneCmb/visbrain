from vispy import scene
import vispy.visuals.transforms as vist

from PyQt4.QtGui import * 

__all__ = ['ViewBase']



class vbShortcuts(object):

    """Shortcuts in visbrain
    """

    def __init__(self, canvas):
        # Shortcuts table :
        self.table_panel.hide()
        self.actionShortcuts.triggered.connect(self.show_hide_shortcuts)
        # self.sh_table.resizeColumnsToContents()
        self.sh_table.resizeRowsToContents()
        self.sh_table.setColumnWidth(self.sh_table.columnCount()-2, 200)
        self.sh_table.setColumnWidth(self.sh_table.columnCount()-1, 100)

        # Init viewbase :
        @canvas.events.key_press.connect
        def on_key_press(event):
            # Switch between default views : :
            if event.text == '0':
                self.view.fixed('axial')
            elif event.text == '1':
                self.view.fixed('coronal')
            elif event.text == '2':
                self.view.fixed('sagittal')
            # Internal/external view :
            elif event.text == '3':
                if self.q_internal.isChecked():
                    self.q_external.setChecked(True)
                elif self.q_external.isChecked():
                    self.q_internal.setChecked(True)
                self.fcn_internal_external()
            # Increase/decrease brain opacity :
            elif event.text in ['+', '-']:
                # Get slider value :
                sl = self.OpacitySlider.value()
                step = 10 if (event.text == '+') else -10
                self.OpacitySlider.setValue(sl+step)
                self.fcn_opacity()


        @canvas.events.mouse_release.connect
        def on_mouse_press(event):
            pass
            # rotation = MatrixTransform()
            # rotation.rotate(self.view.wc.camera.azimuth, (0,0,1))
            # rotation.rotate(self.view.wc.camera.elevation, (1,0,0))
            # self.colorbar.transform = rotation
            # self.colorbar.update
            # print(self.view.wc.camera.azimuth, self.view.wc.camera.elevation, self.view.wc.camera.distance)


    def show_hide_shortcuts(self):
        """
        """
        isVisible = self.table_panel.isVisible()
        if not isVisible:
            self.table_panel.show()
        else:
            self.table_panel.hide()

class ViewBase(object):

    """Class for controlling all displayed elements
    """

    def __init__(self, bgcolor=(0,0,0)):
        # Initialize main canvas:
        self.canvas = scene.SceneCanvas(keys='interactive', show=True, dpi=300,
                                        bgcolor=bgcolor, fullscreen=True, px_scale=1,
                                        resizable=True, position=(0, 250), size=(800, 600))
        self.wc = self.canvas.central_widget.add_view()

        # Initialize colorbar canvas :
        self.cbcanvas = scene.SceneCanvas(bgcolor=bgcolor)
        self.cbwc = self.cbcanvas.central_widget.add_view()

        # Visualization settings :
        self.sagittal = 0
        self.coronal = 0
        self.axial = 0
        self.minOpacity = -10000
        self.maxOpacity = 10000

        

    def fixed(self, vtype='axial'):
        """Switch between coronal, sagittal or axial view
        """
        # Coronal (front, back)
        if vtype is 'sagittal':
            if self.coronal == 0: # Top
                self.wc.camera.azimuth = 180
                self.wc.camera.elevation = 0
                self.coronal = 1
            elif self.coronal == 1: # Bottom
                self.wc.camera.azimuth = 0
                self.wc.camera.elevation = 0
                self.coronal = 0
            self.sagittal, self.axial = 0, 0
        # Sagittal (left, right)
        elif vtype is 'coronal':
            if self.sagittal == 0: # Top
                self.wc.camera.azimuth = -90
                self.wc.camera.elevation = 0
                self.sagittal = 1
            elif self.sagittal == 1: # Bottom
                self.wc.camera.azimuth = 90
                self.wc.camera.elevation = 0
                self.sagittal = 0
            self.coronal, self.axial = 0, 0
        # Axial (top, bottom)
        elif vtype is 'axial':
            if self.axial == 0: # Top
                self.wc.camera.azimuth = 0
                self.wc.camera.elevation = 90
                self.axial = 1
            elif self.axial == 1: # Bottom
                self.wc.camera.azimuth = 0
                self.wc.camera.elevation = -90
                self.axial = 0
            self.sagittal, self.coronal = 0, 0
