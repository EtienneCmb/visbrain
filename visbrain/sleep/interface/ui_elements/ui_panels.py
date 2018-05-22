"""Main class for settings managment."""
from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np

from visbrain.io.dependencies import is_lspopt_installed

from ..ui_init import AxisCanvas, TimeAxis
from ....utils import mpl_cmap, color2vb
from ....config import PROFILER

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):  # noqa
        """From utf8 pyqt function."""
        return s


class UiPanels(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # Bold font :
        self._font = QtGui.QFont()
        self._font.setBold(True)
        self._addspace = '   '
        self._pan_pick.currentIndexChanged.connect(self._fcn_pan_pick)

        # =====================================================================
        # MAIN GRID :
        # =====================================================================
        self._chanGrid = QtWidgets.QGridLayout()
        self._chanGrid.setContentsMargins(-1, -1, -1, 6)
        self._chanGrid.setSpacing(2)
        self._chanGrid.setObjectName(_fromUtf8("_chanGrid"))
        self.gridLayout_21.addLayout(self._chanGrid, 0, 0, 1, 1)
        PROFILER("Channel grid", level=2)

        # =====================================================================
        # CHANNELS
        # =====================================================================
        # Create check buttons and panels for every channel :
        self._fcn_chan_check_and_create_w()
        self._PanChanSelectAll.clicked.connect(self._fcn_select_all_chan)
        self._PanChanDeselectAll.clicked.connect(self._fcn_deselect_all_chan)
        self._PanAmpAuto.clicked.connect(self._fcn_chan_auto_amp)
        self._PanAmpSym.clicked.connect(self._fcn_chan_sym_amp)
        self._channels_lw.valueChanged.connect(self._fcn_chan_set_lw)
        self._channels_alias.clicked.connect(self._fcn_chan_antialias)
        PROFILER("Channel canvas, widgets and buttons", level=2)

        # =====================================================================
        # AMPLITUDES
        # =====================================================================
        # Save all current amplitudes :
        self._PanAllAmpMax.setValue(100.)
        self._ylims = np.zeros((len(self), 2), dtype=np.float32)
        self._fcn_update_amp_info()
        self._PanAllAmpMin.valueChanged.connect(self._fcn_all_amp)
        self._PanAllAmpMax.valueChanged.connect(self._fcn_all_amp)
        PROFILER("Channel amplitudes", level=2)

        # =====================================================================
        # SPECTROGRAM
        # =====================================================================
        # Main canvas for the spectrogram :
        self._specCanvas = AxisCanvas(axis=self._ax, name='Spectrogram',
                                      fcn=[self.on_mouse_wheel])
        self._SpecW, self._SpecLayout = self._create_compatible_w("SpecW",
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
        # Disable multitaper option if not is_lspopt_installed
        self._PanSpecMethod.model().item(2).setEnabled(is_lspopt_installed())
        # Connect spectrogam properties :
        self._PanSpecApply.setEnabled(False)
        self._PanSpecApply.clicked.connect(self._fcn_spec_set_data)
        self._PanSpecNfft.valueChanged.connect(self._fcn_spec_compat)
        self._PanSpecStep.valueChanged.connect(self._fcn_spec_compat)
        self._PanSpecFstart.valueChanged.connect(self._fcn_spec_compat)
        self._PanSpecFend.valueChanged.connect(self._fcn_spec_compat)
        self._PanSpecCon.valueChanged.connect(self._fcn_spec_compat)
        self._PanSpecCmap.currentIndexChanged.connect(self._fcn_spec_compat)
        self._PanSpecChan.currentIndexChanged.connect(self._fcn_spec_compat)
        self._PanSpecMethod.currentIndexChanged.connect(self._fcn_spec_compat)
        self._PanSpecCmapInv.clicked.connect(self._fcn_spec_compat)
        self._PanSpecNorm.currentIndexChanged.connect(self._fcn_spec_compat)
        self._PanSpecInterp.currentIndexChanged.connect(self._fcn_spec_interp)
        PROFILER("Spectrogram", level=2)

        # =====================================================================
        # HYPNOGRAM
        # =====================================================================
        self._hypCanvas = AxisCanvas(axis=self._ax, name='Hypnogram',
                                     fcn=[self.on_mouse_wheel], use_pad=True)
        self._HypW, self._HypLayout = self._create_compatible_w("HypW", "HypL")
        self._HypLayout.addWidget(self._hypCanvas.canvas.native)
        self._chanGrid.addWidget(self._HypW, len(self) + 2, 1, 1, 1)
        # Add label :
        self._hypLabel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self._hypLabel)
        layout.setContentsMargins(0, 0, 0, 0)
        self._hypYLabels = []
        for k in [''] + self._href + ['']:
            label = QtWidgets.QLabel()
            label.setText(self._addspace + k)
            label.setFont(self._font)
            layout.addWidget(label)
            self._hypYLabels.append(label)
        self._chanGrid.addWidget(self._hypLabel, len(self) + 2, 0, 1, 1)
        PROFILER("Hypnogram", level=2)
        # Connect :
        self._PanHypnoReset.clicked.connect(self._fcn_hypno_clean)
        self._PanHypnoLw.valueChanged.connect(self._fcn_set_hypno_lw)
        self._PanHypnoColor.clicked.connect(self._fcn_set_hypno_color)

        # =====================================================================
        # TOPOPLOT
        # =====================================================================
        # Main canvas for the spectrogram :
        self._topoCanvas = AxisCanvas(axis=False, name='Topoplot')
        self._topoLayout.addWidget(self._topoCanvas.canvas.native)
        self._topoW.setVisible(False)
        self._PanTopoCmin.setValue(-.5)
        self._PanTopoCmax.setValue(.5)
        # Connect :
        self._PanTopoCmap.addItems(self._cmap_lst)
        self._PanTopoCmap.setCurrentIndex(self._cmap_lst.index('Spectral'))
        self._PanTopoCmin.setKeyboardTracking(False)
        self._PanTopoCmin.valueChanged.connect(self._fcn_topo_settings)
        self._PanTopoCmax.setKeyboardTracking(False)
        self._PanTopoRev.clicked.connect(self._fcn_topo_settings)
        self._PanTopoCmax.valueChanged.connect(self._fcn_topo_settings)
        self._PanTopoCmap.currentIndexChanged.connect(self._fcn_topo_settings)
        self._PanTopoDisp.currentIndexChanged.connect(self._fcn_topo_settings)
        self._PanTopoFmin.valueChanged.connect(self._fcn_topo_settings)
        self._PanTopoFmax.valueChanged.connect(self._fcn_topo_settings)
        self._PanTopoAutoClim.clicked.connect(self._fcn_topo_settings)
        self._PanTopoApply.clicked.connect(self._fcn_topo_apply)
        PROFILER("Topoplot", level=2)

        # =====================================================================
        # TIME AXIS
        # =====================================================================
        # Create a unique time axis :
        self._TimeAxis = TimeAxis(axis=self._ax, name='TimeAxis',
                                  indic_color=self._indicol,
                                  fcn=[self.on_mouse_wheel])
        self._TimeAxisW, self._TimeLayout = self._create_compatible_w("TimeW",
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
        PROFILER("Time axis", level=2)

    # =====================================================================
    # CHANNELS
    # =====================================================================
    def _fcn_pan_pick(self):
        """Change the panel."""
        idx = int(self._pan_pick.currentIndex())
        self._stacked_panels.setCurrentIndex(idx)

    def _create_compatible_w(self, name_wiget, name_layout, visible=False):
        """Create a widget and a layout."""
        Widget = QtWidgets.QWidget(self.centralwidget)  # noqa
        Widget.setMinimumSize(QtCore.QSize(0, 0))
        Widget.setObjectName(_fromUtf8(name_wiget))
        Widget.setVisible(visible)
        vlay = QtWidgets.QVBoxLayout(Widget)
        vlay.setContentsMargins(9, 0, 9, 0)
        vlay.setSpacing(0)
        vlay.setObjectName(_fromUtf8("vlay"))
        # Create layout :
        Layout = QtWidgets.QVBoxLayout()  # noqa
        Layout.setSpacing(0)
        Layout.setObjectName(_fromUtf8(name_layout))
        vlay.addLayout(Layout)

        return Widget, Layout

    def _fcn_chan_check_and_create_w(self):
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
            self._chanChecks[i].setObjectName(_fromUtf8("_CheckChan" + k))
            self._chanChecks[i].setText(k)
            self._chanChecks[i].setShortcut("Ctrl+" + str(i))
            # Add checkbox to the grid :
            self._PanChanLay.addWidget(self._chanChecks[i], i, 0, 1, 1)
            # Connect with the function :
            self._chanChecks[i].clicked.connect(self._fcn_chan_viz)

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
            self._yminSpin[i].valueChanged.connect(self._fcn_chan_amplitude)
            self._ymaxSpin[i].valueChanged.connect(self._fcn_chan_amplitude)

            # ============ WIDGETS / LAYOUTS ============
            # Create a widget :
            (self._chanWidget[i],
             self._chanLayout[i]) = self._create_compatible_w(
                "_widgetChan" + k, "_LayoutChan" + k)
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
                                             name='Canvas_' + k,
                                             fcn=[self.on_mouse_wheel])
            # Add the canvas to the layout :
            self._chanLayout[i].addWidget(self._chanCanvas[i].canvas.native)

        self._PanChanLay.addItem(vspacer, i + 1, 0, 1, 1)
        self._chanGrid.addItem(hspacer, i + 4, 1, 1, 1)

    # =====================================================================
    # AMPLITUDES
    # =====================================================================
    def _fcn_chan_auto_amp(self):
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
            self._fcn_chan_amplitude()
        else:
            self._chan.update()

    def _fcn_chan_sym_amp(self):
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
        self._fcn_chan_amplitude()

    def _fcn_chan_amplitude(self):
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

    def _fcn_all_amp(self):
        """Set all channel amplitudes."""
        for k, (m, M) in enumerate(zip(self._yminSpin, self._ymaxSpin)):
            m.setValue(self._PanAllAmpMin.value())
            M.setValue(self._PanAllAmpMax.value())
        self._fcn_chan_amplitude()

    def _fcn_update_amp_info(self):
        """Update informations about amplitudes."""
        self._get_data_info()
        self._PanAllAmpMin.setMinimum(self['min'].min())
        self._PanAllAmpMin.setMaximum(self['max'].max())
        self._PanAllAmpMax.setMinimum(self['min'].min())
        self._PanAllAmpMax.setMaximum(self['max'].max())

    def _fcn_chan_set_lw(self):
        """Set channels line-width."""
        self._chan.width = self._channels_lw.value()
        self._fcn_slider_move()

    def _fcn_chan_antialias(self):
        """Set anti-aliasing lines."""
        aa = self._channels_alias.isChecked()
        for k in range(len(self._channels)):
            self._chan.mesh[k].antialias = aa
            self._chan.mesh[k].update()
        if aa:
            self._channels_lw.setMinimum(1.5)
        else:
            self._channels_lw.setMinimum(1.)
        self._fcn_chan_set_lw()

    # =====================================================================
    # CHANNEL SELECTION
    # =====================================================================
    def _fcn_chan_viz(self):
        """Control visible panels of channels."""
        for i, k in enumerate(self._chanChecks):
            viz = k.isChecked()
            self._chanWidget[i].setVisible(viz)
            self._chanLabels[i].setVisible(viz)
            self._chan.visible[i] = viz
            if viz:
                self._chanCanvas[i].set_camera(self._chanCam[i])
        self._chan.update()

    def _fcn_select_all_chan(self):
        """Select all channels."""
        for k in self._chanChecks:
            k.setChecked(True)
        self._fcn_chan_viz()

    def _fcn_deselect_all_chan(self):
        """De-select all channels."""
        for k in self._chanChecks:
            k.setChecked(False)
        self._fcn_chan_viz()

    def _canvas_is_visible(self, k):
        """Find if canvas k is visible.

        Parameters
        ----------
        k : int
            Index of the canvas.

        Returns
        -------
        visible : bool
            A boolean value indicating if the canvas is visible.
        """
        return self._chanWidget[k].isVisible()

    def _canvas_set_visible(self, k, value):
        """Set the visibility of the canvas k to value.

        Parameters
        ----------
        k : int
            Index of the canvas.
        value : bool
            Boolean value if the canvas has to be visible.
        """
        self._chanChecks[k].setChecked(value)
        self._chanWidget[k].setVisible(value)
        self._chanLabels[k].setVisible(value)
        self._chanCanvas[k].set_camera(self._chanCam[k])

    # =====================================================================
    # SPECTROGRAM
    # =====================================================================
    def _fcn_spec_set_data(self):
        """Set data to the spectrogram."""
        # Get nfft and overlap :
        nfft, over = self._PanSpecNfft.value(), self._PanSpecStep.value()
        # Get starting / ending frequency :
        fstart, fend = self._PanSpecFstart.value(), self._PanSpecFend.value()
        # Get contrast :
        contrast = self._PanSpecCon.value()
        # Get colormap :
        cmap = str(self._PanSpecCmap.currentText())
        # Get channel to get spectrogram :
        chan = self._PanSpecChan.currentIndex()
        # Use spectrogram / tf :
        method = str(self._PanSpecMethod.currentText())
        # Interpolation :
        interp = str(self._PanSpecInterp.currentText())
        # Normalization :
        norm = int(self._PanSpecNorm.currentIndex())
        # Get reversed colormap :
        if self._PanSpecCmapInv.isChecked():
            cmap += '_r'
        self._specLabel.setText(self._addspace + self._channels[chan])
        # Set data :
        self._spec.set_data(self._sf, self._data[chan, ...], self._time,
                            nfft=nfft, overlap=over, fstart=fstart, fend=fend,
                            cmap=cmap, contrast=contrast, interp=interp,
                            norm=norm, method=method)
        # Set apply button disable :
        self._PanSpecApply.setEnabled(False)

    def _fcn_spec_compat(self):
        """Check compatibility between spectro parameters."""
        # Get nfft and overlap :
        nfft, _ = self._PanSpecNfft.value(), self._PanSpecStep.value()
        # Get starting / ending frequency :
        _, fend = self._PanSpecFstart.value(), self._PanSpecFend.value()  # noqa
        # Enable / disable normalization :
        use_tf = 1 if str(self._PanSpecMethod.currentText()
                          ) == 'Wavelet' else 0
        self._PanSpecNormW.setEnabled(use_tf)

        self._PanSpecStep.setMaximum(nfft * .99)
        self._PanSpecFend.setMaximum(self._sf / 2)
        self._PanSpecFstart.setMaximum(fend - 0.99)
        # Set apply button enable :
        self._PanSpecApply.setEnabled(True)

    def _fcn_spec_interp(self):
        """Change the 2-D interpolation method."""
        # Interpolation :
        self._spec.interp = str(self._PanSpecInterp.currentText())

    # =====================================================================
    # HYPNOGRAM
    # =====================================================================
    def _fcn_set_hypno_lw(self):
        """Change the line width of the hypnogram."""
        self._hyp.width = self._PanHypnoLw.value()
        self._hyp.set_data(self._sf, self._hypno, self._time)

    def _fcn_set_hypno_color(self):
        """Change the color of the hypnogram."""
        if not(self._PanHypnoColor.isChecked()):
            color = {-1: '#292824', 0: '#292824', 1: '#292824',
                     2: '#292824', 3: '#292824', 4: '#292824'}
        else:
            color = self._hypcolor
        # Get color :
        zp = zip(color.keys(), color.values())
        self._hyp.color = {k: color2vb(color=i) for k, i in zp}
        # Update hypnogram
        self._hyp.set_data(self._sf, self._hypno, self._time)

    def _fcn_hypno_clean(self):
        """Clean the hypnogram."""
        # Confirmation dialog
        reply = QtWidgets.QMessageBox.question(self, 'Message',
                                               "Are you sure you want to reset"
                                               " the program?",
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self._hypno = np.zeros((len(self._hyp),), dtype=np.float32)
            self._hyp.clean(self._sf, self._time)
            # Update info table :
            self._fcn_info_update()
            # Update scoring table :
            self._fcn_hypno_to_score()
            self._fcn_score_to_hypno()
        else:
            pass

    # =====================================================================
    # TOPOPLOT
    # =====================================================================
    def _fcn_topo_settings(self):
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

    def _fcn_topo_apply(self):
        """Apply topo settings."""
        self._fcn_slider_move()
        self._PanTopoApply.setEnabled(False)
