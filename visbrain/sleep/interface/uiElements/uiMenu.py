"""Main class for sleep menus managment."""


import numpy as np
import os
from PyQt5 import QtWidgets

from ....utils import HelpMenu
from ....io import (dialogSave, dialogLoad, write_fig_hyp, write_csv,
                    write_txt, write_hypno_txt, write_hypno_hyp, read_hypno,
                    is_mne_installed)

__all__ = ['uiMenu']


class uiMenu(HelpMenu):
    """Main class for sleep menus managment."""

    def __init__(self):
        """Init."""
        base = 'http://visbrain.org/sleep.html'
        sections = {'Sleep': base,
                    'Hypnogram scoring': base + '#hypnogram-scoring',
                    'Detections': base + '#apply-semi-automatic-detection',
                    'Annotations': base + '#import-add-and-save-annotations'}
        HelpMenu.__init__(self, sections)
        # _____________________________________________________________________
        #                                 SAVE
        # _____________________________________________________________________
        # Hypnogram :
        self.menuSaveHypnogramData.triggered.connect(self.saveHypData)
        self.menuSaveHypnogramFigure.triggered.connect(self.saveHypFig)
        # Stats info table :
        self.menuSaveInfoTable.triggered.connect(self.saveInfoTable)
        # Scoring table :
        self.menuSaveScoringTable.triggered.connect(self.saveScoringTable)
        # Detections :
        self.menuSaveDetectAll.triggered.connect(self.saveAllDetect)
        self.menuSaveDetectSelected.triggered.connect(self.saveSelectDetect)
        # Sleep GUI config :
        self.menuSaveConfig.triggered.connect(self.saveConfig)
        # Annotations :
        self.menuSaveAnnotations.triggered.connect(self.saveAnnotationTable)
        # Screenshot :
        self.menuSaveScreenshot.triggered.connect(self._fcn_gui_screenshot)

        # _____________________________________________________________________
        #                                 LOAD
        # _____________________________________________________________________
        # Load hypnogram :
        self.menuLoadHypno.triggered.connect(self.loadHypno)
        # Sleep GUI config :
        self.menuLoadConfig.triggered.connect(self.loadConfig)
        # Detections :
        self.menuLoadDetectAll.triggered.connect(self.loadDetectAll)
        self.menuLoadDetectSelect.triggered.connect(self.loadDetectSelect)
        # Annotations :
        self.menuLoadAnnotations.triggered.connect(self.loadAnnotationTable)

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

        # _____________________________________________________________________
        #                               SETTINGS
        # _____________________________________________________________________
        self.menuSettingCleanHyp.triggered.connect(self.settCleanHyp)

    ###########################################################################
    ###########################################################################
    #                           SAVE
    ###########################################################################
    ###########################################################################

    # ______________________ HYPNOGRAM ______________________
    def saveHypData(self, *args, filename=None):
        """Save the hypnogram data either in a hyp or txt file."""
        if filename is None:
            filename = dialogSave(self, 'Save File', 'hypno', "Text file ""(*"
                                  ".txt);;Elan file (*.hyp);;All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)

            # Switch between differents types :
            if ext == '.hyp':
                write_hypno_hyp(filename, self._hypno, self._sf, self._sfori,
                                self._N)
            elif ext == '.txt':
                write_hypno_txt(filename, self._hypno, self._sf, self._sfori,
                                self._N, 1)
            else:
                raise ValueError("Not a valid extension")

    def saveHypFig(self, *args, filename=None, **kwargs):
        """Save a 600 dpi .png figure of the hypnogram."""
        if filename is None:
            filename = dialogSave(self, 'Save Hypnogram figure', 'hypno',
                                  "PNG (*.png);;All files (*.*)")
        if filename:
            write_fig_hyp(filename, self._hypno, self._sf, self._toffset,
                          **kwargs)

    # ______________________ STATS INFO TABLE ______________________
    def saveInfoTable(self, *args, filename=None):
        """Export stat info."""
        # Get file name :
        if filename is None:
            filename = dialogSave(self, 'Save file', 'statsinfo',
                                  "CSV file (*.csv);;Text file (*.txt);;"
                                  "All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(self._keysInfo, self._valInfo))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(self._keysInfo, self._valInfo))

    # ______________________ SCORING TABLE ______________________
    def saveScoringTable(self, *args, filename=None):
        """Export score info."""
        # Read Table
        rowCount = self._scoreTable.rowCount()
        staInd, endInd, stage = [], [], []
        for row in np.arange(rowCount):
            staInd.append(str(self._scoreTable.item(row, 0).text()))
            endInd.append(str(self._scoreTable.item(row, 1).text()))
            stage.append(str(self._scoreTable.item(row, 2).text()))
        # Get file name :
        if filename is None:
            filename = dialogSave(self, 'Save file', 'scoring_info',
                                  "CSV file (*.csv);;Text file (*.txt);;"
                                  "All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(staInd, endInd, stage))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(staInd, endInd, stage))

    # ______________________ DETECTIONS ______________________
    def _CheckDetectMenu(self):
        """Activate/Deactivate the saving detection menu."""
        self.menuSaveDetections.setEnabled(bool(self._detect))

    def saveAllDetect(self, *args, filename=None):
        """Export all detections."""
        # Get file name :
        if filename is None:
            filename = dialogSave(self, 'Save all detections', 'detections',
                                  "NumPy (*.npy);;All files (*.*)")
        if filename:
            file = os.path.splitext(str(filename))[0]
            np.save(file + '.npy', self._detect.dict)

    def saveSelectDetect(self, *args, filename=None):
        """Export selected detection."""
        channel, method = self._getCurrentChanType()
        # Read Table
        rowCount = self._DetectLocations.rowCount()
        staInd = [channel, '', 'Time index (s)']
        endInd = [method, '', 'Time index (s)']
        duration = ['', '', 'Duration (s)']
        stage = ['', '', 'Sleep stage']
        for row in np.arange(rowCount):
            staInd.append(str(self._DetectLocations.item(row, 0).text()))
            endInd.append(str(self._DetectLocations.item(row, 1).text()))
            duration.append(str(self._DetectLocations.item(row, 2).text()))
            stage.append(str(self._DetectLocations.item(row, 3).text()))
        # Get file name :
        saveas = "locinfo" + '_' + channel + '-' + method
        if filename is None:
            filename = dialogSave(self, 'Save ' + method + ' detection',
                                  saveas, "CSV file (*.csv);;Text file (*.txt)"
                                  ";;All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            file += '_' + channel + '-' + method
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(staInd, endInd, duration, stage))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(staInd, endInd, duration, stage))

    # ______________________ SLEEP GUI CONFIG ______________________
    def saveConfig(self, *args, filename=None):
        """Save a config file (*.txt) containing several display parameters."""
        import json
        if filename is None:
            filename = dialogSave(self, 'Save config File', 'config',
                                  "Text file (*.txt);;All files (*.*)")
        if filename:
            with open(filename, 'w') as f:
                config = {}
                # Get channels visibility / amplitude :
                viz, amp = [], []
                for i, k in enumerate(self._chanChecks):
                    viz.append(k.isChecked())
                    amp.append(self._ymaxSpin[i].value())
                config['Channel_Names'] = self._channels
                config['Channel_Visible'] = viz
                config['Channel_Amplitude'] = amp
                config['AllAmpMin'] = self._PanAllAmpMin.value()
                config['AllAmpMax'] = self._PanAllAmpMax.value()
                config['SymAmp'] = self._PanAmpSym.isChecked()
                config['AutoAmp'] = self._PanAmpAuto.isChecked()
                # Spectrogram :
                config['Spec_Visible'] = self.menuDispSpec.isChecked()
                config['Spec_Length'] = self._PanSpecNfft.value()
                config['Spec_Overlap'] = self._PanSpecStep.value()
                config['Spec_Cmap'] = self._PanSpecCmap.currentIndex()
                config['Spec_Chan'] = self._PanSpecChan.currentIndex()
                config['Spec_Fstart'] = self._PanSpecFstart.value()
                config['Spec_Fend'] = self._PanSpecFend.value()
                config['Spec_Con'] = self._PanSpecCon.value()
                # Hypnogram/time axis/navigation/topo/indic/zoom :
                config['Hyp_Visible'] = self.menuDispHypno.isChecked()
                config['Time_Visible'] = self.menuDispTimeax.isChecked()
                config['Topo_Visible'] = self.menuDispTopo.isChecked()
                config['Nav_Visible'] = self.menuDispNavbar.isChecked()
                config['Indic_Visible'] = self.menuDispIndic.isChecked()
                config['Zoom_Visible'] = self.menuDispZoom.isChecked()
                # Navigation bar properties :
                config['Slider'] = self._SlVal.value()
                config['Step'] = self._SigSlStep.value()
                config['Window'] = self._SigWin.value()
                config['Goto'] = self._SlGoto.value()
                config['Magnify'] = self._slMagnify.isChecked()
                config['AbsTime'] = self._slAbsTime.isChecked()
                config['Grid'] = self._slGrid.isChecked()
                config['Unit'] = self._slRules.currentIndex()
                json.dump(config, f)

    # ______________________ ANNOTATION TABLE ______________________
    def saveAnnotationTable(self, *args, filename=None):
        """Export annotation table."""
        # Read Table
        rowCount = self._AnnotateTable.rowCount()
        staInd, endInd, annot = [], [], []
        for row in np.arange(rowCount):
            staInd.append(str(self._AnnotateTable.item(row, 0).text()))
            endInd.append(str(self._AnnotateTable.item(row, 1).text()))
            annot.append(str(self._AnnotateTable.item(row, 2).text()))
        # Get file name :
        if filename is None:
            filename = dialogSave(self, 'Save annotations', 'annotations',
                                  "CSV file (*.csv);;Text file (*.txt);;"
                                  "All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(staInd, endInd, annot))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(staInd, endInd, annot))

    # ______________________ SCREENSHOT ______________________
    def _fcn_gui_screenshot(self):
        """Screenshot using the GUI."""
        self.show_gui_screenshot()

    ###########################################################################
    ###########################################################################
    #                                    LOAD
    ###########################################################################
    ###########################################################################

    def loadHypno(self, *args, filename=None):
        """Load a hypnogram."""
        # Get filename :
        if filename is None:
            filename = dialogLoad(self, 'Load hypnogram File', 'hypno',
                                  "Text file (*.txt);;Elan file (*.hyp);;"
                                  "All files (*.*)")
        if filename:
            # Load the hypnogram :
            self._hypno = read_hypno(filename, len(self._hypno))
            self._hyp.set_data(self._sf, self._hypno, self._time)
            # Update info table :
            self._fcn_infoUpdate()
            # Update scoring table :
            self._fcn_Hypno2Score()
            self._fcn_Score2Hypno()

    def loadConfig(self, *args, filename=None):
        """Load a config file (*.txt) containing several display parameters."""
        import json
        if not filename:
            filename = dialogLoad(self, 'Load config File', 'config',
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
                _try("self._PanAllAmpMin.setValue(config['AllAmpMin'])")
                _try("self._PanAllAmpMax.setValue(config['AllAmpMax'])")
                _try("self._PanAmpSym.setChecked(config['SymAmp'])")
                _try("self._PanAmpAuto.setChecked(config['AutoAmp'])")
                # Spectrogram
                _try("self.menuDispSpec.setChecked(config['Spec_Visible'])")
                _try("self._PanSpecNfft.setValue(config['Spec_Length'])")
                _try("self._PanSpecStep.setValue(config['Spec_Overlap'])")
                _try("self._PanSpecCmap.setCurrentIndex(config['Spec_Cmap'])")
                _try("self._PanSpecChan.setCurrentIndex(config['Spec_Chan'])")
                _try("self._PanSpecFstart.setValue(config['Spec_Fstart'])")
                _try("self._PanSpecFend.setValue(config['Spec_Fend'])")
                _try("self._PanSpecCon.setValue(config['Spec_Con'])")
                # Hypnogram/time axis/navigation/topo/indic/zoom :
                _try("self.menuDispHypno.setChecked(config['Hyp_Visible'])")
                _try("self.menuDispTimeax.setChecked(config['Time_Visible'])")
                _try("self.menuDispTopo.setChecked(config['Topo_Visible'])")
                _try("self.menuDispNavbar.setChecked(config['Nav_Visible'])")
                _try("self.menuDispIndic.setChecked(config['Indic_Visible'])")
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
                self._fcn_chanViz()
                self._fcn_chanAmplitude()
                self._fcn_specSetData()
                self._disptog_spec()
                self._disptog_hyp()
                self._disptog_timeax()
                self._disptog_topo()
                self._disptog_indic()
                self._disptog_zoom()
                self._fcn_gridToggle()
                self._fcn_updateAmpInfo()
                self._fcn_chanAutoAmp()
                self._fcn_chanSymAmp()

    def loadDetectAll(self, *args, filename=None):
        """Load all detections."""
        # Dialog window for detection file :
        if filename is None:
            filename = dialogLoad(self, "Import detections", '',
                                  "NumPy (*.npy);;All files (*.*)")
        self._detect.dict = np.ndarray.tolist(np.load(filename))
        # Made canvas visbles :
        for k in self._detect:
            if self._detect[k]['index'].size:
                # Get channel number :
                idx = self._channels.index(k[0])
                self.canvas_setVisible(idx, True)
                self._chan.visible[idx] = True
        # Plot update :
        self._fcn_sliderMove()
        self._locLineReport()
        self._CheckDetectMenu()

    def loadDetectSelect(self, *args, filename=None):
        """Load a specific detection."""
        # Get file name :
        if filename is None:
            filename = dialogLoad(self, "Import table", '',
                                  "CSV file (*.csv);;Text file (*.txt);;"
                                  "All files (*.*)")
        if filename:
            # Get channel / method from file name :
            (chan, meth) = filename.split('_')[-1].split('.')[0].split('-')
            # Load the file :
            (st, end) = np.genfromtxt(filename, delimiter=',')[3::, 0:2].T
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
            self._fcn_sliderMove()
            self._locLineReport()
            self._CheckDetectMenu()

    def loadAnnotationTable(self, *args, filename=None):
        """Load annotations."""
        # Get file name :
        if filename is None:
            filename = dialogLoad(self, "Import annotations", '',
                                  "CSV file (*.csv);;Text file (*.txt);;"
                                  "All files (*.*)")
        # Clean annotations :
        self._AnnotateTable.setRowCount(0)
        # Load the file :
        if isinstance(filename, str):  # 'file.txt'
            # Get starting/ending/annotation :
            start, end, annot = np.genfromtxt(filename, delimiter=',',
                                              dtype=str).T
        elif isinstance(filename, np.ndarray):
            start = end = filename
            annot = np.array(['enter annotations'] * len(start))
        elif is_mne_installed():  # MNE annotations
            import mne
            if isinstance(filename, mne.annotations.Annotations):
                start = filename.onset
                end = filename.onset + filename.duration
                annot = filename.description
        else:
            raise ValueError("Annotation's type not supported.")

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
        self._fcn_sliderMove()

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
        self._PanSpecW.setEnabled(viz)

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
            self._fcn_topoSettings()
            self._fcn_sliderMove()

    def _disptog_indic(self):
        """Toggle method for display / hide the time indicators."""
        self._specInd.mesh.visible = self.menuDispIndic.isChecked()
        self._hypInd.mesh.visible = self.menuDispIndic.isChecked()
        self._TimeAxis.mesh.visible = self.menuDispIndic.isChecked()
        self._fcn_sliderMove()

    def _disptog_zoom(self):
        """Toggle zoom mode."""
        activeIndic = self.menuDispZoom.isChecked()
        if not activeIndic:
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
        self.menuDispIndic.setChecked(not activeIndic)
        self.menuDispIndic.setEnabled(not activeIndic)
        self._hypInd.mesh.visible = not activeIndic
        self._specInd.mesh.visible = not activeIndic
        self._TimeAxis.mesh.visible = not activeIndic

        self._fcn_sliderSettings()

    ###########################################################################
    ###########################################################################
    #                            SETTINGS
    ###########################################################################
    ###########################################################################
    def settCleanHyp(self):
        """Clean the hypnogram."""
        self._hypno = np.zeros((len(self._hyp),), dtype=np.float32)
        self._hyp.clean(self._sf, self._time)
        # Update info table :
        self._fcn_infoUpdate()
        # Update scoring table :
        self._fcn_Hypno2Score()
        self._fcn_Score2Hypno()
