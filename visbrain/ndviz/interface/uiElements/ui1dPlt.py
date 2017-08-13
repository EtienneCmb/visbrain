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
        self._1dargs = {}
        self._shapetxt1d = 'data.shape = {sh}'
        self._1dForceUpdate = False
        self._1dAxCheckTxt.setVisible(False)
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
        pltype = self._1dplt.mesh._name
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
        self._1dPltfStart.setValue(self._1dplt.mesh._fstart)
        self._1dPltfStart.valueChanged.connect(self._fcn_1dPlt)
        self._1dPltfEnd.setValue(self._1dplt.mesh._fend)
        self._1dPltfEnd.valueChanged.connect(self._fcn_1dPlt)
        self._1dLineMeth.setCurrentIndex(meth.index(self._1dplt.mesh._method))
        self._1dLineMeth.currentIndexChanged.connect(self._fcn_1dPlt)
        self._1dMarkSize.setValue(self._1dplt.mesh._msize)
        self._1dMarkSize.valueChanged.connect(self._fcn_1dPlt)
        # Line width :
        self._1dLineWidth.setValue(self._1dlw)
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
        self._1dGridTog.clicked.connect(self._fcn_1dGridToggle)
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
        ndim = self._1dplt.mesh.ndim
        sh = self._1dplt.mesh.sh

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
            # Define available axis :
            avai = [str(k) for k in np.arange(ndim)]
            self._1dAxX.addItems(avai)
            self._1dAxY.addItems(avai)
            # Set the already defined axis :
            self._1dAxX.setCurrentIndex(self._1dplt.mesh._axis[0])
            self._1dAxY.setCurrentIndex(self._1dplt.mesh._axis[1])

    def _fcn_1dAxis_update(self):
        """Check axis compatibility."""
        # Get the number of dimensions :
        ndim = self._1dplt.mesh.ndim
        sh = self._1dplt.mesh.sh

        # Define index range :
        if ndim > 1:
            along = self._1dAxY.currentIndex()
            self._1dAxInd.setMinimum(0)
            self._1dAxInd.setMaximum(sh[along]-1)

        # Display update buton if both axis are different :
        if self._1dAxX.currentIndex() is self._1dAxY.currentIndex():
            self._1dAxInd.setEnabled(False)
            self._1dAxCheckTxt.setVisible(True)
        else:
            self._1dAxCheckTxt.setVisible(False)
            self._1dAxInd.setEnabled(True)

            # Set selected axis and index :
            if ndim == 1:
                self._1dAxInd.setEnabled(False)
                self._1dargs['axis'] = None
                self._1dargs['index'] = 0
            else:
                # Set possible axis and index limits :
                self._1dAxInd.setMinimum(0)
                self._1dAxInd.setMaximum(self._1dplt.mesh.l-1)
                ax = (self._1dAxX.currentIndex(), self._1dAxY.currentIndex())
                self._1dargs['axis'] = ax
                self._1dargs['index'] = self._1dAxInd.value()

            # Update plot and canvas :
            self._fcn_1dUpdate()

    # =====================================================================
    # PLOT
    # =====================================================================
    def _fcn_1dPlt(self):
        """Manage plot type inputs."""
        # Get plot type :
        plt = str(self._1dPltPick.currentText())
        self._1dargs['plot'] = plt
        objlst = [self._1dPltLine, self._1dPltHist, self._1dPltSpec,
                  self._1dPltMark]
        enab = [self._1dColBox, self._1dAxInd, self._1dColType.model().item(2),
                self._1dColType.model().item(3)]

        # ----------------------------------------------------
        # LINE :
        if plt == 'line':
            # Get line method :
            self._1dargs['method'] = str(self._1dLineMeth.currentText())
            # Set only line control visible :
            viz = [True, False, False, False]
            enabviz = [True, True, True, True]

        # ----------------------------------------------------
        # HISTOGRAM :
        elif plt == 'histogram':
            # Get bin number :
            self._1dargs['bins'] = self._1dPltBins.value()
            # Set only histogram control visible :
            viz = [False, True, False, False]
            enabviz = [True, True, False, False]
            # Disable dynamic coloring :
            self._1dDynText.setVisible(False)

        # ----------------------------------------------------
        # SPECTROGRAM :
        elif plt == 'spectrogram':
            # Get nfft, step and color scale :
            self._1dargs['nfft'] = self._1dPltNfft.value()
            self._1dargs['step'] = self._1dPltStep.value()
            self._1dargs['fstart'] = self._1dPltfStart.value()
            self._1dargs['fend'] = self._1dPltfEnd.value()
            # Set only spectrogram control visible :
            viz = [False, False, True, False]
            enabviz = [False, True, False, False]
            # Set color disable :
            self._1dDynText.setVisible(False)

        # ----------------------------------------------------
        # MARKER :
        elif plt == 'marker':
            # Get marker size :
            self._1dargs['msize'] = self._1dMarkSize.value()
            # Set only spectrogram control visible :
            viz = [False, False, False, True]
            enabviz = [True, True, True, True]

        # ----------------------------------------------------

        # Get interpolation type and step :
        self._1dargs['itp_type'] = str(self._1dInterType.currentText())
        self._1dargs['itp_step'] = self._1dInterStep.value()

        # Set visible panels :
        [k.setVisible(i) for k, i in zip(objlst, viz)]
        [k.setEnabled(i) for k, i in zip(enab, enabviz)]

        # Update plot :
        self._fcn_1dUpdate()

    # =====================================================================
    # COLOR
    # =====================================================================
    def _fcn_1dcolor(self):
        """Manage color of nd-signals."""
        # Get color type :
        col = str(self._1dColType.currentText())
        self._1dargs['color'] = col

        # Manage panel to display :
        if col in ['dyn_time', 'dyn_minmax']:
            self._1dRndPan.setVisible(False)
            self._1dUniPan.setVisible(False)
            self._1dDynText.setVisible(True)
            [self._cbObjects.model().item(k).setEnabled(True) for k in [1, 2]]
        elif col == 'random':
            self._1dRndPan.setVisible(True)
            self._1dUniPan.setVisible(False)
            self._1dDynText.setVisible(False)
            [self._cbObjects.model().item(k).setEnabled(False) for k in [1, 2]]
        elif col == 'uniform':
            self._1dRndPan.setVisible(False)
            self._1dUniPan.setVisible(True)
            uni = textline2color(str(self._1dUniColor.text()))[0]
            self._1dDynText.setVisible(False)
            self._1dargs['unicolor'] = uni
            [self._cbObjects.model().item(k).setEnabled(False) for k in [1, 2]]

        # Get random color dynamic :
        self._1dargs['rnd_dyn'] = (self._1dRndDynMin.value(),
                                   self._1dRndDynMax.value())

        # Update color :
        self._fcn_1dUpdate()

    # =====================================================================
    # 1d-SETTINGS
    # =====================================================================
    def _fcn_1dUpdate(self):
        """Update 1d-plot."""
        if self._1dForceUpdate:
            # Set type and args :
            self._1dargs.update(self._cb.cb_kwargs(self._1dargs['plot']))
            self._1dplt.mesh.set_data(self._oridata, self._sf, **self._1dargs)
            # Update canvas and camera :
            self._1dCanvas.canvas.update()
            self._1dCanvas.wc.camera.rect = self._1dplt.mesh.rect
            self._1dCanvas.wc.camera.update()

    def _fcn_get_1dMinmax(self):
        """Get the minmax variable."""
        return self._1dplt.mesh.minmax

    def _fcn_1dLineWidth(self):
        """Increase / decrease plot linewidth."""
        # Get line width (LW) from the button :
        self._1dlw = self._1dLineWidth.value()
        # The method to control linewidth depend of the line method :
        if str(self._1dLineMeth.currentText()) == 'gl':
            # Set the LW to the canvas :
            self._1dCanvas.canvas.context.set_line_width(self._1dlw)
        else:
            self._1dplt.mesh._line._width = self._1dlw
            self._1dplt.mesh._line.update()
        self._1dCanvas.canvas.update()

    def _fcn_1dEdit(self):
        """Update title / labels of the Nd-plot."""
        self._1dCanvas.set_info(title=str(self._1dTitleEdit.text()),
                                xlabel=str(self._1dXlabEdit.text()),
                                ylabel=str(self._1dYlabEdit.text()))

    def _fcn_1dGridToggle(self):
        """Display or hide axis."""
        viz = not self._1dGridTog.isChecked()
        self._1dGridTog.setChecked(viz)
        self._1dCanvas.visible_axis(viz)
        self._1dCanvas.canvas.update()

    def _1dToggleViz(self):
        """Toggle panle."""
        viz = not self._1dVizPanel.isVisible()
        self._CanVis1d.setChecked(viz)
        self._fcn_CanVisToggle()
