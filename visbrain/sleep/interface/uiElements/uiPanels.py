"""Main class for settings managment."""
from PyQt4 import QtCore, QtGui

from ..uiInit import AxisCanvas, TimeAxis
from ....utils import mpl_cmap

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
        self._PanChanSelectAll.clicked.connect(self._fcn_SelectAllchan)
        self._PanChanDeselectAll.clicked.connect(self._fcn_DeselectAllchan)

        # =====================================================================
        # SPECTROGRAM
        # =====================================================================
        # Main canvas for the spectrogram :
        self._specCanvas = AxisCanvas(axis=False, bgcolor=(1., 1., 1.),
                                      y_label='Spectrogram', x_label=None,
                                      name='Spectrogram', color='black',
                                      yargs={'text_color': 'black'},
                                      xargs={'text_color': 'black'})
        self._SpecLayout.addWidget(self._specCanvas.canvas.native)
        self._chanGrid.addWidget(self._SpecW, len(self) + 1, 1, 1, 1)
        # Add label :
        self._specLabel = QtGui.QLabel(self.centralwidget)
        self._specLabel.setText(self._channels[0])
        self._chanGrid.addWidget(self._specLabel, len(self) + 1, 0, 1, 1)
        # Add list of colormaps :
        self._cmap_lst = mpl_cmap()
        self._PanSpecCmap.addItems(self._cmap_lst)
        self._PanSpecCmap.setCurrentIndex(self._cmap_lst.index('viridis'))
        # Add list of channels :
        self._PanSpecChan.addItems(self._channels)
        # Connect spectrogam properties :
        self._PanSpecViz.clicked.connect(self._fcn_specViz)
        self._PanSpecNfft.valueChanged.connect(self._fcn_specSetData)
        self._PanSpecStep.valueChanged.connect(self._fcn_specSetData)
        self._PanSpecFstart.valueChanged.connect(self._fcn_specSetData)
        self._PanSpecFend.valueChanged.connect(self._fcn_specSetData)
        self._PanSpecCmap.currentIndexChanged.connect(self._fcn_specSetData)
        self._PanSpecChan.currentIndexChanged.connect(self._fcn_specSetData)

        # =====================================================================
        # HYPNOGRAM
        # =====================================================================
        self._PanHypViz.clicked.connect(self._fcn_hypViz)
        self._hypCanvas = AxisCanvas(axis=False, bgcolor=(1., 1., 1.),
                                     y_label='Hypnogram', x_label=None,
                                     name='Spectrogram', color='black',
                                     yargs={'text_color': 'black'},
                                     xargs={'text_color': 'black'})
        self._HypLayout.addWidget(self._hypCanvas.canvas.native)
        self._chanGrid.addWidget(self._HypW, len(self) + 2, 1, 1, 1)
        # Add label :
        self._hypLabel = QtGui.QLabel(self.centralwidget)
        self._hypLabel.setText('Hypno')
        self._chanGrid.addWidget(self._hypLabel, len(self) + 2, 0,
                                 1, 1)

        # =====================================================================
        # TIME AXIS
        # =====================================================================
        self._PanTimeViz.clicked.connect(self._fcn_timeViz)
        # Create a unique time axis :
        self._TimeAxis = TimeAxis(xargs={'text_color': 'black'},
                                  x_label='Time (seconds)',
                                  bgcolor=(1., 1., 1.), color='black',)
        self._TimeLayout.addWidget(self._TimeAxis.canvas.native)
        self._chanGrid.addWidget(self._TimeAxisW, len(self) + 3, 1,
                                 1, 1)

    # =====================================================================
    # CHANNELS
    # =====================================================================
    def _fcn_chanCheckAndWCreate(self):
        """Create one checkbox and one widget/layout per channel."""
        # Empty list of checkbox and widgets/layouts :
        self._chanChecks = [0] * len(self)
        self._chanWidget = self._chanChecks.copy()
        self._chanLayout = self._chanChecks.copy()
        self._chanCanvas = self._chanChecks.copy()
        self._chanLabels = []
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
            self._chanGrid.addWidget(self._chanWidget[i], i, 1, 1, 1)
            # Add channel label :
            self._chanLabels.append(QtGui.QLabel(self.centralwidget))
            self._chanLabels[i].setText(k)
            self._chanLabels[i].setVisible(False)
            self._chanGrid.addWidget(self._chanLabels[i], i, 0, 1, 1)

            # ============ CANVAS ============
            # Create canvas :
            self._chanCanvas[i] = AxisCanvas(axis=False, bgcolor=(1., 1., 1.),
                                             y_label=k, x_label=None,
                                             name='Canvas_'+k, color='black',
                                             yargs={'text_color': 'black'},
                                             xargs={'text_color': 'black'},)
            # Add the canvas to the layout :
            self._chanLayout[i].addWidget(self._chanCanvas[i].canvas.native)

        # Set first element checked and first panel visible :
        self._chanChecks[0].setChecked(True)
        # self._chanWidget[0].setVisible(True)
        # Add vertical spacer :
        # Define a vertical and horizontal spacers :
        vspacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Minimum)
        hspacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Minimum)
        self._PanChanLay.addItem(vspacer, i+1, 0, 1, 1)
        self._chanGrid.addItem(hspacer, i+4, 1, 1, 1)

    def _fcn_chanViz(self):
        """Control visible panels of channels."""
        for i, k in enumerate(self._chanChecks):
            viz = k.isChecked()
            self._chanWidget[i].setVisible(viz)
            self._chanLabels[i].setVisible(viz)
            if viz:
                self._chanCanvas[i].set_camera(self._chanCam[i])

    def _fcn_SelectAllchan(self):
        """Select all channels."""
        for k in self._chanChecks:
            k.setChecked(True)
        self._fcn_chanViz()

    def _fcn_DeselectAllchan(self):
        """De-select all channels."""
        for k in self._chanChecks:
            k.setChecked(False)
        self._fcn_chanViz()

    # =====================================================================
    # SPECTROGRAM
    # =====================================================================
    def _fcn_specViz(self):
        """Toggle visibility of the spectrogram panel."""
        viz = self._PanSpecViz.isChecked()
        self._PanSpecW.setEnabled(viz)
        self._PanSpecZoom.setEnabled(viz)
        self._SpecW.setVisible(viz)
        self._specLabel.setVisible(viz)

    def _fcn_specSetData(self):
        """Set data to the spectrogram."""
        # Get nfft and step :
        nfft, step = self._PanSpecNfft.value(), self._PanSpecStep.value()
        # Get starting / ending frequency :
        fstart, fend = self._PanSpecFstart.value(), self._PanSpecFend.value()
        # Get colormap :
        cmap = self._PanSpecCmap.currentText()
        # Get channel to get spectrogram :
        chan = self._PanSpecChan.currentIndex()
        self._specLabel.setText(self._channels[chan])
        # Set data :
        self._spec.set_data(self._sf, self._data[chan, ...], nfft=nfft,
                            step=step, fstart=fstart, fend=fend, cmap=cmap)
        # Update camera :
        self._specCam.rect = self._spec.rect

    # =====================================================================
    # HYPNOGRAM
    # =====================================================================
    def _fcn_hypViz(self):
        """Toggle visibility of the spectrogram panel."""
        viz = self._PanHypViz.isChecked()
        self._PanHypZoom.setEnabled(viz)
        self._HypW.setVisible(viz)
        self._hypLabel.setVisible(viz)

    def _fcn_timeViz(self):
        """Toggle visibility of the time panel."""
        viz = self._PanTimeViz.isChecked()
        self._TimeAxisW.setVisible(viz)
