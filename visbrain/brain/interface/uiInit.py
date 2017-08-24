"""This script group the diffrent graphical components.

Grouped components :
    * PyQt elements (window, Pyqt functions...)
    * Vispy canvas functions
    * User shortcuts
"""

from PyQt5 import QtWidgets

from vispy import app, scene

from .gui import Ui_MainWindow
from ...utils import color2vb, get_screen_size

__all__ = ('uiInit')


class BrainShortcuts(object):
    """This class add some shortcuts to the main canvas of Brain.

    It's also use to initialize to panel of shortcuts.

    Args:
        canvas: vispy canvas
            Vispy canvas to add the shortcuts.
    """

    def __init__(self, canvas):
        """Init."""
        self.sh = [('<space>', 'Brain transparency'),
                   ('<delete>', 'Reset camera'),
                   ('0', 'Top view'),
                   ('1', 'Bottom view'),
                   ('2', 'Left view'),
                   ('3', 'Right view'),
                   ('4', 'Front view'),
                   ('5', 'Back view'),
                   ('b', 'Display / hide brain'),
                   ('x', 'Display / hide cross-sections'),
                   ('v', 'Display / hide volume'),
                   ('s', 'Display / hide sources'),
                   ('t', 'Display / hide connectivity'),
                   ('r', 'Display / hide ROI'),
                   ('c', 'Display / hide colorbar'),
                   ('a', 'Auto-scale the colormap'),
                   ('+', 'Increase brain opacity'),
                   ('-', 'Decrease brain opacity'),
                   ('CTRL + p', 'Run the cortical projection'),
                   ('CTRL + r', 'Run the cortical repartition'),
                   ('CTRL + d', 'Display / hide setting panel'),
                   ('CTRL + e', 'Show the documentation'),
                   ('CTRL + t', 'Display shortcuts'),
                   ('CTRL + n', 'Screenshot of the main canvas'),
                   ('CTRL + n', 'Screenshot of the entire window'),
                   ('CTRL + q', 'Exit'),
                   ]

        # Add shortcuts to BrainCanvas :
        @canvas.events.key_press.connect
        def on_key_press(event):
            """Executed function when a key is pressed on a keyboard over Brain canvas.

            :event: the trigger event
            """
            # Internal / external view :
            if event.text == ' ':
                viz = self._brainTransp.isChecked()
                self._brainTransp.setChecked(not viz)
                self._light_reflection()
                self._light_Atlas2Ui()

            # Increase / decrease brain opacity :
            elif event.text in ['+', '-']:
                # Get slider value :
                sl = self.OpacitySlider.value()
                step = 10 if (event.text == '+') else -10
                self.OpacitySlider.setValue(sl + step)
                self._fcn_opacity()
                self._light_Atlas2Ui()

                # Colormap :
            elif event.text == 'a':
                self.cbqt._fcn_cbAutoscale()

        @canvas.events.mouse_release.connect
        def on_mouse_release(event):
            """Executed function when the mouse is pressed over Brain canvas.

            :event: the trigger event
            """
            # Hide the rotation panel :
            self.userRotationPanel.setVisible(False)

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over Brain canvas.

            :event: the trigger event
            """
            pass

        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            """Executed function when the mouse move over Brain canvas.

            :event: the trigger event
            """
            if self.view.wc.camera.name == 'turntable':
                # Display the rotation panel and set informations :
                self._fcn_userRotation()

        @canvas.events.mouse_press.connect
        def on_mouse_press(event):
            """Executed function when single click mouse over Brain canvas.

            :event: the trigger event
            """
            if self.view.wc.camera.name == 'turntable':
                # Display the rotation panel :
                self._fcn_userRotation()
                self.userRotationPanel.setVisible(True)


class BrainCanvas(object):
    """This class is responsible of cannvas creation.

    The main canvas in which the brain is displayed.

    Kargs:
        bgcolor: tuple, optional, (def: (0, 0, 0))
            Set the background color for both canvas (main canvas in
            which the brain is displayed and the canvas for the colorbar)
    """

    def __init__(self, title='', bgcolor=(0, 0, 0), size=(800, 600)):
        """Init."""
        # Initialize main canvas:
        self.canvas = scene.SceneCanvas(keys='interactive', show=False,
                                        dpi=600, bgcolor=bgcolor,
                                        fullscreen=True, resizable=True,
                                        title=title)  # , size=size)
        self.wc = self.canvas.central_widget.add_view()
        # Visualization settings. The min/maxOpacity attributes are defined
        # because it seems that OpenGL have trouble with small opacity (usually
        # between 0 and 1). Defining min and max far away from 0 / 1 solve this
        # problem.
        self.minOpacity = -10000
        self.maxOpacity = 10000


class uiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas, BrainShortcuts):
    """Group and initialize the graphical elements and interactions.

    Kargs:
        bgcolor: tuple, optional, (def: (0.1, 0.1, 0.1))
            Background color of the main window. The same background
            will be used for the colorbar panel so that future figures
            can be uniform.
    """

    def __init__(self, bgcolor=(0.1, 0.1, 0.1)):
        """Init."""
        # Create the main window :
        super(uiInit, self).__init__(None)
        self.setupUi(self)
        if self._savename is not None:
            self.setWindowTitle('Brain - ' + self._savename)

        # Get screen size :
        size = get_screen_size(self._app)

        #######################################################################
        #                            BRAIN CANVAS
        #######################################################################
        self.view = BrainCanvas('MainCanvas', bgcolor, size)
        self.vBrain.addWidget(self.view.canvas.native)

        #######################################################################
        #                         CROSS-SECTIONS CANVAS
        #######################################################################
        self._csView = BrainCanvas('SplittedCrossSections', bgcolor, size)
        self._csGrid = {'grid': self._csView.canvas.central_widget.add_grid()}
        self._csGrid['Sagit'] = self._csGrid['grid'].add_view(row=0, col=0)
        self._csGrid['Coron'] = self._csGrid['grid'].add_view(row=0, col=1)
        self._csGrid['Axial'] = self._csGrid['grid'].add_view(row=1, col=0,
                                                              col_span=2)
        self._csGrid['Axial'].border_color = (1., 1., 1., 1.)
        self._csGrid['Coron'].border_color = (1., 1., 1., 1.)
        self._csGrid['Sagit'].border_color = (1., 1., 1., 1.)
        self._axialLayout.addWidget(self._csView.canvas.native)

        # Set background color and hide quick settings panel :
        self.bgcolor = tuple(color2vb(color=bgcolor, length=1)[0, 0:3])

        # Set background elements :
        self.bgd_red.setValue(self.bgcolor[0])
        self.bgd_green.setValue(self.bgcolor[1])
        self.bgd_blue.setValue(self.bgcolor[2])

        # Initialize shortcuts :
        BrainShortcuts.__init__(self, self.view.canvas)
