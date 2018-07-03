"""The BaseVisual class thath initialize all visual elements."""
import logging

from vispy import scene
import vispy.visuals.transforms as vist

from ..objects import (CombineSources, CombineConnect, CombineTimeSeries,
                       CombinePictures, CombineVectors, BrainObj, VolumeObj,
                       RoiObj, CrossSecObj)
from ..config import PROFILER

logger = logging.getLogger('visbrain')


class Visuals(object):
    """Initialize Brain objects.

    Initialize sources / connectivity / areas / colorbar / projections.
    Organize them at diffrent levels and make the link with the graphical
    user interface (if no object is detected, the corresponding panel in the
    GUI has to be deactivate).
    """

    def __init__(self, canvas, **kwargs):
        """Init."""
        # Create a root node :
        self._vbNode = scene.Node(name='Brain')
        self._vbNode.transform = vist.STTransform(scale=[self._gl_scale] * 3)
        logger.debug("Brain rescaled " + str([self._gl_scale] * 3))
        PROFILER("Root node", level=1)

        # ========================= SOURCES =========================
        self.sources = CombineSources(kwargs.get('source_obj', None))
        if self.sources.name is None:
            self._obj_type_lst.model().item(4).setEnabled(False)
            # Disable menu :
            self.menuDispSources.setChecked(False)
            self.menuTransform.setEnabled(False)
        self.sources.parent = self._vbNode
        PROFILER("Sources object", level=1)

        # ========================= CONNECTIVITY =========================
        self.connect = CombineConnect(kwargs.get('connect_obj', None))
        if self.connect.name is None:
            self._obj_type_lst.model().item(5).setEnabled(False)
            self.menuDispConnect.setEnabled(False)
        self.connect.parent = self._vbNode
        PROFILER("Connect object", level=1)

        # ========================= TIME-SERIES =========================
        self.tseries = CombineTimeSeries(kwargs.get('time_series_obj', None))
        if self.tseries.name is None:
            self._obj_type_lst.model().item(6).setEnabled(False)
        self.tseries.parent = self._vbNode
        PROFILER("Time-series object", level=1)

        # ========================= PICTURES =========================
        self.pic = CombinePictures(kwargs.get('picture_obj', None))
        if self.pic.name is None:
            self._obj_type_lst.model().item(7).setEnabled(False)
        self.pic.parent = self._vbNode
        PROFILER("Pictures object", level=1)

        # ========================= VECTORS =========================
        self.vectors = CombineVectors(kwargs.get('vector_obj', None))
        if self.vectors.name is None:
            self._obj_type_lst.model().item(8).setEnabled(False)
        self.vectors.parent = self._vbNode
        PROFILER("Vectors object", level=1)

        # ========================= VOLUME =========================
        # ----------------- Volume -----------------
        if kwargs.get('vol_obj', None) is None:
            self.volume = VolumeObj('brodmann')
            self.volume.visible_obj = False
        else:
            self.volume = kwargs.get('vol_obj')
        if self.volume.name not in self.volume.list():
            self.volume.save(tmpfile=True)
        self.volume.parent = self._vbNode
        PROFILER("Volume object", level=1)
        # ----------------- ROI -----------------
        if kwargs.get('roi_obj', None) is None:
            self.roi = RoiObj('brodmann')
            self.roi.visible_obj = False
        else:
            self.roi = kwargs.get('roi_obj')
        if self.roi.name not in self.roi.list():
            self.roi.save(tmpfile=True)
        self.roi.parent = self._vbNode
        PROFILER("ROI object", level=1)
        # ----------------- Cross-sections -----------------
        if kwargs.get('cross_sec_obj', None) is None:
            self.cross_sec = CrossSecObj('brodmann')
        else:
            self.cross_sec = kwargs.get('cross_sec_obj')
        if self.cross_sec.name not in self.cross_sec.list():
            self.cross_sec.save(tmpfile=True)
        self.cross_sec.visible_obj = False
        self.cross_sec.text_size = 2.
        self.cross_sec.parent = self._csView.wc.scene
        self._csView.camera = self.cross_sec._get_camera()
        self.cross_sec.set_shortcuts_to_canvas(self._csView)
        PROFILER("Cross-sections object", level=1)

        # ========================= BRAIN =========================
        if kwargs.get('brain_obj', None) is None:
            self.atlas = BrainObj('B1')
        else:
            self.atlas = kwargs['brain_obj']
        if self.atlas.name not in self.atlas.list():
            self.atlas.save(tmpfile=True)
        self.atlas.scale = self._gl_scale
        self.atlas.parent = self._vbNode
        PROFILER("Brain object", level=1)

        # Add XYZ axis (debugging : x=red, y=green, z=blue)
        # scene.visuals.XYZAxis(parent=self._vbNode)
