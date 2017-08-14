"""Main class for Image managment."""

import numpy as np

__all__ = ['uiImage']


class uiImage(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # ---------------------------------------------------------------------
        # AXIS
        # ---------------------------------------------------------------------
        self._imargs = {'plot': 'image'}
        self._shapetxtim = 'data.shape = {sh}'
        self._imForceUpdate = False
        self._imAxCheckTxt.setVisible(False)
        # First run of axis checking and compatibility :
        self._fcn_imAxis_checking()
        self._fcn_imAxis_update()
        # Link axis objects with functions :
        self._imAxX.currentIndexChanged.connect(self._fcn_imAxis_update)
        self._imAxY.currentIndexChanged.connect(self._fcn_imAxis_update)
        self._imAxZ.currentIndexChanged.connect(self._fcn_imAxis_update)
        self._imAxInd.valueChanged.connect(self._fcn_imAxis_update)

    def _fcn_imAxis_checking(self):
        """Check axis."""
        # Get the number of dimensions :
        ndim = self._1dplt.mesh.ndim
        sh = self._1dplt.mesh.sh

        # Set shape text :
        self._imAxShape.setText(self._shapetxtim.format(sh=str(sh)))

        # Activate / deactivate some controls :
        if ndim == 1:
            self._2dSigTab.setEnabled(False)
            self._imForceUpdate = False
        else:
            self._imForceUpdate = True
            if ndim == 2:
                # Diable Z-axis :
                self._imAxZ.setEnabled(False)
                self._imAxInd.setEnabled(False)
            else:
                # Set possible axis and index limits :
                self._imAxInd.setMinimum(0)
                self._imAxInd.setMaximum(sh[self._imAxZ.currentIndex()]-1)
            # Define available axis :
            avai = [str(k) for k in np.arange(ndim)]
            self._imAxX.addItems(avai)
            self._imAxY.addItems(avai)
            self._imAxZ.addItems(avai)
            # Set the already defined axis :
            self._imAxX.setCurrentIndex(self._1dplt.mesh._axis[0])
            self._imAxY.setCurrentIndex(self._1dplt.mesh._axis[1])
            self._imAxZ.setCurrentIndex(self._1dplt.mesh._imz)

    def _fcn_imAxis_update(self):
        """Update axis selection."""
        # Get the number of dimensions :
        ndim, sh = self._1dplt.mesh.ndim, self._oridata.shape

        # Get axis and index :
        ax = [self._imAxX.currentIndex(), self._imAxY.currentIndex(),
              self._imAxZ.currentIndex()]
        ind = self._imAxInd.value()

        if len(np.unique(ax[:ndim])) == np.min([3, ndim]):
            # Hide check message :
            self._imAxCheckTxt.setVisible(False)
            # Activate / deactivate some controls :
            if ndim == 2:
                self._imargs['axis'] = ax[:2]
                self._imargs['imz'] = None
                self._imargs['index'] = None
            else:
                self._imargs['axis'] = ax[:2]
                self._imargs['imz'] = ax[2]
                self._imargs['index'] = ind
                # Set possible axis and index limits :
                self._imAxInd.setMinimum(0)
                self._imAxInd.setMaximum(sh[self._imAxZ.currentIndex()]-1)

            # Update config :
            self._fcn_imUpdate()
        else:
            self._imAxCheckTxt.setVisible(True)

    def _fcn_imUpdate(self):
        """Update 1d-plot."""
        if self._imForceUpdate:
            # Set type and args :
            self._imargs.update(self._cb.cb_kwargs('image'))
            self._1dplt.mesh.set_data(self._oridata, self._sf, **self._imargs)
            # Update canvas and camera :
            self._1dCanvas.canvas.update()
            self._1dCanvas.wc.camera.rect = self._1dplt.mesh.rect
            self._1dCanvas.wc.camera.update()
