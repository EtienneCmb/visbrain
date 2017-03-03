"""Main class for settings managment."""

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

        # =====================================================================
        # SPECTROGRAM
        # =====================================================================
        self._PanHypViz.clicked.connect(self._fcn_hypViz)

    # =====================================================================
    # CHANNELS
    # =====================================================================
    def _fcn_chanCheckAndWCreate(self):
        """Create one checkbox and one widget/layout per channel."""
        # Empty list of checkbox and widgets/layouts :
        self._chanChecks = [0] * len(self._channels)
        self._chanWidget = self._chanChecks.copy()
        self._chanLayout = self._chanChecks.copy()
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
            self._chanWidget[i] = QtGui.QWidget(self._chanScrollArea)
            self._chanWidget[i].setMinimumSize(QtCore.QSize(0, 0))
            self._chanWidget[i].setObjectName(_fromUtf8("_widgetChan"+k))
            vlay = QtGui.QVBoxLayout(self._chanWidget[i])
            vlay.setContentsMargins(9, 0, 9, 0)
            vlay.setSpacing(0)
            vlay.setObjectName(_fromUtf8("vlay"))
            # Create layout :
            self._chanLayout[i] = QtGui.QVBoxLayout()
            self._chanLayout[i].setSpacing(0)
            self._chanLayout[i].setObjectName(_fromUtf8("_LayoutChan"+k))
            vlay.addLayout(self._chanLayout[i])
            label = QtGui.QLabel(self._chanWidget[i])
            label.setText(k)
            self._chanLayout[i].addWidget(label)
            # Add widget to the grid :
            self._chanGrid.addWidget(self._chanWidget[i], i, 0, 1, 1)

        # Set first element checked and first panel visible :
        self._chanChecks[0].setChecked(True)
        # Add vertical spacer :
        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Minimum)
        self._PanChanLay.addItem(spacer, i+1, 0, 1, 1)

    def _fcn_chanViz(self):
        """Control visible panels of channels."""
        for i, k in enumerate(self._chanChecks):
            self._chanWidget[i].setVisible(k.isChecked())

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
