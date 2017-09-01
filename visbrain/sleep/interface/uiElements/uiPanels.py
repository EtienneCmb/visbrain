"""Main class for settings managment."""
from PyQt5 import QtCore, QtGui, QtWidgets

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
        self._addspace = '   '

        # =====================================================================
        # MAIN GRID :
        # =====================================================================
        self._chanGrid = QtWidgets.QGridLayout()
        self._chanGrid.setContentsMargins(-1, -1, -1, 6)
        self._chanGrid.setSpacing(3)
        self._chanGrid.setObjectName(_fromUtf8("_chanGrid"))
        self.gridLayout_21.addLayout(self._chanGrid, 0, 0, 1, 1)

        # =====================================================================
        # CHANNELS
        # =====================================================================
        # Create check buttons and panels for every channel :
        self._fcn_chanCheckAndWCreate()
        self._PanChanSelectAll.clicked.connect(self._fcn_SelectAllchan)
        self._PanChanDeselectAll.clicked.connect(self._fcn_DeselectAllchan)
        self._PanAmpAuto.clicked.connect(self._fcn_chanAutoAmp)
        self._PanAmpSym.clicked.connect(self._fcn_chanSymAmp)

        # =====================================================================
        # AMPLITUDES
        # =====================================================================
        # Save all current amplitudes :
        self._PanAllAmpMax.setValue(100.)
        self._ylims = np.zeros((len(self), 2), dtype=np.float32)
        self._fcn_updateAmpInfo()
        self._PanAllAmpMin.valueChanged.connect(self._fcn_allAmp)
        self._PanAllAmpMax.valueChanged.connect(self._fcn_allAmp)

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
        self._SpecW, self._SpecLayout = self._createCompatibleW("SpecW",
                                                                "SpecL")
        self._SpecLayout.addWidget(self._specCanvas.canvas.native)
        self._chanGrid.addWidget(self._SpecW, len(self) + 1, 1, 1, 1)
        # Add label :
        self._specLabel = QtWidgets.QLabel(self.centralwidget)
        self._specLabel.setText(self._addspace + self._channels[0])
        self._specLabel.setFont(self._font)
        self._chanGrid.addWidget(self._specLabel, len(self) + 1, 0, 1, 1)
        # Add list of colormaps :
        self._cmap_lst = mpl_cmap()
        self._PanSpecCmap.addItems(self._cmap_lst)
        self._PanSpecCmap.setCurrentIndex(self._cmap_lst.index(self._defcmap))
        # Add list of channels :
        self._PanSpecChan.addItems(self._channels)
        # Connect spectrogam properties :
        self._PanSpecApply.setEnabled(False)
        self._PanSpecApply.clicked.connect(self._fcn_specSetData)
        self._PanSpecNfft.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecStep.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecFstart.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecFend.valueChanged.connect(self._fcn_specCompat)
        self._PanSpecCon.valueChanged.connect(self._fcn_specSetData)
        self._PanSpecCmap.currentIndexChanged.connect(self._fcn_specSetData)
        self._PanSpecChan.currentIndexChanged.connect(self._fcn_specSetData)
        self._PanSpecCmapInv.clicked.connect(self._fcn_specSetData)

        # =====================================================================
        # HYPNOGRAM
        # =====================================================================
        self._hypCanvas = AxisCanvas(axis=self._ax, bgcolor=(1., 1., 1.),
                                     y_label=None, x_label=None,
                                     name='Hypnogram', color='black',
                                     yargs={'text_color': 'black'},
                                     xargs={'text_color': 'black'},
                                     fcn=[self.on_mouse_wheel])
        self._HypW, self._HypLayout = self._createCompatibleW("HypW", "HypL")
        self._HypLayout.addWidget(self._hypCanvas.canvas.native)
        self._chanGrid.addWidget(self._HypW, len(self) + 2, 1, 1, 1)
        # Add label :
        self._hypLabel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self._hypLabel)
        layout.setContentsMargins(0, 0, 0, 0)
        self._hypYLabels = []
        for k in self._href+['']:
            label = QtWidgets.QLabel()
            label.setText(self._addspace + k)
            label.setFont(self._font)
            layout.addWidget(label)
            self._hypYLabels.append(label)
        self._chanGrid.addWidget(self._hypLabel, len(self) + 2, 0, 1, 1)

        # =====================================================================
        # TOPOPLOT
        # =====================================================================
        # Main canvas for the spectrogram :
        self._topoCanvas = AxisCanvas(axis=self._ax, bgcolor=(1., 1., 1.),
                                      y_label=None, x_label=None,
                                      name='Topoplot', color='black',
                                      yargs={'text_color': 'black'},
                                      xargs={'text_color': 'black'})
        self._topoLayout.addWidget(self._topoCanvas.canvas.native)
        self._topoW.setVisible(False)
        self._PanTopoCmin.setValue(-.5)
        self._PanTopoCmax.setValue(.5)
        # Connect :
        self._PanTopoCmap.addItems(self._cmap_lst)
        self._PanTopoCmap.setCurrentIndex(self._cmap_lst.index('Spectral'))
        self._PanTopoCmin.setKeyboardTracking(False)
        self._PanTopoCmin.valueChanged.connect(self._fcn_topoSettings)
        self._PanTopoCmax.setKeyboardTracking(False)
        self._PanTopoRev.clicked.connect(self._fcn_topoSettings)
        self._PanTopoCmax.valueChanged.connect(self._fcn_topoSettings)
        self._PanTopoCmap.currentIndexChanged.connect(self._fcn_topoSettings)
        self._PanTopoDisp.currentIndexChanged.connect(self._fcn_topoSettings)
        self._PanTopoFmin.valueChanged.connect(self._fcn_topoSettings)
        self._PanTopoFmax.valueChanged.connect(self._fcn_topoSettings)
        self._PanTopoAutoClim.clicked.connect(self._fcn_topoSettings)
        self._PanTopoApply.clicked.connect(self._fcn_topoApply)

        # =====================================================================
        # TIME AXIS
        # =====================================================================
        # Create a unique time axis :
        self._TimeAxis = TimeAxis(xargs={'text_color': 'black'},
                                  x_label=None, name='TimeAxis',
                                  bgcolor=(1., 1., 1.), color='black',
                                  indic_color=self._indicol,
                                  fcn=[self.on_mouse_wheel])
        self._TimeAxisW, self._TimeLayout = self._createCompatibleW("TimeW",
                                                                    "TimeL")
        self._TimeLayout.addWidget(self._TimeAxis.canvas.native)
        self._TimeAxisW.setMaximumHeight(400)
        self._TimeAxisW.setMinimumHeight(50)
        self._chanGrid.addWidget(self._TimeAxisW, len(self) + 3, 1, 1, 1)
        # Add label :
        self._timeLabel = QtWidgets.QLabel(self.centralwidget)
        self._timeLabel.setText(self._addspace + 'Time')
        self._timeLabel.setFont(self._font)
        self._chanGrid.addWidget(self._timeLabel, len(self) + 3, 0, 1, 1)

    # =====================================================================
    # CHANNELS
    # =====================================================================
    def _createCompatibleW(self, nameWiget, nameLayout, visible=False):
        """This function create a widget and a layout."""
        Widget = QtWidgets.QWidget(self.centralwidget)
        Widget.setMinimumSize(QtCore.QSize(0, 0))
        Widget.setObjectName(_fromUtf8(nameWiget))
        Widget.setVisible(visible)
        vlay = QtWidgets.QVBoxLayout(Widget)
        vlay.setContentsMargins(9, 0, 9, 0)
        vlay.setSpacing(0)
        vlay.setObjectName(_fromUtf8("vlay"))
        # Create layout :
        Layout = QtWidgets.QVBoxLayout()
        Layout.setSpacing(0)
        Layout.setObjectName(_fromUtf8(nameLayout))
        vlay.addLayout(Layout)

        return Widget, Layout

    def _fcn_chanCheckAndWCreate(self):
        """Create one checkbox and one widget/layout per channel."""
        # Empty list of checkbox and widgets/layouts :
        self._chanChecks = [0] * len(self)
        self._yminSpin, self._ymaxSpin = [0] * len(self), [0] * len(self)
        self._chanWidget = [0] * len(self)
        self._chanLayout = [0] * len(self)
        self._chanCanvas = [0] * len(self)
        self._chanLabels = []
        self._amplitudeTxt = []

        # Define a vertical and horizontal spacers :
        vspacer = QtWidgets.QSpacerItem(20, 40,
                                        QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        hspacer = QtWidgets.QSpacerItem(40, 20,
                                        QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)

        # Loop over channels :
        for i, k in enumerate(self._channels):
            # ============ CHECKBOX ============
            # ----- MAIN CHECKBOX -----
            # Add a checkbox to the scrolling panel :
            self._chanChecks[i] = QtWidgets.QCheckBox(self._PanScrollChan)
            # Name checkbox with channel name :
            self._chanChecks[i].setObjectName(_fromUtf8("_CheckChan"+k))
            self._chanChecks[i].setText(k)
            self._chanChecks[i].setShortcut("Ctrl+"+str(i))
            # Add checkbox to the grid :
            self._PanChanLay.addWidget(self._chanChecks[i], i, 0, 1, 1)
            # Connect with the function :
            self._chanChecks[i].clicked.connect(self._fcn_chanViz)

            # ----- LABEL/ Y-MIN / Y-MAX -----
            fact = 5.
            # Add amplitude label :
            amplitude = QtWidgets.QLabel(self._PanScrollChan)
            amplitude.setText('Amp')
            self._amplitudeTxt.append(amplitude)
            self._PanChanLay.addWidget(amplitude, i, 2, 1, 1)
            # Add ymin spinbox :
            self._yminSpin[i] = QtWidgets.QDoubleSpinBox(self._PanScrollChan)
            self._yminSpin[i].setDecimals(1)
            self._yminSpin[i].setMinimum(self['min'][i])
            self._yminSpin[i].setMaximum(self['max'][i])
            self._yminSpin[i].setProperty("value", -int(fact * self['std'][i]))
            self._yminSpin[i].setSingleStep(1.)
            self._PanChanLay.addWidget(self._yminSpin[i], i, 3, 1, 1)
            # Add ymax spinbox :
            self._ymaxSpin[i] = QtWidgets.QDoubleSpinBox(self._PanScrollChan)
            self._ymaxSpin[i].setDecimals(1)
            self._ymaxSpin[i].setMinimum(self['min'][i])
            self._ymaxSpin[i].setMaximum(self['max'][i])
            self._ymaxSpin[i].setSingleStep(1.)
            self._ymaxSpin[i].setProperty("value", int(fact * self['std'][i]))
            self._PanChanLay.addWidget(self._ymaxSpin[i], i, 4, 1, 1)
            # Connect buttons :
            self._yminSpin[i].valueChanged.connect(self._fcn_chanAmplitude)
            self._ymaxSpin[i].valueChanged.connect(self._fcn_chanAmplitude)

            # ============ WIDGETS / LAYOUTS ============
            # Create a widget :
            self._chanWidget[i], self._chanLayout[
                i] = self._createCompatibleW("_widgetChan"+k, "_LayoutChan"+k)
            self._chanGrid.addWidget(self._chanWidget[i], i, 1, 1, 1)
            # Add channel label :
            self._chanLabels.append(QtWidgets.QLabel(self.centralwidget))
            self._chanLabels[i].setText(self._addspace + k)
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
    def _fcn_chanAutoAmp(self):
        """Use automatic amplitudes."""
        viz = not self._PanAmpAuto.isChecked()
        # Set auto-amp :
        self._chan.autoamp = not viz
        # Disable all amplitude related buttons :
        for k in range(len(self._channels)):
            self._amplitudeTxt[k].setEnabled(viz)
            self._yminSpin[k].setEnabled(viz)
            self._ymaxSpin[k].setEnabled(viz)
        self._PanAllAmpMin.setEnabled(viz)
        self._PanAllAmpMax.setEnabled(viz)
        self._PanAmpSym.setEnabled(viz)
        # Finaly, update :
        if viz:
            self._fcn_chanAmplitude()
        else:
            self._chan.update()

    def _fcn_chanSymAmp(self):
        """Use symetric amplitudes."""
        viz = not self._PanAmpSym.isChecked()
        # Hide amplitude min for all chan :
        for k in range(len(self._channels)):
            self._yminSpin[k].setVisible(viz)
            if not viz:
                self._ymaxSpin[k].setMinimum(.1)
            else:
                self._ymaxSpin[k].setMinimum(self['min'][k])
        self._PanAllAmpMin.setVisible(viz)
        if not viz:
            self._PanAllAmpMax.setMinimum(.1)
        else:
            self._PanAllAmpMax.setMinimum(self['min'].min())
        self._fcn_chanAmplitude()

    def _fcn_chanAmplitude(self):
        """Change amplitude of each channel."""
        # Loop over spinbox and update camera rect :
        for k, (m, M) in enumerate(zip(self._yminSpin, self._ymaxSpin)):
            # Use either symetric / non-symetric amplitudes :
            if self._PanAmpSym.isChecked():
                self._ylims[k, :] = np.array([-M.value(), M.value()])
            else:
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
    def _fcn_specSetData(self):
        """Set data to the spectrogram."""
        # Get nfft and overlap :
        nfft, over = self._PanSpecNfft.value(), self._PanSpecStep.value()
        # Get starting / ending frequency :
        fstart, fend = self._PanSpecFstart.value(), self._PanSpecFend.value()
        # Get contraste :
        contraste = self._PanSpecCon.value()
        # Get colormap :
        cmap = str(self._PanSpecCmap.currentText())
        # Get channel to get spectrogram :
        chan = self._PanSpecChan.currentIndex()
        # Get reversed colormap :
        if self._PanSpecCmapInv.isChecked():
            cmap += '_r'
        self._specLabel.setText(self._addspace + self._channels[chan])
        # Set data :
        self._spec.set_data(self._sf, self._data[chan, ...], self._time,
                            nfft=nfft, overlap=over, fstart=fstart, fend=fend,
                            cmap=cmap, contraste=contraste)
        # Set apply button disable :
        self._PanSpecApply.setEnabled(False)

    def _fcn_specCompat(self):
        """Check compatibility between spectro parameters."""
        # Get nfft and overlap :
        nfft, _ = self._PanSpecNfft.value(), self._PanSpecStep.value()
        # Get starting / ending frequency :
        _, fend = self._PanSpecFstart.value(), self._PanSpecFend.value()

        self._PanSpecStep.setMaximum(nfft * .99)
        self._PanSpecFend.setMaximum(self._sf / 2)
        self._PanSpecFstart.setMaximum(fend - 0.99)
        # Set apply button enable :
        self._PanSpecApply.setEnabled(True)

    # =====================================================================
    # TOPOPLOT
    # =====================================================================
    def _fcn_topoSettings(self):
        """Manage colormap of the topoplot."""
        # ============== TYPE ==============
        dispas = self._PanTopoDisp.currentText()
        self._topo.filt = True
        self._topo.dispas = dispas
        self._topo.fstart = self._PanTopoFmin.value()
        self._topo.fend = self._PanTopoFmax.value()

        # ============== LIMITS / COLORMAP ==============
        # Get limits :
        if self._PanTopoAutoClim.isChecked():
            clim = None
            self._PanTopoClimW.setEnabled(False)
        else:
            self._PanTopoClimW.setEnabled(True)
            cmin = self._PanTopoCmin.value()
            cmax = self._PanTopoCmax.value()
            clim = (float(cmin), float(cmax))
        # Get and set colormap :
        rv = self._PanTopoRev.isChecked()
        cmap = self._PanTopoCmap.currentText() + rv * '_r'

        # Send data :
        self._topo._cmap = cmap
        self._topo._clim = clim
        self._topo._cblabel = dispas
        self._topo.set_sleep_topo()

        # Finally, enable apply button :
        self._PanTopoApply.setEnabled(True)

    def _fcn_topoApply(self):
        """Apply topo settings."""
        self._fcn_sliderMove()
        self._PanTopoApply.setEnabled(False)
