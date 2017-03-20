.. _Sleep:

Sleep
=====

Description
-----------

.. figure::  picture/Sleep_full.png
   :align:   center

   The Sleep module: individual control of each channel.

Sleep is a graphical user interface dedicated to visualization and scoring of sleep data. Sleep runs on Vispy excellent package and benefits thus from the high-performance of this latter (GPU-based computation). Some of the most relevant features of Sleep include:

* Dynamic display of polysomnographic data, spectrogram and hypnogram, with individual real-time adjustment of channel amplitude and visibility. 
* Spectrogram display with several controllable parameters (e.g. frequency, channel, colormap)
* Hypnogram editing and saving functions, as well as real-time computation of the main sleep parameters (see Hypnogram section). 
* Implementation of several semi-automatic detection method such as sleep spindles, rapid eye movements or peak detection. These can be performed either on single or multiple channels and report where each one of them on the hypnogram or inside a table. Each detection comes with several parameters that the user * can adjust to find the optimal detection. 
* Several others signal processing tools such as de-mean, de-trend and filtering. Those tools are directly applied to each channel and to the spectrogram
* Nice and intuitive interface to help you scroll and explore your data.


The Sleep module can be imported as follow :

.. code-block:: python

    from visbrain import Sleep

.. figure::  picture/Sleep_full2.png
   :align:   center

   Bandpass filtering example.

Supported files and format
--------------------------

Sleep support by default several data format for both electrophysiological and hypnogram data.

Data files
~~~~~~~~~~

Here’s the list of currently supported extensions for data files:

* BrainVision (**.eeg**)
* ELAN – (lien: http://elan.lyon.inserm.fr) (**.eeg**)
* European Data Format (**.edf**)

.. note::
   Extensions above are files that are natively supported inside Sleep. But, tha data can be directly pass to the Sleep module if you load them before.

.. warning::
   Sleep applies an automatic downsampling to 100 Hz upon loading. You can change this value with the “downsample” argument of Sleep (command-line only). 

Hypnogram
~~~~~~~~~

Here's the list of supported extensions for hypnogram files : 

* **.hyp** (ELAN)
* **.txt**
* **.csv**

.. warning::
   There is no international gold standard for the hypnogram format yet and each lab can have its own format. To overcome problems caused by different sampling rate of hypnogram files and/or different values assigned to each sleep stages, Sleep requires that you specify these parameters in a .txt file. This text file should be in the same directory as the original hypnogram file and be named: *HYPNOFILENAME_description.txt*. Checkout this `example <https://github.com/EtienneCmb/visbrain/tree/master/docs/Hypnogram_excerpt2_description.txt>`_.

   **This text file should contain the following information :**

   * *Time* : the number of seconds represented by one value of the hypnogram (e.g. one value per 30 second, time = 30, one value per second, time = 1). 
   * *W, N1, N2, N3, REM, Art* : The value in your hypnogram that corresponds to stage Wakefulness, N1, N2, N3, REM and Art.
   
   Please note that Sleep uses the guidelines of *Iber et al. 2007* for sleep stage nomenclature, i.e. Wake, N1, N2, N3, REM and Artefact. If your hypnogram includes both NREM-S3 and NREM-S4 sleep stages you can add “N4” categories with the corresponding values in the description file. However, keep in mind that N3 and N4 will be merged into N3 during the import to the Sleep module.


Save hypnogram
~~~~~~~~~~~~~~

By default, Sleep will save your hypnogram with a sampling rate of 1 value per second, and with the following values assigned to each sleep stages:

* **Wake** :   0
* **N1** :     1
* **N2** :     2
* **N3** :     3
* **REM** :    4
* **Art** :    -1  (*optional*)

Elan .hyp format
^^^^^^^^^^^^^^^^

Sleep will create a single .hyp file with 4 header rows and the values presented above for the sleep stages.

.txt / .csv format
^^^^^^^^^^^^^^^^^^

Sleep will automatically create a HYPNOFILENAME_description.txt with the appropriate parameters (time, sleep stages values), therefore making it easy to reload it later.

Load your files
---------------

There is three way for loading your files :

- **Load from the GUI**:
- **Load from path**:
- **Load raw data**:

From the GUI
~~~~~~~~~~~~

Don't send anything, just open the interface and you will have a popup window asking for the filename of your data and hypnogram

.. code-block:: python

    # Import the Sleep module from visbrain :
    from visbrain import Sleep
    # Run the interface :
    Sleep().show()


.. figure::  picture/Sleep_open.png
   :align:   center

   Popup window for loading your files.

From path
~~~~~~~~~

Instead of leaving inputs arguments empty, send the path to the data :

.. code-block:: python

    # Import the Sleep module from visbrain :
    from visbrain import Sleep
    # Define where the data are located :
    dfile = '/home/perso/myfile.eeg'
    # File for the hypogram :
    hfile = '/home/perso/hypno.hyp'
    # You're not forced to give a hypnogram. If you prefer to start from a fresh empty one, use :
    # hfile = None or ignore passing this argument.
    Sleep(file=dfile, hypno_file=hfile).show()

Raw data
~~~~~~~~

This third way is the manually one. You have to load your data before and sending it to the sleep module. This may seems to be more difficult but it allow advanced user to pass any kind of data :

.. code-block:: python

    # Import the Sleep module from visbrain :
    from visbrain import Sleep
    # Load your dataset :
    mat = loadmat('testing_database.mat')
    # Get the data, sampling frequency and channel names :
    raw_data = mat['data']
    raw_sf = mat['sf']
    raw_channels = mat['channels']
    # For the hypnogram :
    raw_hypno = mat['hypno']
    # As before, if you prefer to start from a fresh empty one, use :
    # raw_hypno = None or ignore passing this argument.
    # Now, pass all the arguments to the Sleep module :
    Sleep(data=raw_data, sf=raw_sf, channels=raw_channels,
          hypno=raw_hypno).show()

.. warning::

   The data must have the same number of points as the hypnogram and the same number of channels in the *channels* variable.

Tabs descripion
---------------

Sleep provide five settings tabs :

* **Panels** : manage object visibility, channel's amplitudes, spectrogram properties...
* **Tools** : a bundle of signal processing tools (like *filtering*)
* **Infos** : some usefull informations about the hypnogram
* **Scoring** : a scoring table that can be used to edit the hypnogram
* **Detection** : run the spindles / REM / peak detection

Panels
~~~~~~

Hypnogram scoring
-----------------

Sleep offer the possibility to score the hypnogram, either manually using the :ref:`scoretab` or :ref:`liveedit`. Both methods are always kept synchronized.

.. figure::  picture/Sleep_edit.png
   :align:   center

   Hypnogram scoring.

.. _scoretab:

Scoring table
~~~~~~~~~~~~~

The Scoring panel can be used to manually edit the hypnogram values. It contains three columns : 

* **From** : specify where the stage start (*in minutes*)
* **To** : specify where the stage finish (*in minutes*)
* **Stage** : the stage type (use Art, Wake, N1, N2, N3 or REM. Can be lowercase)

At the end of the hypnogram, you can **Add line** or **Remove line** when a line is selected. An other interesting option is that the table is sortable (by clicking on the arrow inside the column name).

Then, you can export your hypnogram in **.hyp**, **.txt** or **cvs**.

.. figure::  picture/Scoring_table.png
   :align:   center

   Hypnogram scoring using the Scoring table. Manually specify where each stage start / finish and precise the stage type.

.. _liveedit:

Live editing
~~~~~~~~~~~~

Live editing consist of editing your hypnogram directly from the axis by adding / selecting / dragging points. Unused points will be automatically destroyed. 

	- Your cursor is red. Existing points are set in gray.
	- Double click on the hypnogram to add points
	- Hover an existing point in order to select it (the point turn green)
	- Dragg the point (blue) on the diffrent hypnogram values

.. figure::  picture/Sleep_livedit.png
   :align:   center

   Edit the hypnogram directly from the axes.

Spindles / REM / Peak detection
-------------------------------

.. figure::  picture/Sleep_detect.png
   :align:   center

   REM / Spindle and peak detection.

Additional inputs
-----------------

.. autoclass:: visbrain.sleep.sleep.Sleep


Shortcuts
---------

==============          ==================================================================================
Keys                    Description
==============          ==================================================================================
CTRL+d                  Display quick settings panel
CTRL+n                  Screenshot window
0                       Display / hide spectrogram
1                       Display / hide hypnogram
z                       Enable / disable zoom
b                       Previous window
n                       Next window
mouse wheel             Move the current window
==============          ==================================================================================