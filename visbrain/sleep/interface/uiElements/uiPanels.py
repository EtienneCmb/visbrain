"""Main class for settings managment."""
from PyQt4 import QtCore, QtGui

import numpy as np

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
        # Bold font :
        self._font = QtGui.QFont()
        self._font.setBold(True)
        # =====================================================================
        # CHANNELS
        # =====================================================================
        # Create check buttons and panels for every channel :
        self._fcn_chanCheckAndWCreate()
        self._PanChanSelectAll.clicked.connect(self._fcn_SelectAllchan)
        self._PanChanDeselectAll.clicked.connect(self._fcn_DeselectAllchan)

        # =====================================================================
        # AMPLITUDES
        # =====================================================================
        # Save all current amplitudes :
        self._ylims = np.zeros((len(self), 2), dtype=np.float32)
        self._PanAllAmpMin.valueChanged.connect(self._fcn_allAmp)
        self._PanAllAmpMax.valueChanged.connect(self._fcn_allAmp)
        self._fcn_updateAmpInfo()

        # =====================================================================
        # SPECTROGRAM
        # =====================================================================
        # Main canvas for the spectrogram :
        self._specCanvas = AxisCanvas(axis=self._ax, bgcolor=(1., 1., 1.),
                                      y_label=None, x_label=None,
                                      name='Spectrogram', color='black',
                                      yargs={'text_color': 'black'},
                                      xargs={'text_color': 'black'},
                                      fcn=[self.on_mouse_wheel])
        self._SpecLayout.addWidget(self._specCanvas.canvas.native)
        self._chanGrid.addWidget(self._SpecW, len(self) + 1, 1, 1, 1)
        # Add label :
        self._specLabel = QtGui.QLabel(self.centralwidget)
        self._specLabel.setText(self._channels[0])
        self._specLabel.setFont(self._font)
        self._chanGrid.addWidget(self._specLabel, len(self) + 1, 0, 1, 1)
        # Add list of colormaps :
        self._cmap_lst = mpl_cmap()
        self._PanSpecCmap.addItems(self._cmap_lst)
        self._PanSpecCmap.setCurrentIndex(self._cmap_lst.index('rainbow'))
        # Add list of channels :
        self._PanSpecChan.addItems(self._channels)
        # Connect spectrogam properties :
        self._PanSpecApply.setEnabled(False)
        self._PanSpecViz.clicked.connect(self._fcn_specViz)
        self._PanSpecApply.clicked.connect(self._fcn_specSetData)
        self._PanSpecNfft.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecStep.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecFstart.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecCon.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecFend.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecCmap.currentIndexChanged.connect(self._fcn_specSetData)
        self._PanSpecChan.currentIndexChanged.connect(self._fcn_specSetData)

        # =====================================================================
        # HYPNOGRAM
        # =====================================================================
        self._PanHypViz.clicked.connect(self._fcn_hypViz)
        self._hypCanvas = AxisCanvas(axis=self._ax, bgcolor=(1., 1., 1.),
                                     y_label=None, x_label=None,
                                     name='Spectrogram', color='black',
                                     yargs={'text_color': 'black'},
                                     xargs={'text_color': 'black'},
                                     fcn=[self.on_mouse_wheel])
        self._HypLayout.addWidget(self._hypCanvas.canvas.native)
        self._chanGrid.addWidget(self._HypW, len(self) + 2, 1, 1, 1)
        # Add label :
        self._hypLabel = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(self._hypLabel)
        layout.setMargin(0)
        layout.setSpacing(0)
        self._hypYLabels = []
        for k in ['Art', 'Wake', 'N1', 'N2', 'N3', 'REM', '']:
            label = QtGui.QLabel()
            label.setText(k)
            label.setFont(self._font)
            layout.addWidget(label)
            self._hypYLabels.append(label)
        self._chanGrid.addWidget(self._hypLabel, len(self) + 2, 0, 1, 1)

        # =====================================================================
        # TIME AXIS
        # =====================================================================
        self._PanTimeViz.clicked.connect(self._fcn_timeViz)
        # Create a unique time axis :
        self._TimeAxis = TimeAxis(xargs={'text_color': 'black'},
                                  x_label=None,
                                  bgcolor=(1., 1., 1.), color='black',
                                  indic_color=self._indicol,
                                  fcn=[self.on_mouse_wheel])
        self._TimeLayout.addWidget(self._TimeAxis.canvas.native)
        self._TimeAxisW.setMaximumHeight(400)
        self._TimeAxisW.setMinimumHeight(50)
        self._chanGrid.addWidget(self._TimeAxisW, len(self) + 3, 1, 1, 1)
        # Add label :
        self._timeLabel = QtGui.QLabel(self.centralwidget)
        self._timeLabel.setText('Time')
        self._timeLabel.setFont(self._font)
        self._chanGrid.addWidget(self._timeLabel, len(self) + 3, 0, 1, 1)

        # =====================================================================
        # INDICATORS
        # =====================================================================
        self._PanSpecIndic.clicked.connect(self._fcn_indicviz)
        self._PanHypIndic.clicked.connect(self._fcn_indicviz)
        self._PanTimeIndic.clicked.connect(self._fcn_indicviz)

    # =====================================================================
    # CHANNELS
    # =====================================================================
    def _fcn_chanCheckAndWCreate(self):
        """Create one checkbox and one widget/layout per channel."""
        # Empty list of checkbox and widgets/layouts :
        self._chanChecks = [0] * len(self)
        self._yminSpin, self._ymaxSpin = [0] * len(self), [0] * len(self)
        self._chanWidget = self._chanChecks.copy()
        self._chanLayout = self._chanChecks.copy()
        self._chanCanvas = self._chanChecks.copy()
        self._chanLabels = []

        # Define a vertical and horizontal spacers :
        vspacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Minimum)
        hspacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Minimum)

        # Loop over channels :
        for i, k in enumerate(self._channels):
            # ============ CHECKBOX ============
            # ----- MAIN CHECKBOX -----
            # Add a checkbox to the scrolling panel :
            self._chanChecks[i] = QtGui.QCheckBox(self._PanScrollChan)
            # Name checkbox with channel name :
            self._chanChecks[i].setObjectName(_fromUtf8("_CheckChan"+k))
            self._chanChecks[i].setText(k)
            # Add checkbox to the grid :
            self._PanChanLay.addWidget(self._chanChecks[i], i, 0, 1, 1)
            # Add horizontal spacer :
            self._PanChanLay.addItem(hspacer, i, 1, 1, 1)
            # Connect with the function :
            self._chanChecks[i].clicked.connect(self._fcn_chanViz)

            # ----- Y-MIN / Y-MAX -----
            fact = 5.
            # Add amplitude label :
            amplitude = QtGui.QLabel(self._PanScrollChan)
            amplitude.setText('Amp')
            self._PanChanLay.addWidget(amplitude, i, 2, 1, 1)
            # Add ymin spinbox :
            self._yminSpin[i] = QtGui.QDoubleSpinBox(self._PanScrollChan)
            self._yminSpin[i].setDecimals(1)
            self._yminSpin[i].setMinimum(self['min'][i])
            self._yminSpin[i].setMaximum(self['max'][i])
            self._yminSpin[i].setProperty("value", -int(fact * self['std'][i]))
            self._yminSpin[i].setSingleStep(self['dist'][i] / 10.)
            self._PanChanLay.addWidget(self._yminSpin[i], i, 3, 1, 1)
            # Add ymax spinbox :
            self._ymaxSpin[i] = QtGui.QDoubleSpinBox(self._PanScrollChan)
            self._ymaxSpin[i].setDecimals(1)
            self._ymaxSpin[i].setMinimum(self['min'][i])
            self._ymaxSpin[i].setMaximum(self['max'][i])
            self._ymaxSpin[i].setSingleStep(self['dist'][i] / 10.)
            self._ymaxSpin[i].setProperty("value", int(fact * self['std'][i]))
            self._PanChanLay.addWidget(self._ymaxSpin[i], i, 4, 1, 1)
            # Connect buttons :
            self._yminSpin[i].valueChanged.connect(self._fcn_chanAmplitude)
            self._ymaxSpin[i].valueChanged.connect(self._fcn_chanAmplitude)

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
            self._chanLabels[i].setFont(self._font)
            self._chanLabels[i].setVisible(False)
            self._chanGrid.addWidget(self._chanLabels[i], i, 0, 1, 1)

            # ============ CANVAS ============
            # Create canvas :
            self._chanCanvas[i] = AxisCanvas(axis=self._ax,
                                             bgcolor=(1., 1., 1.),
                                             y_label=None, x_label=None,
                                             name='Canvas_'+k, color='black',
                                             yargs={'text_color': 'black'},
                                             xargs={'text_color': 'black'},
                                             fcn=[self.on_mouse_wheel])
            # Add the canvas to the layout :
            self._chanLayout[i].addWidget(self._chanCanvas[i].canvas.native)

        self._PanChanLay.addItem(vspacer, i+1, 0, 1, 1)
        self._chanGrid.addItem(hspacer, i+4, 1, 1, 1)

    # =====================================================================
    # AMPLITUDES
    # =====================================================================
    def _fcn_chanAmplitude(self):
        """Change amplitude of each channel."""
        # Loop over spinbox and update camera rect :
        for k, (m, M) in enumerate(zip(self._yminSpin, self._ymaxSpin)):
            self._ylims[k, :] = np.array([m.value(), M.value()])
            rect = (self._chan.x[0], self._ylims[k, 0],
                    self._chan.x[1] - self._chan.x[0],
                    self._ylims[k, 1] - self._ylims[k, 0])
            self._chanCam[k].rect = rect

    def _fcn_allAmp(self):
        """Set all channel amplitudes."""
        for k, (m, M) in enumerate(zip(self._yminSpin, self._ymaxSpin)):
            m.setValue(self._PanAllAmpMin.value())
            M.setValue(self._PanAllAmpMax.value())
        self._fcn_chanAmplitude()

    def _fcn_updateAmpInfo(self):
        """Update informations about amplitudes."""
        self._get_dataInfo()
        self._PanAllAmpMin.setMinimum(self['min'].min())
        self._PanAllAmpMin.setMaximum(self['max'].max())
        self._PanAllAmpMax.setMinimum(self['min'].min())
        self._PanAllAmpMax.setMaximum(self['max'].max())

    # =====================================================================
    # CHANNEL SELECTION
    # =====================================================================
    def _fcn_chanViz(self):
        """Control visible panels of channels."""
        for i, k in enumerate(self._chanChecks):
            viz = k.isChecked()
            self._chanWidget[i].setVisible(viz)
            self._chanLabels[i].setVisible(viz)
            self._chan.visible[i] = viz
            if viz:
                self._chanCanvas[i].set_camera(self._chanCam[i])
        self._chan.update()

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

    def canvas_isVisible(self, k):
        """Find if canvas k is visible.

        Args:
            k: int
                Index of the canvas.

        Return:
            visible: bool
                A boolean value indicating if the canvas is visible.
        """
        return self._chanWidget[k].isVisible()

    def canvas_setVisible(self, k, value):
        """Set the visibility of the canvas k to value.

        Args:
            k: int
                Index of the canvas.

            value: bool
                Boolean value if the canvas has to be visible.
        """
        self._chanChecks[k].setChecked(value)
        self._chanWidget[k].setVisible(value)
        self._chanLabels[k].setVisible(value)
        self._chanCanvas[k].set_camera(self._chanCam[k])

    # =====================================================================
    # SPECTROGRAM
    # =====================================================================
    def _fcn_specViz(self):
        """Toggle visibility of the spectrogram panel."""
        viz = self._PanSpecViz.isChecked()
        self._PanSpecW.setEnabled(viz)
        self._SpecW.setVisible(viz)
        self._specLabel.setVisible(viz)
        self._PanSpecIndic.setEnabled(viz)

    def _fcn_specSetData(self):
        """Set data to the spectrogram."""
        # Get nfft and overlap :
        nfft, over = self._PanSpecNfft.value(), self._PanSpecStep.value()
        # Get starting / ending frequency :
        fstart, fend = self._PanSpecFstart.value(), self._PanSpecFend.value()
        # Get contraste :
        contraste = self._PanSpecCon.value()
        # Get colormap :
        cmap = self._PanSpecCmap.currentText()
        # Get channel to get spectrogram :
        chan = self._PanSpecChan.currentIndex()
        self._specLabel.setText(self._channels[chan])
        # Set data :
        self._spec.set_data(self._sf, self._data[chan, ...], self._time,
                            nfft=nfft, overlap=over, fstart=fstart, fend=fend,
                            cmap=cmap, contraste=contraste)
        # Set apply button disable :
        self._PanSpecApply.setEnabled(False)

    def _fcn_specCompat(self):
        """Check compatibility between spectro parameters."""
        # Get nfft and overlap :
        nfft, over = self._PanSpecNfft.value(), self._PanSpecStep.value()
        # Get starting / ending frequency :
        fstart, fend = self._PanSpecFstart.value(), self._PanSpecFend.value()

        self._PanSpecStep.setMaximum(nfft * .99)
        self._PanSpecFend.setMaximum(self._sf / 2)
        self._PanSpecFstart.setMaximum(fend - 0.99)
        # Set apply button enable :
        self._PanSpecApply.setEnabled(True)

    # =====================================================================
    # HYPNOGRAM
    # =====================================================================
    def _fcn_hypViz(self):
        """Toggle visibility of the spectrogram panel."""
        viz = self._PanHypViz.isChecked()
        self._HypW.setVisible(viz)
        self._hypLabel.setVisible(viz)
        self._PanHypIndic.setEnabled(viz)

    # =====================================================================
    # TIME AXIS
    # =====================================================================
    def _fcn_timeViz(self):
        """Toggle visibility of the time panel."""
        viz = self._PanTimeViz.isChecked()
        self._TimeAxisW.setVisible(viz)
        self._PanTimeIndic.setEnabled(viz)
        self._timeLabel.setVisible(viz)

    # =====================================================================
    # INDICATORS
    # =====================================================================
    def _fcn_indicviz(self):
        """Toggle indicator visibility."""
        self._specInd.mesh.visible = self._PanSpecIndic.isChecked()
        self._hypInd.mesh.visible = self._PanHypIndic.isChecked()
        self._TimeAxis.mesh.visible = self._PanTimeIndic.isChecked()
        self._fcn_sliderMove()
