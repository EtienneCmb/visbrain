.. _Objects:

Objects
=======

* :ref:`BrainObj`
* :ref:`SourceObj`
* :ref:`ConnectObj`
* :ref:`VectorObj`
* :ref:`TSObj`
* :ref:`PicObj`
* :ref:`RoiObj`

.. _BrainObj:

Brain object
------------

.. figure::  picture/picobjects/pic_brain_obj.png
   :align:   center

   Brain object example

.. currentmodule:: visbrain.objects.brain_obj

.. autoclass:: BrainObj
  :template: class.rst

    .. rubric:: Methods

    .. autosummary::
        ~BrainObj.preview
        ~BrainObj.set_data
        ~BrainObj.set_state
        ~BrainObj.rotate
        ~BrainObj.add_activation

.. automethod:: BrainObj.preview
.. automethod:: BrainObj.set_data
.. automethod:: BrainObj.set_state
.. automethod:: BrainObj.rotate
.. automethod:: BrainObj.add_activation

.. _SourceObj:

Source object
-------------

.. figure::  picture/picobjects/pic_source_obj.png
   :align:   center

   Source object example

.. currentmodule:: visbrain.objects.source_obj

.. autoclass:: SourceObj

    .. rubric:: Methods

    .. autosummary::
        ~SourceObj.preview
        ~SourceObj.analyse_sources
        ~SourceObj.color_sources
        ~SourceObj.set_visible_sources
        ~SourceObj.fit_to_vertices
        ~SourceObj.project_modulation
        ~SourceObj.project_repartition

.. automethod:: SourceObj.preview
.. automethod:: SourceObj.analyse_sources
.. automethod:: SourceObj.color_sources
.. automethod:: SourceObj.set_visible_sources
.. automethod:: SourceObj.fit_to_vertices
.. automethod:: SourceObj.project_modulation
.. automethod:: SourceObj.project_repartition

.. _ConnectObj:

Connectivity object
-------------------

.. figure::  picture/picobjects/pic_connect_obj.png
   :align:   center

   Connectivity object example

.. currentmodule:: visbrain.objects.connect_obj

.. autoclass:: ConnectObj

    .. rubric:: Methods

    .. autosummary::
        ~ConnectObj.preview

.. automethod:: ConnectObj.preview

.. _VectorObj:

Vector object
-------------

.. figure::  picture/picobjects/pic_vector_obj.png
   :align:   center

   Vector object example

.. currentmodule:: visbrain.objects.vector_obj

.. autoclass:: VectorObj

    .. rubric:: Methods

    .. autosummary::
        ~VectorObj.preview

.. automethod:: VectorObj.preview

.. _TSObj:

Time-series object
------------------

.. figure::  picture/picobjects/pic_ts_obj.png
   :align:   center

   3-D time-series object example

.. currentmodule:: visbrain.objects.ts_obj

.. autoclass:: TimeSeriesObj

    .. rubric:: Methods

    .. autosummary::
        ~TimeSeriesObj.preview

.. automethod:: TimeSeriesObj.preview

.. _PicObj:

Pictures object
---------------

.. figure::  picture/picobjects/pic_picture_obj.png
   :align:   center

   3-D pictures object example

.. currentmodule:: visbrain.objects.picture_obj

.. autoclass:: PictureObj

    .. rubric:: Methods

    .. autosummary::
        ~PictureObj.preview

.. automethod:: PictureObj.preview

.. _RoiObj:

Region Of Interest object
-------------------------

.. figure::  picture/picobjects/pic_roi_obj.png
   :align:   center

   Region Of Interest object example

.. currentmodule:: visbrain.objects.roi_obj

.. autoclass:: RoiObj

    .. rubric:: Methods

    .. autosummary::
        ~RoiObj.preview
        ~RoiObj.change_roi_object
        ~RoiObj.localize_sources
        ~RoiObj.get_roi_vertices

.. automethod:: RoiObj.preview
.. automethod:: RoiObj.change_roi_object
.. automethod:: RoiObj.localize_sources
.. automethod:: RoiObj.get_roi_vertices