"""Main class for sleep menus managment."""


import numpy as np
import os
from PyQt5 import QtWidgets

from ....utils import HelpMenu
from ....io import (dialog_save, dialog_load, write_fig_hyp, write_csv,
                    write_txt, write_hypno, read_hypno, annotations_to_array,
                    oversample_hypno, save_config_json)


class UiMenu(HelpMenu):
    """Main class for sleep menus managment."""

    def __init__(self):
        """Init."""
        base = 'http://visbrain.org/sleep.html'
        sections = {'Sleep': base,
                    'Time-frequency': base + '#time-frequency',
                    'Hypnogram scoring': base + '#hypnogram-scoring',
                    'Detections': base + '#apply-semi-automatic-detection',
                    'Annotations': base + '#import-add-and-save-annotations'}
        HelpMenu.__init__(self, sections)
        # _____________________________________________________________________
        #                                 SAVE
        # _____________________________________________________________________
        # Hypnogram :
        self.menuSaveHypnogramData.triggered.connect(self.saveHypData)
        self.menuSaveHypnogramFigure.triggered.connect(self._save_hyp_fig)
        # Stats info table :
        self.menuSaveInfoTable.triggered.connect(self._save_info_table)
        # Scoring table :
        self.menuSaveScoringTable.triggered.connect(self._save_scoring_table)
        # Detections :
        self.menuSaveDetectAll.triggered.connect(self._save_all_detect)
        self.menuSaveDetectSelected.triggered.connect(self._save_select_detect)
        # Sleep GUI config :
        self.menuSaveConfig.triggered.connect(self._save_config)
        # Annotations :
        self.menuSaveAnnotations.triggered.connect(self._save_annotation_table)
        # Screenshot :
        self.menuSaveScreenshot.triggered.connect(self._fcn_gui_screenshot)

        # _____________________________________________________________________
        #                                 LOAD
        # _____________________________________________________________________
        # Load hypnogram :
        self.menuLoadHypno.triggered.connect(self._load_hypno)
        # Sleep GUI config :
        self.menuLoadConfig.triggered.connect(self._load_config)
        # Detections :
        self.menuLoadDetectAll.triggered.connect(self._load_detect_all)
        self.menuLoadDetectSelect.triggered.connect(self._load_detect_select)
        # Annotations :
        self.menuLoadAnnotations.triggered.connect(self._load_annotation_table)

        # _____________________________________________________________________
        #                                 EXIT
        # _____________________________________________________________________
        self.menuExit.triggered.connect(QtWidgets.qApp.quit)

        # _____________________________________________________________________
        #                              DISPLAY
        # _____________________________________________________________________
        # Quick settings panel :
        self.menuDispSettings.triggered.connect(self._disptog_settings)
        self.q_widget.setVisible(True)
        # Spectrogram :
        self.menuDispSpec.triggered.connect(self._disptog_spec)
        # Hypnogram :
        self.menuDispHypno.triggered.connect(self._disptog_hyp)
        # Time axis :
        self.menuDispTimeax.triggered.connect(self._disptog_timeax)
        # Navigation bar :
        self.menuDispNavbar.triggered.connect(self._disptog_navbar)
        # Time indicators :
        self.menuDispIndic.triggered.connect(self._disptog_indic)
        # Topoplot :
        self.menuDispTopo.triggered.connect(self._disptog_topo)
        # Zoom :
        self.menuDispZoom.triggered.connect(self._disptog_zoom)

    ###########################################################################
    ###########################################################################
    #                           SAVE
    ###########################################################################
    ###########################################################################

    # ______________________ HYPNOGRAM ______________________
    def saveHypData(self, *args, filename=None, reply=None):  # noqa
        """Save the hypnogram data either in a hyp or txt file."""
        # Define default filename for the hypnogram :
        if not isinstance(self._file, str):
            hyp_file = 'hypno'
        else:
            hyp_file = os.path.basename(self._file) + '_hypno'
        # Version switch :
        if reply is None:
            msg = ("Since release 0.4, hypnogram are exported using stage "
                   "duration rather than point-per-second. This new format "
                   "avoids potential errors caused by downsampling and "
                   "confusion in the values assigned to each sleep stage. \n\n"
                   "Click 'Yes' to use the new format and 'No' to use the old "
                   "format. For more information, visit the doc at "
                   "visbrain.org/sleep")
            reply = QtWidgets.QMessageBox.question(self, 'Message', msg,
                                                   QtWidgets.QMessageBox.Yes,
                                                   QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.No:  # v1 = sample
            dialog_ext = "Text file (*.txt);;Elan file (*.hyp)"
            version = 'sample'
        else:  # v2 = time
            dialog_ext = ("Text file (*.txt);;Csv file (*.csv);;Excel file "
                          "(*.xlsx)")
            version = 'time'
        # Open dialog window :
        if filename is None:
            filename = dialog_save(self, 'Save File', hyp_file, dialog_ext +
                                   ";;All files (*.*)")
        if filename:
            info = {'Duration_sec': self._N * 1 / self._sfori}
            if isinstance(self._file, str):
                info['Datafile'] = self._file
            write_hypno(filename, self._hypno, version=version, sf=self._sfori,
                        npts=self._N, time=self._time, info=info)

    def _save_hyp_fig(self, *args, filename=None, **kwargs):
        """Save a 600 dpi .png figure of the hypnogram."""
        if filename is None:
            filename = dialog_save(self, 'Save Hypnogram figure', 'hypno',
                                   "PNG (*.png);;All files (*.*)")
        if filename:
            hypno = self._hypno.copy()
            grid = self._slGrid.isChecked()
            ascolor = self._PanHypnoColor.isChecked()
            write_fig_hyp(hypno, self._sf, file=filename,
                          start_s=self._toffset, grid=grid, ascolor=ascolor)

    # ______________________ STATS INFO TABLE ______________________
    def _save_info_table(self, *args, filename=None):
        """Export stat info."""
        # Get file name :
        if filename is None:
            filename = dialog_save(self, 'Save file', 'statsinfo',
                                   "CSV file (*.csv);;Text file (*.txt);;"
                                   "All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(self._keysInfo, self._valInfo))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(self._keysInfo, self._valInfo))

    # ______________________ SCORING TABLE ______________________
    def _save_scoring_table(self, *args, filename=None):
        """Export score info."""
        # Read Table
        row_count = self._scoreTable.rowCount()
        sta_ind, end_ind, stage = [], [], []
        for row in np.arange(row_count):
            sta_ind.append(str(self._scoreTable.item(row, 0).text()))
            end_ind.append(str(self._scoreTable.item(row, 1).text()))
            stage.append(str(self._scoreTable.item(row, 2).text()))
        # Get file name :
        if filename is None:
            filename = dialog_save(self, 'Save file', 'scoring_info',
                                   "CSV file (*.csv);;Text file (*.txt);;"
                                   "All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(sta_ind, end_ind, stage))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(sta_ind, end_ind, stage))

    # ______________________ DETECTIONS ______________________
    def _check_detect_menu(self):
        """Activate/Deactivate the saving detection menu."""
        self.menuSaveDetections.setEnabled(bool(self._detect))

    def _save_all_detect(self, *args, filename=None):
        """Export all detections."""
        # Get file name :
        if filename is None:
            filename = dialog_save(self, 'Save all detections', 'detections',
                                   "NumPy (*.npy);;All files (*.*)")
        if filename:
            file = os.path.splitext(str(filename))[0]
            np.save(file + '.npy', self._detect.dict)

    def _save_select_detect(self, *args, filename=None):
        """Export selected detection."""
        channel, method = self._get_current_chan_type()
        # Read Table
        row_count = self._DetectLocations.rowCount()
        sta_ind = [channel, '', 'Time index (s)']
        end_ind = [method, '', 'Time index (s)']
        duration = ['', '', 'Duration (s)']
        stage = ['', '', 'Sleep stage']
        for row in np.arange(row_count):
            sta_ind.append(str(self._DetectLocations.item(row, 0).text()))
            end_ind.append(str(self._DetectLocations.item(row, 1).text()))
            duration.append(str(self._DetectLocations.item(row, 2).text()))
            stage.append(str(self._DetectLocations.item(row, 3).text()))
        # Get file name :
        saveas = "locinfo" + '_' + channel + '-' + method
        if filename is None:
            filename = dialog_save(self, 'Save ' + method + ' detection',
                                   saveas, "CSV file (*.csv);;Text file"
                                   " (*.txt);;All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            file += '_' + channel + '-' + method
            zp = zip(sta_ind, end_ind, duration, stage)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zp)
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zp)

    # ______________________ SLEEP GUI CONFIG ______________________
    def _save_config(self, *args, filename=None):
        """Save a config file (*.txt) containing several display parameters."""
        if filename is None:
            filename = dialog_save(self, 'Save config File', 'config',
                                   "JSON file (*.json);;Text file (*.txt)")
        if filename:
            config = {}
            # Get channels visibility / amplitude :
            viz, amp = [], []
            for i, k in enumerate(self._chanChecks):
                viz.append(k.isChecked())
                amp.append(self._ymaxSpin[i].value())
            config['Channel_Names'] = self._channels
            config['Channel_Visible'] = viz
            config['Channel_Amplitude'] = amp
            # config['AllAmpMin'] = self._PanAllAmpMin.value()
            # config['AllAmpMax'] = self._PanAllAmpMax.value()
            config['SymAmp'] = self._PanAmpSym.isChecked()
            config['AutoAmp'] = self._PanAmpAuto.isChecked()
            # Spectrogram :
            config['Spec_Visible'] = self.menuDispSpec.isChecked()
            config['Spec_Method'] = self._PanSpecMethod.currentIndex()
            config['Spec_Length'] = self._PanSpecNfft.value()
            config['Spec_Overlap'] = self._PanSpecStep.value()
            config['Spec_Cmap'] = self._PanSpecCmap.currentIndex()
            config['Spec_CmapInv'] = self._PanSpecCmapInv.isChecked()
            config['Spec_Chan'] = self._PanSpecChan.currentIndex()
            config['Spec_Fstart'] = self._PanSpecFstart.value()
            config['Spec_Fend'] = self._PanSpecFend.value()
            config['Spec_Con'] = self._PanSpecCon.value()
            config['Spec_Interp'] = self._PanSpecInterp.currentIndex()
            # Hypnogram/time axis/navigation/topo/indic/zoom :
            config['Hyp_Visible'] = self.menuDispHypno.isChecked()
            config['Time_Visible'] = self.menuDispTimeax.isChecked()
            config['Topo_Visible'] = self.menuDispTopo.isChecked()
            config['Nav_Visible'] = self.menuDispNavbar.isChecked()
            config['Indic_Visible'] = self.menuDispIndic.isChecked()
            config['Zoom_Visible'] = self.menuDispZoom.isChecked()
            config['Hyp_Lw'] = self._PanHypnoLw.value()
            config['Hyp_Color'] = self._PanHypnoColor.isChecked()
            # Navigation bar properties :
            config['Slider'] = self._SlVal.value()
            config['Step'] = self._SigSlStep.value()
            config['Window'] = self._SigWin.value()
            config['Goto'] = self._SlGoto.value()
            config['Magnify'] = self._slMagnify.isChecked()
            config['AbsTime'] = self._slAbsTime.isChecked()
            config['Grid'] = self._slGrid.isChecked()
            config['Unit'] = self._slRules.currentIndex()
            save_config_json(filename, config)

    # ______________________ ANNOTATION TABLE ______________________
    def _save_annotation_table(self, *args, filename=None):
        """Export annotation table."""
        # Read Table
        row_count = self._AnnotateTable.rowCount()
        sta_ind, end_ind, annot = [], [], []
        for row in np.arange(row_count):
            sta_ind.append(str(self._AnnotateTable.item(row, 0).text()))
            end_ind.append(str(self._AnnotateTable.item(row, 1).text()))
            annot.append(str(self._AnnotateTable.item(row, 2).text()))
        # Get file name :
        if filename is None:
            filename = dialog_save(self, 'Save annotations', 'annotations',
                                   "CSV file (*.csv);;Text file (*.txt);;"
                                   "All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(sta_ind, end_ind, annot))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(sta_ind, end_ind, annot))

    # ______________________ SCREENSHOT ______________________
    def _fcn_gui_screenshot(self):
        """Screenshot using the GUI."""
        self.show_gui_screenshot()

    ###########################################################################
    ###########################################################################
    #                                    LOAD
    ###########################################################################
    ###########################################################################

    def _load_hypno(self, *args, filename=None):
        """Load a hypnogram."""
        # Define default filename for the hypnogram :
        if not isinstance(self._file, str):
            hyp_file = 'hypno'
        else:
            hyp_file = os.path.basename(self._file) + '_hypno'
        # Get filename :
        if filename is None:
            filename = dialog_load(self, 'Load hypnogram File', hyp_file,
                                   "Text file (*.txt);;CSV file (*.csv);;"
                                   "Elan file (*.hyp);;Excel file (*.xlsx);;"
                                   "All files (*.*)")
        if filename:
            # Load the hypnogram :
            self._hypno, _ = read_hypno(filename, time=self._time)
            self._hypno = oversample_hypno(self._hypno, self._N)[::self._dsf]
            self._hyp.set_data(self._sf, self._hypno, self._time)
            # Update info table :
            self._fcn_info_update()
            # Update scoring table :
            self._fcn_hypno_to_score()
            self._fcn_score_to_hypno()

    def _load_config(self, *args, filename=None):
        """Load a config file (*.txt) containing several display parameters."""
        import json
        if not filename:
            filename = dialog_load(self, 'Load config File', 'config',
                                   "Text file (*.txt);;All files (*.*)")
        if filename:
            with open(filename) as f:
                # Load the configuration file :
                config = json.load(f)

                def _try(string, self=self, config=config):
                    """Execute the string.

                    This function insure backward compatibility for loading the
                    configuration file.
                    """
                    try:
                        exec(string)
                    except:
                        pass

                # Channels
                for i, k in enumerate(self._chanChecks):
                    self._chanChecks[i].setChecked(
                        config['Channel_Visible'][i])
                    self._ymaxSpin[i].setValue(config['Channel_Amplitude'][i])
                # Amplitudes :
                # _try("self._PanAllAmpMin.setValue(config['AllAmpMin'])")
                # _try("self._PanAllAmpMax.setValue(config['AllAmpMax'])")
                _try("self._PanAmpSym.setChecked(config['SymAmp'])")
                _try("self._PanAmpAuto.setChecked(config['AutoAmp'])")
                # Spectrogram
                _try("self.menuDispSpec.setChecked(config['Spec_Visible'])")
                _try("self._PanSpecMethod.setCurrentIndex("
                     "config['Spec_Method'])")
                _try("self._PanSpecNfft.setValue(config['Spec_Length'])")
                _try("self._PanSpecStep.setValue(config['Spec_Overlap'])")
                _try("self._PanSpecCmap.setCurrentIndex(config['Spec_Cmap'])")
                _try("self._PanSpecCmapInv.setChecked(config['Spec_CmapInv'])")
                _try("self._PanSpecChan.setCurrentIndex(config['Spec_Chan'])")
                _try("self._PanSpecFstart.setValue(config['Spec_Fstart'])")
                _try("self._PanSpecFend.setValue(config['Spec_Fend'])")
                _try("self._PanSpecCon.setValue(config['Spec_Con'])")
                _try("self._PanSpecInterp.setCurrentIndex("
                     "config['Spec_Interp'])")
                # Hypnogram/time axis/navigation/topo/indic/zoom :
                _try("self.menuDispHypno.setChecked(config['Hyp_Visible'])")
                _try("self.menuDispTimeax.setChecked(config['Time_Visible'])")
                _try("self.menuDispTopo.setChecked(config['Topo_Visible'])")
                _try("self.menuDispNavbar.setChecked(config['Nav_Visible'])")
                _try("self.menuDispIndic.setChecked(config['Indic_Visible'])")
                _try("self._PanHypnoLw.setValue(config['Hyp_Lw'])")
                _try("self._PanHypnoColor.setChecked(config['Hyp_Color'])")
                # Navigation bar properties :
                _try("self._SlVal.setValue(config['Slider'])")
                _try("self._SigSlStep.setValue(config['Step'])")
                _try("self._SigWin.setValue(config['Window'])")
                _try("self._SlGoto.setValue(config['Goto'])")
                _try("self._slMagnify.setChecked(config['Magnify'])")
                _try("self._slAbsTime.setChecked(config['AbsTime'])")
                _try("self._slGrid.setChecked(config['Grid'])")
                _try("self._slRules.setCurrentIndex(config['Unit'])")
                # Update display
                self._fcn_chan_viz()
                self._fcn_chan_amplitude()
                self._fcn_spec_set_data()
                self._disptog_spec()
                self._disptog_hyp()
                self._disptog_timeax()
                self._disptog_topo()
                self._disptog_indic()
                self._disptog_zoom()
                self._fcn_grid_toggle()
                self._fcn_update_amp_info()
                self._fcn_chan_auto_amp()
                self._fcn_chan_sym_amp()
                self._fcn_set_hypno_lw()
                self._fcn_set_hypno_color()

    def _load_detect_all(self, *args, filename=None):
        """Load all detections."""
        # Dialog window for detection file :
        if filename is None:
            filename = dialog_load(self, "Import detections", '',
                                   "NumPy (*.npy);;All files (*.*)")
        self._detect.dict = np.ndarray.tolist(np.load(filename))
        # Made canvas visbles :
        for k in self._detect:
            if self._detect[k]['index'].size:
                # Get channel number :
                idx = self._channels.index(k[0])
                self._canvas_set_visible(idx, True)
                self._chan.visible[idx] = True
        # Plot update :
        self._fcn_slider_move()
        self._loc_line_report()
        self._check_detect_menu()

    def _load_detect_select(self, *args, filename=None):
        """Load a specific detection."""
        # Get file name :
        if filename is None:
            filename = dialog_load(self, "Import table", '',
                                   "CSV file (*.csv);;Text file (*.txt);;"
                                   "All files (*.*)")
        if filename:
            # Get channel / method from file name :
            (chan, meth) = filename.split('_')[-1].split('.')[0].split('-')
            # Load the file :
            (st, end) = np.genfromtxt(filename, delimiter=',',
                                      encoding='utf-8')[3::, 0:2].T
            # Sort by starting index :
            idxsort = np.argsort(st)
            st, end = st[idxsort], end[idxsort]
            # Concatenate (starting, ending) index :
            index = np.c_[st, end]
            # Convert into index :
            index = np.round(index * self._sf).astype(int)
            # Set index :
            self._detect[(chan, meth)]['index'] = index
            # Plot update :
            self._fcn_slider_move()
            self._loc_line_report()
            self._check_detect_menu()

    def _load_annotation_table(self, *args, filename=None):
        """Load annotations."""
        # Get file name :
        if filename is None:
            filename = dialog_load(self, "Import annotations", '',
                                   "CSV file (*.csv);;Text file (*.txt);;"
                                   "All files (*.*)")
        # Clean annotations :
        self._AnnotateTable.setRowCount(0)
        start, end, annot = annotations_to_array(filename)

        # Fill table :
        self._AnnotateTable.setRowCount(len(start))
        # File the table :
        for k, (s, e, a) in enumerate(zip(start, end, annot)):
            # Starting index :
            self._AnnotateTable.setItem(
                k, 0, QtWidgets.QTableWidgetItem(str(s)))
            # Ending index :
            self._AnnotateTable.setItem(
                k, 1, QtWidgets.QTableWidgetItem(str(e)))
            # Text :
            self._AnnotateTable.setItem(
                k, 2, QtWidgets.QTableWidgetItem(str(a)))
            # Set the current tab to the annotation tab :
            self.QuickSettings.setCurrentIndex(5)
        # Set markers :
        middle = (start.astype(np.float32) + end.astype(np.float32)) / 2
        self._annot_mark = middle
        self._fcn_slider_move()

    ###########################################################
    ###########################################################
    #                            DISPLAY
    ###########################################################
    ###########################################################

    def _disptog_settings(self):
        """Toggle method for display / hide the settings panel.

        Shortcut : CTRL + D
        """
        viz = self.q_widget.isVisible()
        self.q_widget.setVisible(not viz)
        # Set topo widget larger if settings panel hide :
        self._topoW.setMaximumWidth(300 * (1 + .7 * viz))

    def _disptog_spec(self):
        """Toggle method for display / hide the spectrogram.

        Shortcut : S
        """
        viz = self.menuDispSpec.isChecked()
        self._SpecW.setVisible(viz)
        self._specLabel.setVisible(viz)

    def _disptog_hyp(self):
        """Toggle method for display / hide the hypnogram.

        Shortcut : H
        """
        viz = self.menuDispHypno.isChecked()
        self._HypW.setVisible(viz)
        self._hypLabel.setVisible(viz)

    def _disptog_navbar(self):
        """Toggle method for display / hide the navigation bar.

        Shortcut : P
        """
        self._slFrame.hide() if self._slFrame.isVisible(
        ) else self._slFrame.show()

    def _disptog_timeax(self):
        """Toggle method for display / hide the time axis.

        Shortcut : X
        """
        viz = self.menuDispTimeax.isChecked()
        self._TimeAxisW.setVisible(viz)
        self._timeLabel.setVisible(viz)

    def _disptog_topo(self):
        """Toggle method for display / hide the topoplot.

        Shortcut : T
        """
        viz = self.menuDispTopo.isChecked()
        self._topoW.setVisible(viz)
        self._PanTopoVizW.setEnabled(viz)
        if viz:
            self._fcn_topo_settings()
            self._fcn_slider_move()

    def _disptog_indic(self):
        """Toggle method for display / hide the time indicators."""
        viz = self.menuDispIndic.isChecked()
        self._specInd.mesh.visible = viz
        self._hypInd.mesh.visible = viz
        self._TimeAxis.mesh.visible = viz
        self._fcn_slider_move()

    def _disptog_zoom(self):
        """Toggle zoom mode."""
        active_indic = self.menuDispZoom.isChecked()
        if not active_indic:
            # Spectrogram camera :
            self._speccam.rect = (self._time.min(), self._spec.freq[0],
                                  self._time.max() - self._time.min(),
                                  self._spec.freq[-1] - self._spec.freq[0])
            self._specInd.mesh.visible = self.menuDispIndic.isChecked()
            # Hypnogram camera :
            self._hypcam.rect = (self._time.min(), -5.,
                                 self._time.max() - self._time.min(), 7.)
            # Time camera :
            self._timecam.rect = (self._time.min(), 0.,
                                  self._time.max() - self._time.min(), 1.)

        # Activate / Deactivate indicators :
        self.menuDispIndic.setChecked(not active_indic)
        self.menuDispIndic.setEnabled(not active_indic)
        self._hypInd.mesh.visible = not active_indic
        self._specInd.mesh.visible = not active_indic
        self._TimeAxis.mesh.visible = not active_indic

        self._fcn_slider_settings()
