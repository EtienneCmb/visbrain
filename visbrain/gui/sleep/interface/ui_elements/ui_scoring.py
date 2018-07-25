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
        items = ['Wake', 'N1', 'N2', 'N3', 'REM', 'Art']
        # Remove every info in the table :
        self._scoreTable.setRowCount(0)
        # Find unit conversion :
        fact = self._get_fact_from_unit()
        # Find transients :
        _, idx, stages = transient(self._hypno, self._time / fact)
        idx = np.round(10. * idx) / 10.
        # Set length of the table :
        self._scoreTable.setRowCount(len(stages))
        # Fill the table :
        for k in range(len(stages)):
            # Add stage start / end :
            self._scoreTable.setItem(k, 0, QtWidgets.QTableWidgetItem(
                str(idx[k, 0])))
            self._scoreTable.setItem(k, 1, QtWidgets.QTableWidgetItem(
                str(idx[k, 1])))
            # Add stage :
            self._scoreTable.setItem(k, 2, QtWidgets.QTableWidgetItem(
                items[stages[k]]))
        self._scoreSet = True

    def _fcn_score_to_hypno(self):
        """Update hypno data from hypno score."""
        if self._scoreSet:
            # Reset hypnogram :
            self._hypno = np.zeros((len(self._time)), dtype=np.float32)
            # Loop over table row :
            for k in range(self._scoreTable.rowCount()):
                # Get tstart / tend / stage :
                tstart, tend, stage = self._get_score_marker(k)
                # Update pos if not None :
                if tstart is not None:
                    self._hypno[tstart:tend] = stage
                    self._hyp.set_stage(tstart, tend, stage)
            self._hyp.edit.update()
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
        stage : int
            The stage.
        """
        it = {'art': -1., 'wake': 0., 'n1': 1., 'n2': 2., 'n3': 3., 'rem': 4.}
        # Get unit :
        fact = self._get_fact_from_unit()
        # Get selected row :
        # idx = self._scoreTable.currentRow()
        # ============= NON EMPTY ITEM =============
        # Define error message if bad editing :
        errmsg = "\nTable score error. Starting and ending time must be " + \
                 "float numbers (with time start < time end) and stage " + \
                 "must be Wake, N1, N2, N3, REM or Art"
        # Get row data and update if possible:
        tstart_item = self._scoreTable.item(idx, 0)
        tend_item = self._scoreTable.item(idx, 1)
        stage_item = self._scoreTable.item(idx, 2)
        if tstart_item and tend_item and stage_item:
            # ============= PROPER FORMAT =============
            if all([bool(str(tstart_item.text())), bool(str(tend_item.text())),
                    str(stage_item.text()).lower() in it.keys()]):
                try:
                    # Get start / end / stage :
                    tstart = int(float(str(tstart_item.text(
                    ))) * fact * self._sf)
                    tend = int(float(str(tend_item.text())) * fact * self._sf)
                    stage = it[str(stage_item.text()).lower()]

                    return tstart, tend, stage
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
