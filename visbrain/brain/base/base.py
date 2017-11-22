"""The BaseVisual class thath initialize all visual elements."""
import logging

from vispy import scene
import vispy.visuals.transforms as vist

from .VolumeBase import VolumeBase
from .projection import Projections
from ...objects import (CombineSources, CombineConnect, CombineTimeSeries,
                        CombinePictures, CombineVectors, BrainObj)
from ...config import PROFILER

logger = logging.getLogger('visbrain')


class BaseVisual(Projections):
    """Initialize Brain objects.

    Initialize sources / connectivity / areas / colorbar / projections.
    Organize them at diffrent levels and make the link with the graphical
    user interface (if no object is detected, the corresponding panel in the
    GUI has to be deactivate).
    """

    def __init__(self, canvas, parent_sp, **kwargs):
        """Init."""
        # Projection arguments :
        pj = dict(cmap=kwargs.get('project_cmap', 'inferno'),
                  clim=kwargs.get('project_clim', (0., 1.)),
                  vmin=kwargs.get('project_vmin', None),
                  vmax=kwargs.get('project_vmax', None),
                  under=kwargs.get('project_under', 'gray'),
                  over=kwargs.get('project_over', 'red'))

        # Create a root node :
        self._vbNode = scene.Node(name='Brain')
        self._vbNode.transform = vist.STTransform(scale=[self._gl_scale] * 3)
        logger.debug("Brain rescaled " + str([self._gl_scale] * 3))
        PROFILER("Root node", level=1)

        # ========================= SOURCES =========================
        self.sources = CombineSources(kwargs.get('source_obj', None), **pj)
        if self.sources.name is None:
            self._obj_type_lst.model().item(0).setEnabled(False)
            # Disable menu :
            self.menuDispSources.setChecked(False)
            self.menuTransform.setEnabled(False)
        self.sources.parent = self._vbNode
        PROFILER("Sources object", level=1)

        # ========================= CONNECTIVITY =========================
        self.connect = CombineConnect(kwargs.get('connect_obj', None))
        if self.connect.name is None:
            self._obj_type_lst.model().item(1).setEnabled(False)
            self.menuDispConnect.setEnabled(False)
        self.connect.parent = self._vbNode
        PROFILER("Connect object", level=1)

        # ========================= TIME-SERIES =========================
        self.tseries = CombineTimeSeries(kwargs.get('time_series_obj', None))
        if self.tseries.name is None:
            self._obj_type_lst.model().item(2).setEnabled(False)
        self.tseries.parent = self._vbNode
        PROFILER("Time-series object", level=1)

        # ========================= PICTURES =========================
        self.pic = CombinePictures(kwargs.get('picture_obj', None))
        if self.pic.name is None:
            self._obj_type_lst.model().item(3).setEnabled(False)
        self.pic.parent = self._vbNode
        PROFILER("Pictures object", level=1)

        # ========================= VECTORS =========================
        self.vectors = CombineVectors(kwargs.get('vector_obj', None))
        if self.vectors.name is None:
            self._obj_type_lst.model().item(4).setEnabled(False)
        self.vectors.parent = self._vbNode
        PROFILER("Vectors object", level=1)

        # ========================= VOLUME =========================
        self.volume = VolumeBase(parent_sp=parent_sp)
        self.volume.parent = self._vbNode
        PROFILER("Volume object", level=1)

        # ========================= BRAIN =========================
        if kwargs.get('brain_obj', None) is None:
            template = kwargs.get('brain_template', 'B1')
            translucent = kwargs.get('brain_translucent', True)
            hemisphere = kwargs.get('brain_hemisphere', 'both')
            self.atlas = BrainObj(template, translucent=translucent,
                                  hemisphere=hemisphere)
        else:
            self.atlas = kwargs['brain_obj']
        self.atlas.scale = self._gl_scale
        self.atlas.parent = self._vbNode
        PROFILER("Brain object", level=1)

        # Add projections :
        Projections.__init__(self, **kwargs)
        self._proj_obj['brain'] = self.atlas
        PROFILER("Initialize projection", level=1)

        # Add XYZ axis (debugging : x=red, y=green, z=blue)
        # scene.visuals.XYZAxis(parent=self._vbNode)
