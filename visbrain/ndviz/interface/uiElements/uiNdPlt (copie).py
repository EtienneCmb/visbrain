"""Main class for Nd-plot managment."""

import numpy as np

from ....utils import textline2color


__all__ = ['uiNdPlt']


class uiNdPlt(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # ---------------------------------------------------------------------
        # AXIS :
        # ---------------------------------------------------------------------
        self._shapetxtNd = 'data.shape = {sh}'
        self._ndAxUpdate.setEnabled(False)
        self._ndForceUpdate = False
        # First run of axis checking and compatibility :
        self._fcn_ndAxis_checking()
        self._fcn_NdAxis_compat()
        # Link axis objects with functions :
        self._ndAxTime.currentIndexChanged.connect(self._fcn_NdAxis_compat)
        self._ndAxNdRows.currentIndexChanged.connect(self._fcn_NdAxis_compat)
        self._ndAxNdCols.currentIndexChanged.connect(self._fcn_NdAxis_compat)
        self._ndAx2dRows.valueChanged.connect(self._fcn_NdAxis_compat)
        self._ndAx2dCols.valueChanged.connect(self._fcn_NdAxis_compat)
        self._ndAxUpdate.clicked.connect(self._fcn_ndAxis_update)

        # ---------------------------------------------------------------------
        # COLOR :
        # ---------------------------------------------------------------------
        # Color type :
        coltype = ['random', 'uniform', 'dyn_time', 'dyn_minmax']
        self._ndColType.setCurrentIndex(coltype.index(self._ndplt.mesh._color))
        self._ndColType.currentIndexChanged.connect(self._fcn_ndcolor)
        # Get random min / max :
        self._ndplt.mesh._rnd_dyn = (self._ndRndDynMin.value(),
                                     self._ndRndDynMax.value())
        self._ndRndDynMin.valueChanged.connect(self._fcn_ndcolor)
        self._ndRndDynMax.valueChanged.connect(self._fcn_ndcolor)
        # New random color :
        self._ndRndNew.clicked.connect(self._fcn_ndcolor)
        # Uniform color :
        self._ndUniColor.setText(self._ndplt.mesh._unicolor)
        self._ndUniColor.editingFinished.connect(self._fcn_ndcolor)
        self._ndUniColor.setPlaceholderText("red,  green, #ab4642...")

        self._fcn_ndcolor()

        # ---------------------------------------------------------------------
        # REAL TIME :
        # ---------------------------------------------------------------------
        # Set the number of laps :
        self._ndRtLaps.setValue(self._ndplt.mesh._laps)
        # Play / Pause / Reset control :
        self._ndRtStart.clicked.connect(self._fcn_rtplay)
        self._ndRtLaps.valueChanged.connect(self._fcn_rtplay)
        self._ndRtStop.clicked.connect(self._fcn_rtstop)
        self._ndRtReset.clicked.connect(self._fcn_rtreset)
        self._isPlaying = False

        # ---------------------------------------------------------------------
        # Nd-SETTINGS :
        # ---------------------------------------------------------------------
        # Space between plots :
        self._ndSetSpace.valueChanged.connect(self._fcn_set_space)
        self._ndSetSpace.setValue(self._ndplt.mesh._space)
        # Line width :
        self._ndLineWidth.setValue(self._lw)
        self._ndLineWidth.valueChanged.connect(self._fcn_ndLineWidth)
        self._fcn_ndLineWidth()
        # Signal scaling :
        self._ndScaleX.setValue(self._ndplt.mesh._uscale[0])
        self._ndScaleY.setValue(self._ndplt.mesh._uscale[1])
        self._ndScaleX.valueChanged.connect(self._fcn_scale_sig)
        self._ndScaleY.valueChanged.connect(self._fcn_scale_sig)

        # ---------------------------------------------------------------------
        # INFO
        # ---------------------------------------------------------------------
        self._ndGridTog.setChecked(self._ndCanvas._axis)
        self._ndGridTog.clicked.connect(self._fcn_ndGridToggle)
        self._ndTitleEdit.editingFinished.connect(self._fcn_ndEdit)
        self._ndXlabEdit.editingFinished.connect(self._fcn_ndEdit)
        self._ndYlabEdit.editingFinished.connect(self._fcn_ndEdit)

        self._ndForceUpdate = True

    # =====================================================================
    # AXIS
    # =====================================================================
    def _fcn_ndAxis_checking(self):
        """Display / hide axis panels according to data dimension."""
        # ---------------------------------------------------------------------
        # GET DATA INFO
        # ---------------------------------------------------------------------
        # Get the actual data ndim and shape :
        ndim, sh = self._oridata.ndim, self._oridata.shape
        # Build a list of possible axis (string for combo box) :
        self._avaiAxis = [str(k) for k in range(ndim)]
        # Set time axis :
        self._ndAxTime.addItems(self._avaiAxis)
        self._ndAxTime.setCurrentIndex(self._ndplt.mesh._axis[0])

        # Set shape text :
        self._ndAxShape.setText(self._shapetxtNd.format(sh=str(sh)))

        # Get rows / cols :
        rows, cols = self._ndplt.mesh.nrows, self._ndplt.mesh.ncols

        # ---------------------------------------------------------------------
        # SHAPE MANAGEMENT
        # ---------------------------------------------------------------------
        # Row vector :
        if ndim == 1:
            # Disable every control :
            self._ndAxTime.setEnabled(False)
            self._ndAx2DPan.setVisible(False)
            self._ndAxCheckMsg.setVisible(False)
            self._ndAx2dSecText.setVisible(False)
            self._ndAx2d.setVisible(False)
            self._ndAxNdPan.setVisible(False)

        # 2D array :
        elif ndim == 2:
            # Enable 2d control :
            self._ndAx2DPan.setVisible(True)
            self._ndAxCheckMsg.setVisible(True)
            self._ndAx2dSecText.setVisible(True)
            self._ndAx2d.setVisible(True)
            self._ndAx2d.setEnabled(False)
            self._ndAxNdPan.setVisible(False)
            # Set second axis values :
            self._ndAx2d.addItems(self._avaiAxis)
            # Set the grid (N_rows x N_cols) :
            self._ndAx2dRows.setValue(rows)
            self._ndAx2dCols.setValue(cols)

        # Nd-array :
        elif ndim >= 3:
            # Enable Nd control :
            self._ndAx2DPan.setVisible(False)
            self._ndAxCheckMsg.setVisible(False)
            self._ndAx2dSecText.setVisible(False)
            self._ndAx2d.setVisible(False)
            self._ndAxNdPan.setVisible(True)
            # Set combo box :
            self._ndAxNdRows.addItems(self._avaiAxis)
            self._ndAxNdCols.addItems(self._avaiAxis)
            self._ndAxNdRows.setCurrentIndex(self._ndplt.mesh._axis[1])
            self._ndAxNdCols.setCurrentIndex(self._ndplt.mesh._axis[2])

    def _fcn_NdAxis_compat(self):
        """Manage axis'prameters compatibility according to data dimension."""
        # ---------------------------------------------------------------------
        # GET DATA INFO
        # ---------------------------------------------------------------------
        # Get the actual data ndim and shape :
        ndim = self._oridata.ndim

        # ---------------------------------------------------------------------
        # AXIS COMPATIBILITY
        # ---------------------------------------------------------------------
        # 2D array :
        if ndim == 2:
            # Swap time / 2nd axis :
            idx = [0, 1]
            idx.pop(self._ndAxTime.currentIndex())
            self._ndAx2d.setCurrentIndex(idx[0])
            # Get shape along 2nd axis :
            L = self._oridata.shape[idx[0]]
            # Now check that the grid fit with this length :
            grid = [self._ndAx2dRows.value(), self._ndAx2dCols.value()]
            if L != grid[0]*grid[1]:
                self._ndAxUpdate.setEnabled(False)
                self._ndAxCheckMsg.setVisible(True)
                self._ndAxCheckMsg.setText("The grid must be n_rows*"
                                           "n_cols="+str(L))
            else:
                self._ndAxUpdate.setEnabled(True)
                self._ndAxCheckMsg.setVisible(False)

        # Nd-array :
        elif ndim >= 3:
            # Swap time / 1rst / 2nd axis :
            index = [self._ndAxTime.currentIndex(),
                     self._ndAxNdRows.currentIndex(),
                     self._ndAxNdCols.currentIndex()]
            if len(np.unique(index)) is not 3:
                self._ndAxUpdate.setEnabled(False)
                self._ndAxCheckMsg.setVisible(True)
                self._ndAxCheckMsg.setText("The three dimensions axis must be"
                                           " differents.")
            else:
                self._ndAxCheckMsg.setVisible(False)
                self._ndAxUpdate.setEnabled(True)

    def _fcn_ndAxis_update(self):
        """Update data according to new settings."""
        # ---------------------------------------------------------------------
        # GET DATA INFO
        # ---------------------------------------------------------------------
        # Get the actual data ndim and shape :
        ndim = self._oridata.ndim

        # ---------------------------------------------------------------------
        # UPDATE DATA
        # ---------------------------------------------------------------------
        # 2D array :
        if ndim == 2:
            # Get new axis location :
            ax = list(np.abs(np.array([0, 1]) - self._ndAxTime.currentIndex()))
            # Get column number :
            force_col = self._ndAx2dCols.value()

        # Nd-array :
        elif ndim >= 3:
            # Get new axis location :
            ax = [self._ndAxTime.currentIndex(),
                  self._ndAxNdRows.currentIndex(),
                  self._ndAxNdCols.currentIndex()]
            force_col = None
            self._ndplt.mesh.set_data(self._oridata, axis=ax)

        # Update plot with new data:
        self._ndplt.mesh.clean()
        self._ndplt.mesh.set_data(self._oridata, axis=ax, force_col=force_col)
        self._ndplt.mesh.update()

    # =====================================================================
    # COLOR
    # =====================================================================
    def _fcn_ndcolor(self):
        """Manage color of nd-signals."""
        # Get color type :
        col = self._ndColType.currentText()
        uni = 'gray'

        # Manage panel to display :
        if col in ['dyn_time', 'dyn_minmax']:
            self._ndRndPan.setVisible(False)
            self._ndUniPan.setVisible(False)
            self.q_Cmap.setEnabled(True)
            self._ndDynText.setVisible(True)
        elif col == 'random':
            self._ndRndPan.setVisible(True)
            self._ndUniPan.setVisible(False)
            self.q_Cmap.setEnabled(False)
            self._ndDynText.setVisible(False)
        elif col == 'uniform':
            self._ndRndPan.setVisible(False)
            self._ndUniPan.setVisible(True)
            uni = textline2color(self._ndUniColor.text())[0]
            self.q_Cmap.setEnabled(False)
            self._ndDynText.setVisible(False)

        # Get random color dynamic :
        rnd_dyn = (self._ndRndDynMin.value(), self._ndRndDynMax.value())

        # Update color :
        if self._ndForceUpdate:
            self._ndplt.mesh.set_color(color=col, rnd_dyn=rnd_dyn,
                                       unicolor=uni)
            self._ndplt.mesh.update()

    # =====================================================================
    # REAL TIME
    # =====================================================================
    def _fcn_rtplay(self):
        """Play data in real time."""
        self._ndplt.mesh.play(start=True, laps=self._ndRtLaps.value())
        self._isPlaying = True

    def _fcn_rtstop(self):
        """Stop playing data."""
        self._ndplt.mesh.play(start=False)
        self._isPlaying = False

    def _fcn_rtreset(self):
        """Reset signals in time."""
        self._ndplt.mesh.time_reset()

    def _fcn_TogglePlay(self):
        """Toggle play."""
        self._isPlaying = not self._isPlaying
        self._ndplt.mesh.play(start=self._isPlaying,
                              laps=self._ndRtLaps.value())

    # =====================================================================
    # Nd-SETTINGS
    # =====================================================================
    def _fcn_set_space(self):
        """Increase / Decrease space between plots."""
        self._ndplt.mesh.set_space(self._ndSetSpace.value())
        self._ndplt.mesh.update()

    def _fcn_ndLineWidth(self):
        """Increase / decrease plot linewidth."""
        # Get line width (LW) from the button :
        self._lw = self._ndLineWidth.value()
        # Set the LW to the canvas :
        self._ndCanvas.canvas.context.set_line_width(self._lw)
        self._ndCanvas.canvas.update()

    def _fcn_scale_sig(self):
        """Scale each signal along (x, y) axis."""
        self._ndplt.mesh._uscale = (self._ndScaleX.value(),
                                    self._ndScaleY.value())
        self._ndplt.mesh._check_others()
        self._ndplt.mesh.update()

    def _fcn_ndEdit(self):
        """Update title / labels of the Nd-plot."""
        self._ndCanvas.set_info(title=self._ndTitleEdit.text(),
                                xlabel=self._ndXlabEdit.text(),
                                ylabel=self._ndYlabEdit.text())

    def _fcn_ndGridToggle(self):
        """Display or hide axis."""
        self._ndCanvas.visible_axis(self._ndGridTog.isChecked())

    def _ndToggleViz(self):
        """Toggle panle."""
        viz = not self._NdVizPanel.isVisible()
        self._CanVisNd.setChecked(viz)
        self._fcn_CanVisToggle()
