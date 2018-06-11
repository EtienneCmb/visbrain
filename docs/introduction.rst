.. _Introduction:

Install Visbrain
================

Dependencies
------------

Here's the list of visbrain's dependencies :

===============================================================               ===========     =========================================
Package                                                                       Version         Purpose
===============================================================               ===========     =========================================
`NumPy <http://www.numpy.org/>`_                                              >= 1.13         Scientific computing
`SciPy <http://www.scipy.org/>`_                                              -               Mathematics, science, and engineering
`Matplotlib <http://www.matplotlib.org/>`_                                    >= 1.5.5        Colors and colormaps integration
`VisPy <http://www.vispy.org/>`_                                              >= 0.5.2        Graphics rendering
`PyQt5 <https://riverbankcomputing.com/software/pyqt/intro>`_                 -               Graphical User Interface components
`Pillow <https://pillow.readthedocs.io>`_                                     -               Screenshots and image file format support
===============================================================               ===========     =========================================

PyQt5 can be installed using either **pip install pyqt5** or **conda install pyqt**. We also strongly recommend to install *pandas* and *pyopengl* :

.. code-block:: shell

    pip install pandas PyOpenGL PyOpenGL_accelerate

Installation
------------

Install Visbrain :

.. code-block:: shell

    pip install visbrain

Develop mode
------------

If you want to install visbrain in develop mode :

.. code-block:: shell

    git clone https://github.com/EtienneCmb/visbrain.git visbrain/
    cd visbrain/
    python setup.py develop 
