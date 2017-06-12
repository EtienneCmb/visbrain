.. -*- mode: rst -*-

|Travis|_ 

.. |Travis| image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
.. _Travis: https://travis-ci.org/EtienneCmb/visbrain

# visbrain


![Visbrain](https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/visbrain.png "Visbrain")


Visbrain is a python package dedicated (mainly) to the visualization of neuroscientist data. Check the [documentation](http://etiennecmb.github.io/visbrain/) for further details

## Installation

To see the installation requirements, check the [documentation](http://etiennecmb.github.io/visbrain/).

## Modules

### Brain

The [Brain](http://etiennecmb.github.io/visbrain/brain.html#) Display a standard MNI brain inside a graphical user interface (using PyQt4 for instance). This module can be used for:

- Display one of the 3 included standard MNI brain or your own template (using vertices and faces)
- Interactions (rotation / translation / transformations / slices)
- Display sources, materialized by small balls (like deep sources or captors...)
	- Add activity to each sources
	- Color each sources as you want (like one color per subject, per area...)
	- Project sources acitivity on the surface
	- Project the cortical repartion of those sources
	- A lot of control on color (use any matplotlib colormaps, specify color threshold and colors for under/over those threshold, mask some sources...)
- Display connectivity link between sources
	- Color connexions either by their strength or by the number of connexions per node
	- Use a dynamic control of transparency to make stronger connexions more visible
	- A lot of other color controls (colormap / limits / threshold...)
- Deep structures (like brodmann areas, AAL...). Source's activity can be projected on deep sources.
- Use either the graphical inteface to interact or use the [user functions](http://etiennecmb.github.io/visbrain/brain.html#user-functions) to run every commands without opening the interface. This tricks can be really usefull to produce a large number of figures.
- Finally, export figures in high-definition.

![Brain](https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/example.png "Brain : visualize your data into a transparent MNI brain")

### Sleep

[Sleep](http://etiennecmb.github.io/visbrain/sleep.html) is a sleep data dedicated interface for visualization, processing and edition.

- Load .eeg (Brainvision and ELAN), .edf, .trc (Micromed) or directly pass raw data
- Visualize channels / spectrogram / hypnogram / topoplot, time window control and fast plot update
- Hypnogram edition (either by manually adding where stages start / finish or interactively by adding / dragging and moving points) and save the edited hypnogram (.txt, .csv and .hyp)
- Spindles / REM / Peaks / Slow waves / K-complex / Muscle twiches detection and report results on each channel and hypnogram
- Signal processing tools (filtering...)

![sleep](https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/Sleep_main.png "Sleep : load, visualize and edit sleep data")

### Ndviz

The [Ndviz](http://etiennecmb.github.io/visbrain/ndviz.html) module help you to visualize multi-dimentional data in a memory efficient way.

- Nd-plot: visualize all of your signals in one grid
- 1d-plot: visualize each signal individually in one of the several forms below
	- As a nice continuous line
	- As a cloud of points
	- As a histogram
	- As an image
	- In the time-frequency domain using the spectrogram

	Each object inherit from a large number of color control or different settings.

![ndviz](https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/ndviz_example.png "Ndviz : data mining")

## Contributors

### Main contributors

- [Etienne Combrisson](http://etiennecmb.github.io)
- [Raphael Vallat](https://raphaelvallat.github.io/)
- [Dmitri Altukchov](https://github.com/dmalt)
- [David Meunier](https://github.com/davidmeunier79)
- [Tarek Lajnef](https://github.com/TarekLaj)
- [Karim Jerbi](www.karimjerbi.com)

### Thx to...
*Christian O'Reilly, Perrine Ruby, JB Einchenlaub, kevroy314, Annalisa Pascarella, Thomas Thiery, Yann Harel, Anne-Lise Saive, Golnush Alamian...*
