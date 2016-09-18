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
                self.uiUpdate_light()
            # Increase/decrease brain opacity :
            elif event.text in ['+', '-']:
                # Get slider value :
                sl = self.OpacitySlider.value()
                step = 10 if (event.text == '+') else -10
                self.OpacitySlider.setValue(sl+step)
                self.fcn_opacity()
                self.uiUpdate_light()


        @canvas.events.mouse_release.connect
        def on_mouse_press(event):
            pass

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            pass

        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            pass

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            pass

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

