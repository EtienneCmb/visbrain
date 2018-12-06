.. _Objects:

Objects
=======

.. raw:: html

  <div class="jumbotron">
    <h1 class="display-3">Quick description</h1>
    <p class="lead">Objects are highly customizable elementary visualization bricks that can either be used independently for superpose in a scene.</p>
    <hr class="my-4">
    <p>

Checkout the list and API of available objects :py:mod:`visbrain.objects`.

.. raw:: html

    <img alt="_static/object/ex_combine_obj.png" src="_static/object/ex_combine_obj.png" align="center"></p>
  </div>

.. contents:: Contents
   :local:
   :depth: 2

Description
-----------

Objects have multiple use cases :

* Preview objects independently
* Embedded object inside subplot
* Pass objects to modules (e.g inside the :ref:`BrainModule`)

Import objects
^^^^^^^^^^^^^^

Objects can be imported as follow :

.. code-block:: python

    from visbrain.objects import *

Object definition
^^^^^^^^^^^^^^^^^

All objects have a similar definition i.e `Obj(name)` where name is the object name that you want to use. Note that for some objects, this `name` input can also sometimes be used to load a default file (e.g `BrainObj('B1')` or a specific custom file (e.g `CrossSecObj('full_path/my_nifti_file.nii.qz')`, `HypnogramObj('full_path/my_hypnogram.txt')`).

Once defined, each object contains methods for extended controls and customizations. Checkout the API to see implemented methods relative to each :class:`visbrain.objects`.

Finally, each object inherits a method `preview` to visualize the result. Bellow, a small example where a source object is defined and plotted.

.. code-block:: python

    import numpy as np
    from visbrain.objects import SourceObj  # Import a source object

    # Define 100 random 3D (x, y, z) coordinates :
    xyz = np.random.rand(100, 3)

    # Define a source object :
    s_obj = SourceObj('obj_name', xyz, color='green', symbol='square',
                      edge_color='white')

    # Object preview with a black background:
    s_obj.preview(bgcolor='black')

Embedded objects to create a complex scene
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Similarly to matplotlib, a scene is a way to arrange objects either by superimposing them or by putting them in different rows and columns. Note that only 3D objects can be superimposed.

A scene can be imported from :class:`visbrain.objects` and defined as follow :


.. code-block:: python

    import numpy as np
    from visbrain.objects import BrainObj, SceneObj, SourceObj

    # Define a source and a brain objects :
    b_obj_1 = BrainObj('white', translucent=False)
    b_obj_2 = BrainObj('B1')
    s_obj = SourceObj('my_sources', 50 * np.random.uniform(-1, 1, (100, 3)))

    # Define a scene with a black background:
    sc = SceneObj(bgcolor='black')

    # Add the first brain object to the scene :
    sc.add_to_subplot(b_obj_1, row=0, col=0)

    # Add the source and the first brain object to same subplot :
    sc.add_to_subplot(b_obj_2, row=0, col=1)
    sc.add_to_subplot(s_obj, row=0, col=1)

    # Finally, display the scene :
    sc.preview()


This is a non-exhaustive example. You definitively should take a look at the :class:`visbrain.objects.SceneObj`


Complete object tutorial
------------------------

For each object, we provide a `complete tutorial <http://visbrain.org/auto_examples/index.html#objects-examples>`_ with illustration of all functionalities.
