"""Main class for settings managment."""
from ..uiInit import AxisCanvas
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


__all__ = ['uiPanels']


class uiPanels(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # CHANNELS
        # =====================================================================
        # Create check buttons and panels for every channel :
        self._fcn_chanCheckAndWCreate()

        # =====================================================================
        # SPECTROGRAM
        # =====================================================================
        self._PanSpecViz.clicked.connect(self._fcn_specViz)
        self._specCanvas = AxisCanvas(axis=True, bgcolor=(1., 1., 1.),
                                      y_label='Spectrogram', x_label=None,
                                      name='Spectrogram', color='black',
                                      yargs={'text_color': 'black'},
                                      xargs={'text_color': 'black'})
        self._SpecLayout.addWidget(self._specCanvas.canvas.native)
        self._chanGrid.addWidget(self._SpecW, len(self._channels)+1, 0, 1, 1)

        # =====================================================================
        # SPECTROGRAM
        # =====================================================================
        self._PanHypViz.clicked.connect(self._fcn_hypViz)
        self._hypCanvas = AxisCanvas(axis=True, bgcolor=(1., 1., 1.),
                                     y_label='Hypnogram', x_label=None,
                                     name='Spectrogram', color='black',
                                     yargs={'text_color': 'black'},
                                     xargs={'text_color': 'black'})
        self._HypLayout.addWidget(self._hypCanvas.canvas.native)
        self._chanGrid.addWidget(self._HypW, len(self._channels)+2, 0, 1, 1)

    # =====================================================================
    # CHANNELS
    # =====================================================================
    def _fcn_chanCheckAndWCreate(self):
        """Create one checkbox and one widget/layout per channel."""
        # Empty list of checkbox and widgets/layouts :
        self._chanChecks = [0] * len(self._channels)
        self._chanWidget = self._chanChecks.copy()
        self._chanLayout = self._chanChecks.copy()
        self._chanCanvas = self._chanChecks.copy()
        # self._chanGrid.setSpacing(0)
        # Loop over channels :
        for i, k in enumerate(self._channels):
            # ============ CHECKBOX ============
            # Add a checkbox to the scrolling panel :
            self._chanChecks[i] = QtGui.QCheckBox(self._PanScrollChan)
            # Name checkbox with channel name :
            self._chanChecks[i].setObjectName(_fromUtf8("_CheckChan"+k))
            self._chanChecks[i].setText(k)
            # Add checkbox to the grid :
            self._PanChanLay.addWidget(self._chanChecks[i], i, 0, 1, 1)
            # Connect with the function :
            self._chanChecks[i].clicked.connect(self._fcn_chanViz)

            # ============ WIDGETS / LAYOUTS ============
            # Create a widget :
            self._chanWidget[i] = QtGui.QWidget(self.centralwidget)
            self._chanWidget[i].setMinimumSize(QtCore.QSize(0, 0))
            self._chanWidget[i].setObjectName(_fromUtf8("_widgetChan"+k))
            self._chanWidget[i].setVisible(False)
            vlay = QtGui.QVBoxLayout(self._chanWidget[i])
            vlay.setContentsMargins(9, 0, 9, 0)
            vlay.setSpacing(0)
            vlay.setObjectName(_fromUtf8("vlay"))
            # Create layout :
            self._chanLayout[i] = QtGui.QVBoxLayout()
            self._chanLayout[i].setSpacing(0)
            self._chanLayout[i].setObjectName(_fromUtf8("_LayoutChan"+k))
            vlay.addLayout(self._chanLayout[i])
            # Add widget to the grid :
            self._chanGrid.addWidget(self._chanWidget[i], i, 0, 1, 1)

            # ============ CANVAS ============
            # Create canvas :
            self._chanCanvas[i] = AxisCanvas(axis=True, bgcolor=(1., 1., 1.),
                                             y_label=k, x_label=None,
                                             name='Canvas_'+k, color='black',
                                             yargs={'text_color': 'black'},
                                             xargs={'text_color': 'black'})
            # Add the canvas to the layout :
            self._chanLayout[i].addWidget(self._chanCanvas[i].canvas.native)

        # Set first element checked and first panel visible :
        self._chanChecks[0].setChecked(True)
        self._chanWidget[0].setVisible(True)
        # Add vertical spacer :
        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Minimum)
        self._PanChanLay.addItem(spacer, i+1, 0, 1, 1)

    def _fcn_chanViz(self):
        """Control visible panels of channels."""
        for i, k in enumerate(self._chanChecks):
            viz = k.isChecked()
            self._chanWidget[i].setVisible(viz)
            if viz:
                self._chanCanvas[i].set_camera(self._chanCam)

    # =====================================================================
    # SPECTROGRAM
    # =====================================================================
    def _fcn_specViz(self):
        """Toggle visibility of the spectrogram panel."""
        viz = self._PanSpecViz.isChecked()
        self._PanSpecW.setEnabled(viz)
        self._PanSpecZoom.setEnabled(viz)
        self._SpecW.setVisible(viz)

    # =====================================================================
    # HYPNOGRAM
    # =====================================================================
    def _fcn_hypViz(self):
        """Toggle visibility of the spectrogram panel."""
        viz = self._PanHypViz.isChecked()
        self._PanHypZoom.setEnabled(viz)
        self._HypW.setVisible(viz)
