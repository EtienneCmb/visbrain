.. _SleepModule:

.. currentmodule:: visbrain.gui

Sleep
=====

.. admonition:: Overview
   :class: sd-bg-light

   Sleep is a flexible graphical user interface for visualising, analysing and
   scoring polysomnographic data.  The Phase 5 refactor adopts a
   model/view/controller split where ``SleepDataset`` encapsulates recordings,
   ``SleepView`` renders the Qt widgets and ``SleepController`` orchestrates
   interactions.  Launch the façade via :class:`~visbrain.gui.Sleep` or run
   curated demos with
   ``python -m visbrain.examples run sleep/<example>``.  If you use Sleep in a
   publication, please cite the article in `Frontiers in Neuroinformatics
   <http://journal.frontiersin.org/article/10.3389/fninf.2017.00060/full>`_.

Checkout the API of the :class:`~visbrain.gui.Sleep` class. If you need help
with the :class:`~visbrain.gui.Sleep` module, ask your questions in the
dedicated `gitter Sleep chat
<https://gitter.im/visbrain-python/Sleep?utm_source=share-link&utm_medium=link&utm_campaign=share-link>`_.

.. figure::  _static/sleep/sleep_main.png
   :align:   center

.. contents:: Contents
   :local:
   :depth: 2

.. ##########################################################################
.. ##########################################################################
..                                 DESCRIPTION
.. ##########################################################################
.. ##########################################################################

Main features
~~~~~~~~~~~~~

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item-card:: Graphical user interface
      :class-card: sd-bg-primary sd-text-white

      * Modular Qt panes with responsive layouts.
      * High-DPI screenshots for publications.
      * Persisted channel selection, amplitude ranges and panel visibility.

   .. grid-item-card:: Loader flexibility
      :class-card: sd-bg-light

      * Built-in EDF, BrainVision, Micromed and Elan readers.
      * Optional ``mne`` integration for additional formats.
      * Hypnogram importers for ``.txt``, ``.csv``, ``.xlsx`` and ``.hyp``.

   .. grid-item-card:: Multi-pane displays
      :class-card: sd-bg-light

      * Time-series, spectrogram, hypnogram and topographic map panes stay
        synchronised.
      * Configurable down-sampling and rescaling pipelines.
      * Shared navigation shortcuts across panes.

   .. grid-item-card:: Hypnogram tooling
      :class-card: sd-bg-light

      * Inline editing with statistics refreshed in real time.
      * Publication-grade exports of scoring timelines.
      * Stage dictionaries resolved from bundled templates.

   .. grid-item-card:: Signal processing
      :class-card: sd-bg-light

      * Demean, detrend and filter recordings interactively.
      * Re-reference to a single channel or common average.
      * Bipolar derivations and envelope tracking.

   .. grid-item-card:: Event detection
      :class-card: sd-bg-light

      * Semi-automatic detection of spindles, K-complexes, slow waves and REM
        events.
      * Operate on one or multiple channels simultaneously.
      * Review detections in tables linked to the hypnogram timeline.


Import and use sleep
~~~~~~~~~~~~~~~~~~~~

The :class:`~visbrain.gui.Sleep` module can be imported as follow :

.. code-block:: python

    from visbrain.gui import Sleep
    # Run the interface (requires loading of a data file):
    Sleep().show()


GUI description
~~~~~~~~~~~~~~~

Components
^^^^^^^^^^

The :class:`~visbrain.gui.Sleep` GUI is divided into 4 main parts:

.. figure::  _static/sleep/sleep_main_parts.png
   :align:   center


**Menu** :
The contextual menu allows to perform several functions such as the loading and saving of data files, hypnogram files, screenshots, GUI configuration.. It is also useful to control the visbility of each panel, display a list of shortcuts, or open the documentation.

**Main window** :
    * Polysomnographic data
    * Spectrogram (= time-frequency) of the whole recording
    * Hypnogram
    * Topoplot (*hidden by default*)

**Navigation bar** :
    * *Go to* : go to the time location of your choice
    * *[Display] Window* : length of the displayed time window
    * *Scoring window* : length of the scoring time window 
    * *Slider step* : step between each consecutive display windows
    * *Rule* : display unit in second, minute or hours
    * *Grid* : display the grid on the hypnogram and channel plot
    * *Magnify* : apply a zoom on the signal (e.g. useful to examine short events such as spindles). Alternatively, you can use CTRL + click at any time to zoom on a specific signal and time point.
    * *Display scoring window* : Hide or display vertical bars onto the data to indicate the limits of the current scoring window.
    * *Lock scoring to display* : When this option is selected (default), the scoring window is equal to the display window. When this option is off, the epoch used for scoring can be independent from the displayed epoch. See :ref:`hypnogram_scoring`..

**Settings panel** :
The setting panels is where most of the (advanced) functions of the software are! Among other things, you can control which channel to display, adjust the amplitudes, customize the spectrogram and hypnogram, compute the duration of each sleep stage, add annotations to the recording, and perform a bunch of semi-automatic detection (spindles, K-complexes...). See the section :ref:`sleep_settings_panel` for a description of each tab.

Themes and accessibility
~~~~~~~~~~~~~~~~~~~~~~~~

Sleep ships with the same runtime theme manager as the Brain module.  Use the
:menuselection:`Display --> Theme` submenu to toggle between the high contrast
``Dark`` palette and the presentation-friendly ``Light`` variant; Visbrain
persists the preference between launches so workshop demos and automated screen
captures stay consistent.

.. note::
   Generate theme previews with the Task 8 screenshot harness referenced in
   :doc:`modernization/phase-3` when preparing documentation updates.  The
   captures land in ``docs/_static/brain/`` during the build step so writers can
   embed or review them locally, but the PNG files stay out of version control.

All canvases (channel grid, spectrogram, hypnogram, topo map and the global time
axis) request keyboard focus and expose accessible names/descriptions, allowing
screen readers and :kbd:`Tab` navigation to reference the active visualization.
Global shortcuts remain active regardless of focus—for example :kbd:`Ctrl+D`
toggles the settings panel, :kbd:`Ctrl+S` saves the hypnogram and :kbd:`Ctrl+T`
opens the keyboard reference panel.  The :menuselection:`Help --> Shortcuts`
entry uses the same accessible table as the Brain module and surfaces the
scoring keys (:kbd:`1`/ :kbd:`2`/ :kbd:`3`, :kbd:`R`, etc.) alongside utility
actions.

.. note::
   Use the same Task 8 harness to refresh the shortcuts helper overlay for Sleep
   when preparing tutorials or changelogs.  Share the resulting PNGs alongside
   release artifacts instead of checking them into the repository.

.. _sleep_settings_panel:

Settings panel tabs
^^^^^^^^^^^^^^^^^^^

There are five settings tabs :

* :ref:`paneltab` : manage channel, time-frequency, hypnogram and topographic map
* :ref:`toolstab` : signal processing tools (*e.g filtering, re-referencing*)
* :ref:`infotab` : sleep statistics and basic infos on the EEG recording
* :ref:`scoringtab` : a scoring table that can be used to edit the hypnogram
* :ref:`detectiontab` : automatic events detections
* :ref:`annotationtab` : manage annotations

.. _paneltab:

Panels
++++++

Manage channel, time-frequency, hypnogram and topographic map

.. figure::  _static/sleep/sleep_topo.png
   :align:   center

   The Settings panel: topoplot properties

* *Channels*
    * Show / hide channels :
        * Select the channels to display by clicking on the corresponding checkbox
        * Alternatively, you can click on display / hide all channels
    * Control the amplitude :
        * Per channel
        * By setting all amplitudes at once
        * Use symmetric amplitudes (-M, +M)
        * Use automatic amplitude (each amplitude fit to the (minimum, maximum) of the current displayed window)
* *Time-frequency*
    * Customize the spectrogram
        * Channel on which to compute the time-frequency
        * Computation method (see :ref:`time_frequency`)
        * Starting and ending frequencies
        * Time length window and overlap
        * Colormap
* *Hypnogram*
    * Customize the hypnogram
        * line width and line color
* *Topoplot*
    * Customize the topographic map (topoplot)
        * Show / hide topoplot
        * Display either the filtered signal, the amplitude or the power in specific frequency band
        * Colormap control

.. _toolstab:

Tools
+++++

Signal processing and re-referencing tools.

.. figure::  _static/sleep/sleep_filtering.png
   :align:   center

   Bandpass filter (12-14 Hz) applied on all channels.

* Signal processing (*apply in real time*)
    * Apply de-meaning and de-trending
    * filtering* and re-referencing which are applied directly on the signal and spectrogram (see image above)
* Re-referencing
    * Common average
    * Bipolarization (useful for intra-cranial EEG data)

.. _infotab:

Infos
+++++

The Infos panel displays the recording infos (e.g. name and downsampling frequency) as well as the main sleep statistics computed with the hypnogram (see specs below). These values are adjusted in real-time when you edit the hypnogram. Sleep statistics can be exported to **.csv** or **.txt** file.

.. figure::  _static/sleep/sleep_info.png
   :align:   center

   The Infos panel: sleep statistics and basic infos of the current recording.

* File properties
    * Filename
    * Sampling frequency
    * Down-sampling frequency
* Sleep statistics (*All values are expressed in minutes*):
    * Time in Bed (TIB) : total duration of the hypnogram
    * Total Dark Time (TDT) : duration of the hypnogram from beginning to last period of sleep
    * Sleep Period Time (SPT) : duration from first to last period of sleep
    * Wake After Sleep Onset (WASO) : duration of wake periods within SPT
    * Sleep Efficiency (SE) : TST / TDT * 100 (%)
    * Total Sleep Time (TST) : SPT - WASO
    * W, N1, N2, N3 and REM : sleep stages duration
    * Latencies : latencies of sleep stages from the beginning of the record

.. _scoringtab:

Scoring
+++++++

This tab contains the scoring table, i.e. where each stage start and finish. For further informations about how to score your hypnogram see :ref:`hypnogram_scoring`.

.. _detectiontab:

Detections
++++++++++

Perform semi-automatic detection of phasic events, such as sleep spindles, K-complexes, rapid eye movements...For a full tutorial see :ref:`apply_detection`.

.. _annotationtab:

Annotations
+++++++++++

Add and edit annotations (annotations are defined by a start and end point, as well as an optional text marker). To quickly add annotations:

* Use the *Annotate* button in the ruler to annotate the entire window
* Double click (with left mouse button) on a channel to add an annotation starting and finishing at the mouse cursor location.

If you want to import / export annotations, see the :ref:`import_annotation`

Shortcuts
^^^^^^^^^

Sleep comes with a bundle of shortcuts that can be used to speed up your productivity. If shortcuts do not work, simply left click on a canvas.

===================     =======================================================
Keys                    Description
===================     =======================================================
mouse wheel             Move the current window
double left click       Add annotation under mouse cursor
\-                      Decrease amplitude
\+                      Increase amplitude
a                       Score the current epoch as Artefact
w                       Score the current epoch as Wake
1                       Score the current epoch as N1
2                       Score the current epoch as N2
3                       Score the current epoch as N3
r                       Score the current epoch as REM
b                       Previous window
n                       Next window
s                       Display / hide spectrogram
t                       Display / hide topoplot
h                       Display / hide hypnogram
p                       Display / hide navigation bar
x                       Display / hide time axis
g                       Display / hide grid
z                       Enable / disable zoom
i                       Enable / disable indicators
CTRL + Num              Display / hide the channel Num [0, 9]
CTRL + left click       On a channel canvas, magnify signal under mouse location
CTRL + d                Display quick settings panel
CTRL + s                Save hypnogram
CTRL + n                Screenshot window
CTRL + e                Display documentation
CTRL + t                Display shortcuts window
CTRL + q                Close the window
===================     =======================================================

.. ##########################################################################
.. ##########################################################################
..                                 TUTORIAL
.. ##########################################################################
.. ##########################################################################

.. ----------------------------------------------------------------------------
..                              SUPPORTED FILES
.. ----------------------------------------------------------------------------

Supported files and format
~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`~visbrain.gui.Sleep` natively supports several file formats for both electrophysiological and hypnogram data.

Data files
^^^^^^^^^^

Here’s the list of natively supported file formats:

* **.vhdr** (BrainVision version 1 and 2)
* **.edf** (European Data Format)
* **.trc** (Micromed version 4)
* **.eeg** (`ELAN <http://elan.lyon.inserm.fr>`_)

If MNE-python is installed, this list is extended to (see `also <https://martinos.org/mne/dev/manual/io.html#importing-eeg-data>`_) :

* **.bdf**
* **.gdf**
* **.egi**
* **.mff**
* **.set** (EEGLAB)
* **.cnt**
* **.vhdr** (*BrainVision files can be loaded using either the native library of Sleep or using MNE*)

Note that once MNE-python is installed, the loading of these file formats is transparent for users. It means that you can load these file formats directly using Sleep graphical user interface or command-line, without any additional steps. We therefore **strongly recommand** to `install MNE-python <https://martinos.org/mne/stable/index.html>`_.

If you have a file format that is currently not supported, :class:`~visbrain.gui.Sleep` also provide the ability to directly pass raw data (NumPy array). Please see the ``examples/gui_sleep/load_matlab.py`` example (launch it with ``python -m visbrain.examples run sleep/load_matlab``) for a step-by-step walkthrough before passing the data directly to Sleep.

.. note::
  If you are having trouble with the loading of .edf files, we recommand installing `MNE-python <https://martinos.org/mne/stable/index.html>`_ and then loading your data using the following command::

    Sleep(data='mydata.edf', hypno='myhypno.csv', use_mne=True).show()

  This will force the loading of the .edf files using MNE, which can generally handle more cases and exceptions than the native EDF library implemented in :class:`~visbrain.gui.Sleep`.

.. caution::
   By default, data are **automatically downsampled to 100 Hz** upon loading. If the sampling frequency of your recording is a power of two (e.g. 256, 512 Hz), we recommand to change the default downsampling value to 128 Hz using the following command::

    Sleep(data='mydata.edf', hypno='myhypno.csv', downsample=128).show()

Hypnogram
^^^^^^^^^

One of the main objective of Sleep is to **facilitate the sharing of data** across laboratories. This involves being able to accomodate for a variety of hypnogram format (unfortunately, there is no current gold standard on how to save hypnogram data). Here's the list of supported extensions for hypnogram files :

* **.txt**
* **.csv**
* **.xlsx**
* **.edf** (EDF+)
* **.hyp** (`ELAN <http://elan.lyon.inserm.fr>`_)

.. warning::
   Please note that Sleep uses the guidelines of *Iber et al. 2007* for sleep stage nomenclature (Wake, N1, N2, N3, REM and Artefact). If your hypnogram includes both NREM-S3 and NREM-S4 sleep stages you can add “N4” categories with the corresponding values in the description file. However, keep in mind that S3 and S4 will be merged into N3 during the import to the Sleep module. That also means that if you load and then save your hypnogram in Sleep, you will loose differentiation between S3 and S4 so be sure not to overwrite your original file!


Save hypnogram
^^^^^^^^^^^^^^

.. important::
  Since release v0.4, the default hypnogram export format uses stage duration rather than point-per-second encoding. This format avoids potential errors caused by downsampling and confusion in the values assigned to each sleep stage (which can drastically differ between two labs, e.g. N2 sleep can be encoded with the value 2 in one lab, and -2 in another lab). However, for retro-compatibility, we still allow user to save and load hypnogram in point-per-second format. Please see the image below to see the difference between stage-duration and point-per-second encoding.

.. figure::  _static/sleep/hypno_encoding.png
   :align:   center

By default, Sleep will save your hypnogram in .txt, using the stage-duration encoding:

==============          =================
Stage                    Duration
==============          =================
**Wake**                500
**N1**                  750
**N2**                  2000
**N3**                  3000
**N2**                  3200
...                     ...
**REM**                 30018
**Wake**                30100
==============          =================

**How to read the example above?**

The subject was awake from 0 to 500 seconds, then fell in N1 sleep between 500 to 750 seconds, then in N2 sleep between 750 to 2000 seconds, then in N3 sleep and so on. The subject was awakened in REM sleep, and the recording was stopped shortly after. The total duration of the recording (in seconds) corresponds to the last value of the hypnogram, in that case 30100 seconds.

The main advantages of using such an encoding format for the hypnogram is that it avoids any confusion related to the values used for each sleep stage, and drastically reduces the hypnogram file length without loosing any information. Please note that the software contains command-line functions to convert between point-per-second and stage-duration encoding.

.. tip::
  If you want to add any relevant informations / comments to the hypnogram, you can do so by adding lines preceded by an asterisk directly within the text file. Sleep will not read any line in the hypnogram that starts with an asterisk mark. For example, you can add the name of the scorer::

    *Scorer  John
    *Date    05_17_2018
    Wake     500
    N1       750


Elan .hyp format
++++++++++++++++

Alternatively, if you prefer point-per-second encoding, you can save your data in .hyp format, which can be read with any text editor. Sleep will create a single .hyp file with 4 header rows and the values presented above for the sleep stages, with the exception that the value assigned to REM sleep will be 5 for compatibility with Elan hypnogram reader.


.. important::
   If your hypnogram was created using another software, and is encoded in point-per-second, it is important that Sleep knows which value is associated with each sleep stage (e.g. 2 = N2 sleep, 4 = REM sleep). To do that, you need to create a simple text file in the same directory as the original hypnogram file,  named: *HYPNOFILENAME_description.txt*. A template named ``Hypnogram_description_template.txt`` ships with Visbrain and can be located with ``path_to_visbrain_data(..., folder='example_data')``.

   **This text file should contain the following information :**

   ==========    ======  ======================================================
   Parameters    Values  Description
   ==========    ======  ======================================================
   Time          1       Hypnogram file contains one value per second
   Wake          0       The value assigned to Wake in the hypnogram is 0
   N1            1       The value assigned to N1 sleep in the hypnogram is 1
   N2            2       The value assigned to N2 sleep in the hypnogram is 2
   N3            3       The value assigned to N3 sleep in the hypnogram is 3
   REM           4       The value assigned to REM in the hypnogram is 4
   Artefact      \-1     The value assigned to Artefact in the hypnogram is \-1
   ==========    ======  ======================================================


.. ----------------------------------------------------------------------------
..                              LOAD FILES
.. ----------------------------------------------------------------------------

Load your files
~~~~~~~~~~~~~~~

There are four ways to load datasets into Sleep:

* :ref:`loadfromgui`
* :ref:`loadfrompath`
* :ref:`loadfromraw`
* :ref:`loadfrommne`

.. _loadfromgui:

Load file from the GUI
^^^^^^^^^^^^^^^^^^^^^^

Don't send anything, just open the interface and you will have a popup window asking for the filename of your data and hypnogram. If you do not have a hypnogram for your data and/or wish to display only the data, just press Cancel when the hypnogram popup opens.

.. code-block:: python

    # Import the Sleep module from visbrain :
    from visbrain.gui import Sleep
    # Run the interface :
    Sleep().show()


.. figure::  _static/sleep/sleep_open.png
   :align:   center

   Popup window for loading your files.

.. _loadfrompath:

Load file from path
^^^^^^^^^^^^^^^^^^^

Instead of leaving inputs arguments empty, send the path to the data :

.. code-block:: python

    # Import the Sleep module from visbrain :
    from visbrain.gui import Sleep
    # Define where the data are located :
    dfile = '/home/perso/myfile.eeg'
    # File for the hypogram :
    hfile = '/home/perso/hypno.hyp'
    # If you prefer to start with an empty hypnogram, just pass :
    # hfile = None
    Sleep(data=dfile, hypno=hfile).show()

.. _loadfrommne:

Load file using MNE-Python
^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, it is possible to load several other file formats using `MNE Python package <http://martinos.org/mne/stable/>`_. The code below shows how to load either BDF, EGI or EEGLab files and pass them to :class:`~visbrain.gui.Sleep`.

.. code-block:: python

  # Import the Sleep module:
  from visbrain.gui import Sleep
  # - Biosemi Data Format (BDF)
  data = 'mybdffile.bdf'
  # - EGI format
  # data = 'myegifile.egi'
  # - EEGLab
  # data = 'myeeglabfile.set'
  # Now, pass all the data to the Sleep module :
  Sleep(data=data).show()

.. tip::
   Sleep understands complete BIDS directories.  When calling :class:`~visbrain.gui.Sleep` or
   ``SleepController.load_dataset_async`` you can forward BIDS-specific
   parameters through ``kwargs_mne`` to avoid manually locating files::

       Sleep(
           data='/path/to/bids_root',
           use_mne=True,
           kwargs_mne={
               'bids_entities': {'subject': '01', 'task': 'rest'},
               'bids_resolve': 'first',
           },
       ).show()

   ``bids_path`` accepts either a ``mne_bids.BIDSPath`` instance, a mapping of
   entities or a relative filename.  When multiple runs are available you can
   set ``bids_resolve`` to ``"first"``, ``"last"`` or an index to select the
   desired dataset explicitly.

.. _loadfromraw:

Load file from raw data
^^^^^^^^^^^^^^^^^^^^^^^

It is possible to manually load raw data and pass them as inputs arguments Sleep. The code below show how to extract raw data from a Matlab .mat file (using SciPy):

.. code-block:: python

    from scipy.io import loadmat
    # Import the Sleep module from visbrain:
    from visbrain.gui import Sleep
    # Load your dataset :
    mat = loadmat('testing_database.mat')
    # Get the data, sampling frequency and channel names:
    raw_data, raw_sf, raw_channels = mat['data'], mat['sf'], mat['channels']
    # For the hypnogram :
    raw_hypno = mat['hypno']
    # As before, if you prefer to start from a fresh empty one, use:
    # raw_hypno = None or ignore passing this argument.
    # Now, pass all the arguments to the Sleep module:
    Sleep(data=raw_data, sf=raw_sf, channels=raw_channels,
          hypno=raw_hypno).show()

.. warning::
	Data must be an array with shape (channels, samples). The number of channels must be the same as in *channels* variable. If you load an hypnogram this way, it must have the same number of point (i.e same sampling rate) as the data. If your hypnogram comes with a different time base, the simplest way is to export it into a simple txt file and follow the procedure described above.

.. ----------------------------------------------------------------------------
..                              TIME-FREQUENCY
.. ----------------------------------------------------------------------------

.. _time_frequency:

Time-frequency
~~~~~~~~~~~~~~

There are currently three time-frequency methods implemented in Sleep.

=================   ===================================     ============================================
Name                Method                                  Dependency
=================   ===================================     ============================================
Fourier transform   Fourier-based spectrogram (default)     SciPy
Wavelet             Morlet's wavelet                        None
Multitaper          Multitaper-based Wigner spectrogram     `lspopt <https://github.com/hbldh/lspopt>`_
=================   ===================================     ============================================

.. figure::  _static/sleep/sleep_spectro_methods.png
   :align:   center

   Comparison of the 3 methods on a 50 minutes recording (C3 electrode, 0.5-20 Hz).

.. note::
   In most cases, the multitaper method is the one that gives the best results. To enable it, you must first install the `lspopt <https://github.com/hbldh/lspopt>`_ package.

.. ----------------------------------------------------------------------------
..                              SCORING
.. ----------------------------------------------------------------------------

.. _hypnogram_scoring:

Hypnogram scoring
~~~~~~~~~~~~~~~~~

Sleep offers two possibilities to score the hypnogram: using shortcuts or using the :ref:`scoretable`.

.. _scoretable:

Scoring table
^^^^^^^^^^^^^

The Scoring panel can be used to manually edit the hypnogram values. It contains three columns:

* **From** : specify where the stage start (*in minutes*)
* **To** : specify where the stage finish (*in minutes*)
* **Stage** : the stage type (use Art, Wake, N1, N2, N3 or REM. Can be lowercase)

At the end of the hypnogram, you can **Add line** or **Remove line** when a line is selected. An other interesting option is that the table is sortable (by clicking on the arrow inside the column name).

.. note::
    You can export either the raw hypnogram values, the hypnogram scoring table, or a high-quality figure of the hypnogram using the  *Files > Save* contextual menu.

.. _navigation:

Navigation
^^^^^^^^^^

This is probably the most useful editing method, as it allows scoring while scrolling through your data. 

To insert a sleep stage, use the keys below :

==============          =================
Keys                    Description
==============          =================
a                       Artefact
w                       Wake stage
1                       N1 stage
2                       N2 stage
3                       N3 stage
r                       REM stage
==============          =================

After pressing one of those keys, the software will score accordingly the current "Scoring window", and scroll through to the next epoch so that you can continue scoring.

The software supports two modes of scoring, to allow scoring of both human or animal data:

* **Locked mode** (when :menuselection:`Display --> Lock scoring to display` is
  enabled) keeps the scoring window equal to the display window, so pressing a
  key scores the entire visible epoch. The slider step defaults to the display
  duration, mirroring manual workflows for human datasets.

* **Unlocked mode** (when :menuselection:`Display --> Lock scoring to display`
  is cleared) lets the scoring window move independently from the display
  window, allowing you to label short epochs while retaining surrounding
  context. Vertical bars on the channel plots mark the scoring window and can be
  toggled via the :menuselection:`Display scoring window` action. The
  :menuselection:`Display --> Zoom` tool (or :kbd:`Z`) refines the hypnogram view
  around the scored epoch—handy for animal datasets. In this mode the slider
  step follows the scoring window duration, and adjusting the window size
  automatically disables the locked mode.


.. warning::
   If no canvas are selected the shortcuts might not work. Simply click on a canvas (on a channel / spectrogram / hypnogram) before starting to score to avoid this issue.

.. figure::  _static/sleep/sleep_scoring_locked.png
   :align:   center

   Score the whole displayed epoch.

.. figure::  _static/sleep/sleep_scoring_unlocked.png
   :align:   center

   Score the epoch within the centered "scoring window".

.. figure::  _static/sleep/sleep_scoring_unlocked_zoom.png
   :align:   center

   Use the "Zoom" mode to visualize the hypnogram around the scored epoch.

.. ----------------------------------------------------------------------------
..                              DETECTIONS
.. ----------------------------------------------------------------------------

.. _apply_detection:

Apply semi-automatic detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Detection panel offers several semi-automatic algorithms for the detection of sleep features such as sleep spindles, K-complexes, rapid eyes movements, slow waves, muscle twitches and peaks. All detection types shared the following parameters :

* *Apply on* : choose on which channel to perform the detection

  * Selected : apply detection on selected channel
  * Visible : apply detection on all visible channels
  * All : apply detection on all channels (even those that are hidden)

.. note::
   After performing one of the detection, go to the *Location* tab to see infos about each detected events (starting and ending points, duration, sleep stage). Select the event to jump to it. Finally, you can export the location table using the File > Save contextual menu.

Two examples of automatic event detection are shown below.

Spindles detection
^^^^^^^^^^^^^^^^^^
This algorithm perform a semi-automatic detection of sleep spindles which are an essential feature of N2 sleep. Sleep spindles are defined as bursts of 12-14 Hz waves that occur for at least 0.5 seconds. They are maximally visible on central electrodes.

.. figure::  _static/sleep/sleep_spindles.png
   :align:   center

   Spindles detection on channel Cz.

.. note::

   * **Parameters**
       * *Fmin* : Highpass frequency, default 12 Hz
       * *Fmax* : Lowpass frequency, default 14 Hz
       * *Tmin* : Minimum duration, default 0.5 second
       * *Tmax* : Maximum duration, default 2 seconds
       * *Threshold* : defined as Mean + X * standard deviation of the signal. A  higher threshold will results in a more conservative detection.
       * *Perform detection only for NREM sleep* : if True and a hypnogram is loaded, then the detection will only be performed on NREM sleep epochs.


Peaks detection
^^^^^^^^^^^^^^^

Perform a peak detection.

.. figure::  _static/sleep/sleep_peak.png
   :align:   center

   Peaks detection on ECG channel.

.. note::

   * **Parameters**
       * *Lookahead* : minimum distance between two peaks.
       * *Display* : display either maximum / minimum / maximum & minimum


.. important::
  Please note that the software does not yet allow to automatically score sleep stages. However, if you are interested to collaborate and / or implement your own algorithm, please feel free to contact us.

.. _replace_detection:

Use your own detections in Sleep
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Sleep* offers the possibility to replace the native detection algorithms with your own detection algorithms. To do it, you have to provide a function with predefined inputs and outputs.

Prototype of the function
^^^^^^^^^^^^^^^^^^^^^^^^^

Here's a prototype of a function to replace *Sleep* spindle detections :

.. code-block:: python

  def my_custom_spindle_detection(data, sf, time, hypno):
      """Use your own spindle detection

      Parameters
      ----------
      data : np.ndarray
          Data of one unique channel (i.e shape (n_time_pts,))
      sf : float
           The sampling frequency (512., 1024. etc.)
      time : np.ndarray
          The time vector (i.e shape (n_time_pts,))
      hypno : np.ndarray
          The hypnogram (i.e shape (n_time_pts,))

      Returns
      -------
      indexes : np.ndarray
          indexes of detected events.
      """
      pass

Function output
^^^^^^^^^^^^^^^

For your convenience, *Sleep* accepts several possible output formats for your custom detection :

* **(Start, Stop)** : an array of shape *(n_dected_events, 2)* where *2* describes the index where each event start and finish.
* **Boolean vector** : a boolean vector of shape *(n_time_pts,)* where each *True* value refers to a time point that belong to a detected event.
* **Consecutive indexes** : an array which only contains consecutive indexes of detected events.

It means that your function will work as long as you are able to return any one of these three possible vectors. Since it is very likely that your home-made detection function already return one of those, implementing it in *Sleep* should be fairly easy! A graphical representation of these output formats is displayed below:

.. figure::  _static/sleep/sleep_return_indices.png
   :align:   center

   Supported output format of the custom detection algorithm.

Replace Sleep detection
^^^^^^^^^^^^^^^^^^^^^^^

Once your function has proper inputs and outputs, simply use the :meth:`~visbrain.gui.Sleep.replace_detections` method to replace the detection of *Sleep* with your own. Please visit the Examples section to see some concrete examples.


.. ----------------------------------------------------------------------------
..                              GUI CONFIG
.. ----------------------------------------------------------------------------

Load and save the GUI configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the *Files > Save* contextual menu, you can save the GUI configuration. This will save the state of all buttons and properties inside :class:`~visbrain.gui.Sleep`. Then, you can recharge the GUI configuration using *Files > Load > GUI config*.
Alternatively, if you want to use a configuration when running :class:`~visbrain.gui.Sleep`, you can use the *config_file* argument to directly pass the path to a configuration file. Note that configuration file are encoded in JSON format, which can be easily read and modified using any text editor.

.. code-block:: python

  from mne import io
  # Import the Sleep module:
  from visbrain.gui import Sleep

  Sleep(config_file='pathto/myconfig.json')


.. ----------------------------------------------------------------------------
..                              ANNOTATIONS
.. ----------------------------------------------------------------------------

.. _import_annotation:

Import, add and save annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`~visbrain.gui.Sleep` provides a table for annotations. In this table, specify where the event start, finish and the associated text. Selecting a row of this table center the window around the selected time-code. This allow to quickly navigate even in large files.

.. figure::  _static/sleep/sleep_annotations.png
   :align:   center

   Annotations in Sleep. All annotations are referenced in a table in the quick settings panel (left). Each annotation is then reported in the time axis as a green triangle.

Import annotations
^^^^^^^^^^^^^^^^^^

If the interface is opened, load annotations from the menu *Files > Load > Annotations*. Otherwise, you can use the input variable *annotations* to set the path to an existing annotation file that need to be loaded. There is several ways to define annotations :

* :ref:`annotations_txt`
* :ref:`annotations_mne`
* :ref:`annotations_mark`

.. _annotations_txt:

Annotations in a text file
++++++++++++++++++++++++++

Annotations can be defined in plain-text or comma-separated tables. Minimal
templates (``Sleep_annotations_template.txt`` / ``Sleep_annotations_template.csv``)
are bundled with Visbrain and can be located via
``path_to_visbrain_data(..., folder='example_data')``. The optional
``sleep_rec.zip`` archive, downloadable with ``python -m visbrain.io.download
sleep_rec.zip --type example_data``, contains richer recordings and matching
annotation files.

.. code-block:: python

  from mne import io
  # Import the Sleep module:
  from visbrain.gui import Sleep

  Sleep(annotations='pathto/myannotations.txt')

.. _annotations_mne:

Using MNE-Python annotations
++++++++++++++++++++++++++++

Alternatively, you can use annotations from MNE-python and pass your annotations to the *annotations* variable :

.. code-block:: python

  import numpy as np
  from mne import Annotations
  from visbrain.gui import Sleep

  # Define the onset, duration and description :
  onset = np.array([117., 256., 312.])
  durations = np.array([5, 10, 4])
  description = np.array(['First event', 'Second event', 'Third event'])
  annot = Annotations(onset, durations, description)

  Sleep(annotations=annot)

.. _annotations_mark:

Define only markers
+++++++++++++++++++

Annotations can be seen as the combination of a time-code and a label. If you don't need a label to your event, you can only specify the time-code in seconds:

.. code-block:: python

  import numpy as np
  from visbrain.gui import Sleep

  # Define the onset :
  onset = np.array([117., 256., 312.])

  Sleep(annotations=onset)

Add new annotations
^^^^^^^^^^^^^^^^^^^

To add new annotations :

* From the ruler or from the **Annotations** tab of the quick settings panel, use the **Annotate** button to annotate the currently displayed window
* Double clicking on a canvas is an other way to quickly add annotations.

Save annotations
^^^^^^^^^^^^^^^^

The list of annotations can be exported (either in .txt or .csv) or loaded from the *Files* contextual menu.

Examples
~~~~~~~~

.. include:: generated/visbrain.gui.Sleep.examples.rst
