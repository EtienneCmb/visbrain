"""Main class for settings managment."""
import numpy as np
from PyQt5 import QtWidgets

from visbrain.utils import transient


class UiScoring(object):
    """Enable scoring using the table."""

    def __init__(self):
        """Init."""
        # Add / remove line :
        self._scoreAdd.clicked.connect(self._fcn_add_score_row)
        self._scoreRm.clicked.connect(self._fcn_rm_score_row)

        # Table edited :
        self._scoreTable.cellChanged.connect(self._fcn_score_to_hypno)

    ##########################################################################
    # UPDATE SCORE <=> HYPNO
    ##########################################################################
    def _fcn_hypno_to_score(self):
        """Update hypno table from hypno data."""
        self._hypno = self._hyp.gui_to_hyp()
        # Avoid updating data while setting cell :
        self._scoreSet = False
        # Remove every info in the table :
        self._scoreTable.setRowCount(0)
        # Find unit conversion :
        fact = self._get_fact_from_unit()
        # Find transient's index, state value and state label
        _, idx, state_values = transient(self._hypno, self._time / fact)
        labels_map = {
            value: lbl for value, lbl in zip(self._hvalues, self._hstates)
        }
        state_labels = [labels_map[value] for value in state_values]
        idx = np.round(10. * idx) / 10.
        # Set length of the table :
        self._scoreTable.setRowCount(len(state_values))
        # Fill the table :
        for k in range(len(state_values)):
            # Add stage start / end :
            self._scoreTable.setItem(k, 0, QtWidgets.QTableWidgetItem(
                str(idx[k, 0])))
            self._scoreTable.setItem(k, 1, QtWidgets.QTableWidgetItem(
                str(idx[k, 1])))
            # Add state :
            self._scoreTable.setItem(k, 2, QtWidgets.QTableWidgetItem(
                state_labels[k]))
        self._scoreSet = True

    def _fcn_score_to_hypno(self):
        """Update hypno data from hypno score."""
        if self._scoreSet:
            # Reset hypnogram (not directly to avoid losing data if failure)
            hypno = np.zeros((len(self._time)), dtype=np.float32)
            # Loop over table row :
            for k in range(self._scoreTable.rowCount()):
                # Get tstart / tend / stage :
                tstart, tend, value = self._get_score_marker(k)
                # Update pos if not None :
                if tstart is not None:
                    hypno[tstart:tend] = value
                    self._hyp.set_state(tstart, tend, value)
            self._hyp.edit.update()
            self._hypno = hypno
            # Update sleep info :
            self._fcn_info_update()

    def _get_score_marker(self, idx):
        """Get a specific row dat.

        This function insure that the edited line is complete and is properly
        formated.

        Parameters
        ----------
        idx : int
            The row from which get data.

        Returns
        -------
        tstart : float
            Time start (in sample)
        tend : float
            Time end (in sample).
        value : int
            The state value
        """
        state_values_map = {
            lbl.lower(): value
            for lbl, value in zip(self._hstates, self._hvalues)
        }
        # Get unit :
        fact = self._get_fact_from_unit()
        # Get selected row :
        # idx = self._scoreTable.currentRow()
        # ============= NON EMPTY ITEM =============
        # Define error message if bad editing :
        errmsg = "\nTable score error. Starting and ending time must be " + \
                 "float numbers (with time start < time end) and stage " + \
                 f"must be in {self._hstates}"
        # Get row data and update if possible:
        tstart_item = self._scoreTable.item(idx, 0)
        tend_item = self._scoreTable.item(idx, 1)
        state_item = self._scoreTable.item(idx, 2)
        if tstart_item and tend_item and state_item:
            # ============= PROPER FORMAT =============
            if all([
                bool(str(tstart_item.text())),
                bool(str(tend_item.text())),
                str(state_item.text()).lower() in [st.lower()
                                                   for st in self._hstates]
            ]):
                try:
                    # Get start / end / stage :
                    tstart = int(float(str(tstart_item.text(
                    ))) * fact * self._sf)
                    tend = int(float(str(tend_item.text())) * fact * self._sf)
                    value = state_values_map[str(state_item.text()).lower()]

                    return tstart, tend, value
                except:
                    raise ValueError(errmsg)
            else:
                raise ValueError(errmsg)
        else:
            return None, None, None

    ##########################################################################
    # EDITING TABLE
    ##########################################################################
    def _fcn_add_score_row(self):
        """Add a row to the table."""
        # Increase length :
        self._scoreTable.setRowCount(self._scoreTable.rowCount() + 1)

    def _fcn_rm_score_row(self):
        """Remove selected row."""
        # Remove row :
        self._scoreTable.removeRow(self._scoreTable.currentRow())
        # Update hypnogram from table :
        self._fcn_score_to_hypno()
