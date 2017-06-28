"""Define some basic viewing elements (canvas / shortcuts).

This file contain:
    * vbShortcuts : main class for shortcuts managment
    * vbCanvas : create Brain main canvas and the canvas
    for the colorbar
"""

from vispy import scene

__all__ = ['vbCanvas', 'vbShortcuts']


class vbShortcuts(object):
    """This class add some shortcuts to the main canvas of Brain.

    It's also use to initialize to panel of shortcuts.

    Args:
        canvas: vispy canvas
            Vispy canvas to add the shortcuts.
    """

    def __init__(self, canvas):
        """Init."""
        self.sh = [('<space>', 'Brain transparency'),
                   ('0', 'Top view'),
                   ('1', 'Bottom view'),
                   ('2', 'Left view'),
                   ('3', 'Right view'),
                   ('4', 'Front view'),
                   ('5', 'Back view'),
                   ('b', 'Display / hide brain'),
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
                   ('CTRL + n', 'Take a screenshot'),
                   ('CTRL + q', 'Exit'),
                   ]

        # Add shortcuts to vbCanvas :
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
                self.OpacitySlider.setValue(sl+step)
                self._fcn_opacity()
                self._light_Atlas2Ui()

                # Colormap :
            elif event.text == 'a':
                self._auto_scale()

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


class vbCanvas(object):
    """This class is responsible of cannvas creation.

    The main canvas in which the brain is displayed (canvas) and the canvas
    for the colorbar (cbcanvas)

    Kargs:
        bgcolor: tuple, optional, (def: (0, 0, 0))
            Set the background color for both canvas (main canvas in
            which the brain is displayed and the canvas for the colorbar)
    """

    def __init__(self, bgcolor=(0, 0, 0)):
        """Init."""
        # Initialize main canvas:
        self.canvas = scene.SceneCanvas(keys='interactive', show=False, dpi=600,
                                        bgcolor=bgcolor, fullscreen=True,
                                        resizable=True, position=(0, 250))
        self.wc = self.canvas.central_widget.add_view()

        # Initialize colorbar canvas :
        self.cbcanvas = scene.SceneCanvas(keys='interactive', bgcolor=bgcolor,
                                          resizable=True, )
        self.cbwc = self.cbcanvas.central_widget.add_view()

        # Add axis (debugging):
        # self._axis = scene.visuals.XYZAxis()
        # self.wc.add(self._axis)

        # Visualization settings. The min/maxOpacity attributes are defined
        # because it seems that OpenGL have trouble with small opacity (usually
        # between 0 and 1). Defining min and max far away from 0 / 1 solve this
        # problem.
        self.minOpacity = -10000
        self.maxOpacity = 10000
