"""This script group the diffrent graphical components.

Grouped components :
    * PyQt elements (window, Pyqt functions...)
    * Vispy canvas functions
    * User shortcuts
"""
import numpy as np

from PyQt5 import QtWidgets
from vispy import app, scene
import vispy.visuals.transforms as vist

from ..visuals.marker import Markers
from .gui import Ui_MainWindow
from visbrain.utils import color2vb


class UiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas):
    """Group and initialize the graphical elements and interactions."""

    def __init__(self):
        """Init."""
        # Create the main window :
        super(UiInit, self).__init__(None)
        self.setupUi(self)


class TimeAxis(object):
    """Create a unique time axis."""

    def __init__(self, axis=True, x_label='', name='', bgcolor=(1., 1., 1.),
                 indic_color='darkred', fcn=[]):
        """Init."""
        # Create the main canvas :
        self.canvas = scene.SceneCanvas(keys=None, bgcolor=bgcolor,
                                        show=False)
        _ = [self.canvas.connect(k) for k in fcn]  # noqa

        # Create a grid :
        grid = self.canvas.central_widget.add_grid(margin=0)
        grid.spacing = 0

        # Add x-axis :
        self.xaxis = scene.AxisWidget(orientation='bottom', text_color='black')
        if axis:
            pad = grid.add_widget(row=0, col=0)
            pad.width_max = 50
        _col = int(axis)
        grid.add_widget(self.xaxis, row=1, col=_col)

        # Main plot :
        self.wc = grid.add_view(row=0, col=_col, border_color='black')

        # Add a square indicator :
        image = color2vb(indic_color)[np.newaxis, ...]
        self.mesh = scene.visuals.Image(image, name='Time indicator')
        self.mesh.transform = vist.STTransform()
        self.mesh.parent = self.wc.scene

        # Add markers :
        pos = np.full((1, 3), -10, dtype=np.float32)
        self.markers = Markers(pos=pos, parent=self.wc.scene)
        self.markers.set_gl_state('translucent')

    def set_data(self, tox=None, width=None, time=None, unit='seconds',
                 markers=None):
        """Move the main square."""
        # Get factor according to unit :
        if unit == 'seconds':
            fact = 1.
        elif unit == 'minutes':
            fact = 60.
        elif unit == 'hours':
            fact = 3660.
        # Move the square
        if (tox, width, time) != (None, None, None):
            self.mesh.transform.translate = tox / fact
            self.mesh.transform.scale = width / fact
            # Update camera :
            self.wc.camera.rect = (0, 0, (time.max() - time.min()) / fact, 1)
        # Set markers :
        if markers is not None:
            if markers.size:
                pos = np.zeros((len(markers), 3), dtype=np.float32)
                pos[:, 0] = markers / fact
                pos[:, 1] = .5
                pos[:, 2] = -10
            else:
                pos = np.full((1, 3), -10, dtype=np.float32)
            self.markers.set_data(pos=pos, symbol='triangle_down', size=20.,
                                  face_color='#42ab46', edge_width=0.)

    def set_camera(self, camera):
        """Set a camera and link all objects inside."""
        # Set camera to the main widget :
        self.wc.camera = camera
        # Link transformations with axis :
        self.xaxis.link_view(self.wc)

    def clean(self):
        """Clean axis."""
        self.mesh.parent = None
        self.mesh = None


class AxisCanvas(object):
    """Create a canvas with an embeded axis."""

    def __init__(self, axis=True, x_label='', name='', use_pad=False,
                 bgcolor='white', fcn=[]):
        """Init."""
        # Save variables :
        self._axis = axis

        # Create the main canvas :
        self.canvas = scene.SceneCanvas(keys=None, bgcolor=bgcolor, show=False,
                                        title=name)
        _ = [self.canvas.connect(k) for k in fcn]  # noqa

        # Add axis :
        if axis:
            # Create a grid :
            grid = self.canvas.central_widget.add_grid(margin=0)

            # Add y-axis :
            if use_pad:
                pad = grid.add_widget(row=1, col=0)
                pad.width_max = 50
            else:
                self.yaxis = scene.AxisWidget(orientation='left',
                                              text_color='black')
                self.yaxis.width_max = 50
                grid.add_widget(self.yaxis, row=1, col=0)

            # Add right padding :
            bottom_pad = grid.add_widget(row=2, col=0, row_span=1)
            bottom_pad.height_max = 10
            top_pad = grid.add_widget(row=0, col=0, row_span=1)
            top_pad.height_max = 10

            # Main plot :
            self.wc = grid.add_view(row=1, col=1, border_color='white')
        # Ignore axis :
        else:
            self.wc = self.canvas.central_widget.add_view()

    def set_camera(self, camera):
        """Set a camera and link all objects inside."""
        # Link transformations with axis :
        self.wc.camera = camera
        if hasattr(self, 'yaxis'):
            self.yaxis.link_view(self.wc)

    def visible_axis(self, visible=True):
        """Display or hide the axis."""
        self._axis = visible
        self.yaxis.visible = visible
        self._rpad.visible = visible
