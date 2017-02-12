"""Main class for Nd-plot managment."""

import numpy as np

from ....utils import textline2color


__all__ = ['ui1dPlt']


class ui1dPlt(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # ---------------------------------------------------------------------
        # AXIS
        # ---------------------------------------------------------------------
        self._shapetxt1d = 'data.shape = {sh}'
        self._1dAxUpdate.setVisible(False)
        self._1dForceUpdate = False
        # First run of axis checking and compatibility :
        self._fcn_1dAxis_checking()
        self._fcn_1dAxis_update()
        # Link axis objects with functions :
        self._1dAxX.currentIndexChanged.connect(self._fcn_1dAxis_update)
        self._1dAxY.currentIndexChanged.connect(self._fcn_1dAxis_update)
        self._1dAxInd.valueChanged.connect(self._fcn_1dAxis_update)

        # ---------------------------------------------------------------------
        # PLOT
        # ---------------------------------------------------------------------
        pltype = ['line', 'histogram', 'spectrogram']
        meth = ['gl', 'agg']
        # Plot type :
        self._1dPltPick.setCurrentIndex(pltype.index(self._1dplt.mesh._plot))
        self._1dPltPick.currentIndexChanged.connect(self._fcn_1dPlt)
        # Plot args :
        self._1dPltBins.setValue(self._1dplt.mesh._bins)
        self._1dPltBins.valueChanged.connect(self._fcn_1dPlt)
        self._1dPltNfft.setValue(self._1dplt.mesh._nfft)
        self._1dPltNfft.valueChanged.connect(self._fcn_1dPlt)
        self._1dPltStep.setValue(self._1dplt.mesh._step)
        self._1dPltStep.valueChanged.connect(self._fcn_1dPlt)
        self._1dLineMeth.setCurrentIndex(meth.index(self._1dplt.mesh._method))
        self._1dLineMeth.currentIndexChanged.connect(self._fcn_1dPlt)
        # Line width :
        self._1dLineWidth.setValue(self._lw)
        self._1dLineWidth.valueChanged.connect(self._fcn_1dLineWidth)
        # Interpolation :
        self._1dInterType.currentIndexChanged.connect(self._fcn_1dPlt)
        self._1dInterStep.valueChanged.connect(self._fcn_1dPlt)

        self._fcn_1dLineWidth()
        self._fcn_1dPlt()

        # ---------------------------------------------------------------------
        # COLOR
        # ---------------------------------------------------------------------
        # Color type :
        coltype = ['random', 'uniform', 'dyn_time', 'dyn_minmax']
        self._1dColType.setCurrentIndex(coltype.index(self._1dplt.mesh._color))
        self._1dColType.currentIndexChanged.connect(self._fcn_1dcolor)
        # Get random min / max :
        self._1dplt.mesh._rnd_dyn = (self._1dRndDynMin.value(),
                                     self._1dRndDynMax.value())
        self._1dRndDynMin.valueChanged.connect(self._fcn_1dcolor)
        self._1dRndDynMax.valueChanged.connect(self._fcn_1dcolor)
        # New random color :
        self._1dRndNew.clicked.connect(self._fcn_1dcolor)
        # Uniform color :
        self._1dUniColor.setText(self._ndplt.mesh._unicolor)
        self._1dUniColor.editingFinished.connect(self._fcn_1dcolor)
        self._1dUniColor.setPlaceholderText("red,  green, #ab4642...")
        self._fcn_1dcolor()

        # ---------------------------------------------------------------------
        # INFO
        # ---------------------------------------------------------------------
        self._1dTitleEdit.editingFinished.connect(self._fcn_1dEdit)
        self._1dXlabEdit.editingFinished.connect(self._fcn_1dEdit)
        self._1dYlabEdit.editingFinished.connect(self._fcn_1dEdit)

        self._1dForceUpdate = True

    # =====================================================================
    # AXIS
    # =====================================================================
    def _fcn_1dAxis_checking(self):
        """Check axis of 1d plot."""
        # Get the number of dimensions :
        ndim = self._1dplt.mesh._data.ndim
        sh = self._1dplt.mesh._data.shape

        # Set shape text :
        self._1dAxShape.setText(self._shapetxt1d.format(sh=str(sh)))

        # Object's control according to data shape :
        if ndim == 1:
            # Disable everything for a row vector :
            self._1dAxX.setEnabled(False)
            self._1dAxY.setEnabled(False)
            self._1dAxInd.setEnabled(False)
        else:
            # Set possible axis and index limits :
            self._1dAxInd.setMinimum(0)
            self._1dAxInd.setMaximum(self._1dplt.mesh.l-1)
            # Define avaible axis :
            avai = [str(k) for k in np.arange(ndim)]
            self._1dAxX.addItems(avai)
            self._1dAxY.addItems(avai)
            # Set the already defined axis :
            self._1dAxX.setCurrentIndex(self._1dplt.mesh._axis[0])
            self._1dAxY.setCurrentIndex(self._1dplt.mesh._axis[1])

    def _fcn_1dAxis_update(self):
        """Check axis compatibility."""
        # Get the number of dimensions :
        ndim = self._1dplt.mesh._data.ndim
        sh = self._1dplt.mesh._data.shape

        # Define index range :
        if ndim > 1:
            along = self._1dAxY.currentIndex()
            self._1dAxInd.setMinimum(0)
            self._1dAxInd.setMaximum(sh[along]-1)

        # Display update buton if both axis are different :
        if self._1dAxX.currentIndex() is self._1dAxY.currentIndex():
            # self._1dAxUpdate.setVisible(False)
            self._1dAxInd.setEnabled(False)
        else:
            # self._1dAxUpdate.setVisible(True)
            self._1dAxInd.setEnabled(True)

            # Set selected axis and index :
            if ndim is 1:
                self._1dplt.mesh._axis = None
                self._1dplt.mesh._index = 0
            else:
                ax = (self._1dAxX.currentIndex(), self._1dAxY.currentIndex())
                self._1dplt.mesh._axis = ax
                self._1dplt.mesh._index = self._1dAxInd.value()

            # Update plot and canvas :
            if self._1dForceUpdate:
                self._1dplt.mesh.update()
                self._1dCanvas.wc.camera.rect = self._1dplt.mesh.rect
                self._1dCanvas.canvas.update()

    # =====================================================================
    # PLOT
    # =====================================================================
    def _fcn_1dPlt(self):
        """Manage plot type inputs."""
        # Get plot type :
        plt = self._1dPltPick.currentText()

        # Line plot :
        if plt == 'line':
            # Get line method :
            meth = self._1dLineMeth.currentText()
            # Set only line control visible :
            self._1dPltLine.setVisible(True)
            self._1dPltHist.setVisible(False)
            self._1dPltSpec.setVisible(False)
            # Enable coloring :
            self._1dColBox.setEnabled(True)
            self._1dColType.model().item(2).setEnabled(True)
            self._1dColType.model().item(3).setEnabled(True)
            # Set data line type :
            tp, kwargs = 'line', {'method': meth}

        # Histogram :
        elif plt == 'histogram':
            # Get bin number :
            bins = self._1dPltBins.value()
            # Set only histogram control visible :
            self._1dPltLine.setVisible(False)
            self._1dPltHist.setVisible(True)
            self._1dPltSpec.setVisible(False)
            # Disable dynamic coloring :
            self._1dColBox.setEnabled(True)
            self._1dColType.model().item(2).setEnabled(False)
            self._1dColType.model().item(3).setEnabled(False)
            self._1dDynText.setVisible(False)
            # Set data histogram type :
            tp, kwargs = 'histogram', {'bins': bins}

        # Spectrogram :
        elif plt == 'spectrogram':
            # Get nfft, step and color scale :
            nfft = self._1dPltNfft.value()
            step = self._1dPltStep.value()
            # Set only spectrogram control visible :
            self._1dPltLine.setVisible(False)
            self._1dPltHist.setVisible(False)
            self._1dPltSpec.setVisible(True)
            # Set color disable :
            self._1dColBox.setEnabled(False)
            self._1dDynText.setVisible(False)
            # Set data spectrogram type :
            tp, kwargs = 'spectrogram', {'nfft': nfft, 'step': step}


        # Get interpolation type and step :
        self._1dplt.mesh._itptype = self._1dInterType.currentText()
        self._1dplt.mesh._itpstep = self._1dInterStep.value()

        if self._1dForceUpdate:
            # Set type and args :
            self._1dplt.mesh.set_type(tp, **kwargs)
            # Update canvas and camera :
            self._1dCanvas.canvas.update()
            self._1dCanvas.wc.camera.rect = self._1dplt.mesh.rect
            self._1dCanvas.wc.camera.update()

    # =====================================================================
    # COLOR
    # =====================================================================
    def _fcn_1dcolor(self):
        """Manage color of nd-signals."""
        # Get color type :
        col = self._1dColType.currentText()
        uni = 'gray'

        # Manage panel to display :
        if col in ['dyn_time', 'dyn_minmax']:
            self._1dRndPan.setVisible(False)
            self._1dUniPan.setVisible(False)
            self.q_Cmap.setEnabled(True)
            self._1dDynText.setVisible(True)
        elif col == 'random':
            self._1dRndPan.setVisible(True)
            self._1dUniPan.setVisible(False)
            self.q_Cmap.setEnabled(False)
            self._1dDynText.setVisible(False)
        elif col == 'uniform':
            self._1dRndPan.setVisible(False)
            self._1dUniPan.setVisible(True)
            uni = textline2color(self._1dUniColor.text())[0]
            self.q_Cmap.setEnabled(False)
            self._1dDynText.setVisible(False)

        # Get random color dynamic :
        rnd_dyn = (self._1dRndDynMin.value(), self._1dRndDynMax.value())

        # Update color :
        if self._1dForceUpdate:
            self._1dplt.mesh.set_color(color=col, rnd_dyn=rnd_dyn,
                                       unicolor=uni)
        # self._1dplt.mesh._obj.update()

    # =====================================================================
    # 1d-SETTINGS
    # =====================================================================
    def _fcn_1dLineWidth(self):
        """Increase / decrease plot linewidth."""
        # Get line width (LW) from the button :
        self._lw = self._1dLineWidth.value()
        # The method to control linewidth depend of the line method :
        if self._1dLineMeth.currentText() is 'gl':
            # Set the LW to the canvas :
            self._1dCanvas.canvas.context.set_line_width(self._lw)
        else:
            self._1dplt.mesh._line._width = self._lw
            self._1dplt.mesh._line.update()
        self._1dCanvas.canvas.update()

    def _fcn_1dEdit(self):
        """Update title / labels of the Nd-plot."""
        self._1dCanvas.set_info(title=self._1dTitleEdit.text(),
                                xlabel=self._1dXlabEdit.text(),
                                ylabel=self._1dYlabEdit.text())
