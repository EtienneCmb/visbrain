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
                self.rotate_fixed('axial')
            elif event.text == '1':
                self.rotate_fixed('coronal')
            elif event.text == '2':
                self.rotate_fixed('sagittal')
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
            # self.atlas.mesh.mesh_data.set_vertices( reset_normals=True)
            # self._vbNode.transform = vist.NullTransform()
            # import vispy.visuals.transforms as vist
            # st = vist.STTransform(translate=(0.1, 0, 0))
            # self.view.wc.scene.transform = st
            pass

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            import numpy as np
            az = self.view.wc.camera.azimuth
            el = self.view.wc.camera.elevation
            print(el)
            self.atlas.mesh.shared_program.vert['light_dir'] = tuple(np.random.randint(0, el, 3))
            self.view.canvas.update()
            # self._vbNode.transform = self.view.wc.camera.transform

        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            pass
            """
            """
            # import vispy.visuals.transforms as vist
            # from vispy.visuals.transforms import MatrixTransform
            # rotation = MatrixTransform()
            # rotation.rotate(self.view.wc.camera.azimuth, (0,0,1))
            # rotation.rotate(self.view.wc.camera.elevation, (1,0,0))
            # self.view.wc.scene.transform = rotation

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            t = self.view.wc.camera.transform
            ldir = self.atlas.mesh.shared_program.vert['light_dir'] 
            print(self.atlas.mesh.shared_program.vert['light_dir'])
            self.atlas.mesh.shared_program.vert['light_dir'] = t.map(ldir)[0:-1]
            self.atlas.mesh.update()



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
        self.canvas = scene.SceneCanvas(keys='interactive', show=True, dpi=600,
                                        bgcolor=bgcolor, fullscreen=True, #px_scale=2,
                                        resizable=True, position=(0, 250))
        self.canvas.context.set_line_width(5)
        self.wc = self.canvas.central_widget.add_view()

        # Initialize colorbar canvas :
        self.cbcanvas = scene.SceneCanvas(bgcolor=bgcolor)
        self.cbwc = self.cbcanvas.central_widget.add_view()

        # Add axis (debugging):
        # ax = scene.visuals.XYZAxis()
        # self.wc.add(ax)

        # Visualization settings :
        self.minOpacity = -10000
        self.maxOpacity = 10000

