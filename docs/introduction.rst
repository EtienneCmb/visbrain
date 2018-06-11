.. _Introduction:

Presentation
============

Quick description
-----------------

Visbrain is an open-source `Python 3 <https://www.python.org/>`_ package, distributed under the 3-Clause BSD license and is dedicated to brain signals visualization.

Visbrain is under heavy development and many functionalities are frequently added to the package, such as bug fixing, documentation improvements etc.

Visbrain use VisPy to render graphics. Taken from their website :

.. raw:: html

    <blockquote class="blockquote">
      <p class="mb-0">VisPy is a high-performance interactive 2D/3D data visualization library leveraging the computational power of modern Graphics Processing Units (GPUs) through the OpenGL library to display very large datasets.</p>
      <footer class="blockquote-footer">VisPy website : <a href="http://vispy.org">http://vispy.org</a></footer>
    </blockquote>



Structure
---------

Installation
============

Dependencies
------------

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

Regular installation
--------------------

Run the following command in a terminal :

.. code-block:: shell

    pip install visbrain

Develop mode
------------

If you want to install visbrain in develop mode :

.. code-block:: shell

    git clone https://github.com/EtienneCmb/visbrain.git visbrain/
    cd visbrain/
    python setup.py develop 
