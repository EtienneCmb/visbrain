"""This script group the diffrent graphical components.

Grouped components :
    * PyQt elements (window, Pyqt functions...)
    * Vispy canvas functions
    * User shortcuts
"""

from PyQt5 import QtWidgets
from vispy import app, scene

from .gui import Ui_MainWindow
from .cbar import Cbar
from ...utils import color2vb

__all__ = ['uiInit']


class AxisCanvas(object):
    """Create a canvas with an embeded axis."""

    def __init__(self, axis=True, x_label='', x_heightMax=80, y_label='',
                 y_widthMax=80, font_size=12, color='white', title='',
                 axis_label_margin=50, tick_label_margin=5, name='',
                 bgcolor=(.9, .9, .9), cargs={}, xargs={}, yargs={}):
        """Init."""
        # Save variables :
        self._axis = axis
        self._title = title
        self._xlabel = x_label
        self._ylabel = y_label

        # Create the main canvas :
        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor=bgcolor,
                                        show=False, title=name, **cargs)

        # Add axis :
        if axis:
            # Create a grid :
            grid = self.canvas.central_widget.add_grid(margin=10)
            grid.spacing = 0

            # Add a title :
            self._titleObj = scene.Label(title, color=color)
            self._titleObj.height_max = 40
            grid.add_widget(self._titleObj, row=0, col=0, col_span=2)

            # Add y-axis :
            self.yaxis = scene.AxisWidget(orientation='left', domain=(0, 129),
                                          axis_label=y_label,
                                          axis_font_size=font_size,
                                          axis_label_margin=axis_label_margin,
                                          tick_label_margin=tick_label_margin,
                                          **yargs)
            self.yaxis.width_max = y_widthMax
            grid.add_widget(self.yaxis, row=1, col=0)

            # Add x-axis :
            self.xaxis = scene.AxisWidget(orientation='bottom',
                                          axis_label=x_label,
                                          axis_font_size=font_size,
                                          axis_label_margin=axis_label_margin,
                                          tick_label_margin=tick_label_margin,
                                          **xargs)
            self.xaxis.height_max = x_heightMax
            grid.add_widget(self.xaxis, row=2, col=1)

            # Add right padding :
            self._rpad = grid.add_widget(row=1, col=2, row_span=1)
            self._rpad.width_max = 50

            # Main plot :
            self.wc = grid.add_view(row=1, col=1, border_color=color)

        # Ignore axis :
        else:
            self.wc = self.canvas.central_widget.add_view()

    def set_camera(self, camera):
        """Set a camera and link all objects inside."""
        # Set camera to the main widget :
        self.wc.camera = camera
        # Link transformations with axis :
        if self._axis:
            self.xaxis.link_view(self.wc)
            self.yaxis.link_view(self.wc)

    def set_info(self, title=None, xlabel=None, ylabel=None):
        """Set title and labels for the axis of the canvas."""
        # Set label / title only for grid axis :
        if self._axis:
            # X-label :
            if xlabel is not None:
                self.xaxis.axis.axis_label = xlabel
                self.xaxis.update()
            # Y-label :
            if ylabel is not None:
                self.yaxis.axis.axis_label = ylabel
                self.yaxis.update()
            # Title :
            if title is not None:
                self._titleObj.text = title
            self.canvas.update()
        else:
            raise ValueError("For defining infos, you must use an axis canvas")

    def visible_axis(self, visible=True):
        """Display or hide the axis."""
        self._axis = visible
        self.xaxis.visible = visible
        self.yaxis.visible = visible
        self._titleObj.visible = visible
        self._rpad.visible = visible


class vbShortcuts(object):
    """This class add some shortcuts to the main canvas of ndviz.

    It's also use to initialize to panel of shortcuts.

    Args:
        canvas: vispy canvas
            Vispy canvas to add the shortcuts.
    """

    def __init__(self, canvas):
        """Init."""
        # Add shortcuts to vbCanvas :
        @canvas.events.key_press.connect
        def on_key_press(event):
            """Executed function when a key is pressed on a keyboard over ndviz canvas.

            :event: the trigger event
            """
            if event.text == ' ':
                # Play stop :
                self._fcn_TogglePlay()
            if event.text == 'r':
                # Play stop :
                self._fcn_rtreset()
            if event.text == '0':
                # Reset the camera :
                if canvas.title == 'ndCanvas':
                    self._ndplt.mesh.camera.rect = (-1, -1, 2, 2)
                elif canvas.title == '1dCanvas':
                    self._1dCanvas.wc.camera.rect = self._1dplt.mesh.rect
                    self._1dCanvas.wc.camera.update()
            elif event.text == '1':
                # Toggle display nd panel :
                self._ndToggleViz()
            elif event.text == '2':
                # Toggle display 1d panel :
                self._1dToggleViz()
            elif event.text == '3':
                pass
            elif event.text == 'g':
                # Toggle display the grid :
                if canvas.title == 'ndCanvas':
                    self._fcn_ndGridToggle()
                elif canvas.title == '1dCanvas':
                    self._fcn_1dGridToggle()

            elif event.text == 'l':
                # Set 1d plot as line :
                self._cbObjects.setCurrentIndex(1)
                self._fcn_cbautoscale()
            elif event.text == 'm':
                # Set 1d plot as marker :
                self._cbObjects.setCurrentIndex(2)
                self._fcn_cbautoscale()
            elif event.text == 's':
                # Set 1d plot as spectrogram :
                self._cbObjects.setCurrentIndex(3)
                self._fcn_cbautoscale()
            elif event.text == 'h':
                # Set 1d plot as histogram :
                self._1dPltPick.setCurrentIndex(1)
            elif event.text == 'i':
                # Set 1d plot as line :
                self._cbObjects.setCurrentIndex(4)
                self._fcn_cbautoscale()
            elif event.text == 'a':
                # Auto-scale colorbar :
                self._fcn_cbautoscale()
            elif event.text == 'n':
                # Next 1d signal :
                self._1dAxInd.setValue(self._1dAxInd.value()+1)
            elif event.text == 'p':
                # Previous 1d signal :
                self._1dAxInd.setValue(self._1dAxInd.value()-1)
            elif event.text == 'N':
                self._imAxInd.setValue(self._imAxInd.value()+1)
            elif event.text == 'P':
                self._imAxInd.setValue(self._imAxInd.value()-1)

        @canvas.events.mouse_release.connect
        def on_mouse_release(event):
            """Executed function when the mouse is pressed over ndviz canvas.

            :event: the trigger event
            """
            pass

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over ndviz canvas.

            :event: the trigger event
            """
            pass

        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            """Executed function when the mouse move over ndviz canvas.

            :event: the trigger event
            """
            # Display the rotation panel and set informations :
            pass

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            """Executed function when single click mouse over ndviz canvas.

            :event: the trigger event
            """
            # Display the rotation panel :
            pass


class uiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas, vbShortcuts):
    """Group and initialize the graphical elements and interactions.

    Kargs:
        bgcolor: tuple, optional, (def: (0.1, 0.1, 0.1))
            Background color of the main window. The same background
            will be used for the colorbar panel so that future figures
            can be uniform.
    """

    def __init__(self, bgcolor=(.09, .09, .09), nd_title='Nd-plot',
                 nd_xlabel='X axis', nd_ylabel='Y axis', od_title='1d-plot',
                 od_xlabel='X axis', od_ylabel='Y axis'):
        """Init."""
        # Create the main window :
        super(uiInit, self).__init__(None)
        self.setupUi(self)
        if self._savename is not None:
            self.setWindowTitle('ndviz - '+self._savename)

        # Initlialize all canvas :
        self._ndCanvas = AxisCanvas(axis=True, bgcolor=bgcolor, title=nd_title,
                                    x_label=nd_xlabel, y_label=nd_ylabel,
                                    name='ndCanvas')
        self._1dCanvas = AxisCanvas(axis=True, bgcolor=bgcolor, title=od_title,
                                    x_label=od_xlabel, y_label=od_ylabel,
                                    name='1dCanvas')
        self._cbCanvas = AxisCanvas(axis=False, bgcolor=bgcolor,
                                    name='cbCanvas')

        # Add the canvas to the UI (_ndVizLayout layout) and colorbar:
        self._NdVizLayout.addWidget(self._ndCanvas.canvas.native)
        self._NdVizPanel.setVisible(True)
        self._1dVizLayout.addWidget(self._1dCanvas.canvas.native)
        self._1dVizPanel.setVisible(False)
        self.cbpanel.addWidget(self._cbCanvas.canvas.native)

        # Create the colorbar with the different objects :
        self._cb = Cbar(self._cbCanvas.wc.scene)
        self._cb.add_object('ndplt', label='Nd-plot',  fcn=self._fcn_ndUpdate,
                            fcn_minmax=self._fcn_get_NdMinmax)
        self._cb.add_object('line', label='Line', fcn=self._fcn_1dUpdate,
                            fcn_minmax=self._fcn_get_1dMinmax)
        self._cb.add_object('spectrogram', label='Spectrogram',
                            fcn=self._fcn_1dUpdate,
                            fcn_minmax=self._fcn_get_1dMinmax)
        self._cb.add_object('histogram', label='None', fcn=self._fcn_1dUpdate,
                            fcn_minmax=self._fcn_get_1dMinmax)
        self._cb.add_object('marker', label='Marker', fcn=self._fcn_1dUpdate,
                            fcn_minmax=self._fcn_get_1dMinmax)
        self._cb.add_object('image', label='Image', fcn=self._fcn_imUpdate,
                            fcn_minmax=self._fcn_get_1dMinmax)

        # Set background color and hide quick settings panel :
        self.bgcolor = tuple(color2vb(color=bgcolor, length=1)[0, 0:3])
        self.q_widget.hide()

        # Set background elements :
        self._uiBgdRed.setValue(self.bgcolor[0])
        self._uiBgdGreen.setValue(self.bgcolor[1])
        self._uiBgdBlue.setValue(self.bgcolor[2])

        # Set title / label :
        self._ndTitleEdit.setText(nd_title)
        self._ndXlabEdit.setText(nd_xlabel)
        self._ndYlabEdit.setText(nd_ylabel)
        self._1dTitleEdit.setText(od_title)
        self._1dXlabEdit.setText(od_xlabel)
        self._1dYlabEdit.setText(od_ylabel)

        # Initialize shortcuts :
        vbShortcuts.__init__(self, self._ndCanvas.canvas)
        vbShortcuts.__init__(self, self._1dCanvas.canvas)
