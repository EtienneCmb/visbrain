"""The BaseVisual class thath initialize all visual elements."""
import logging

from vispy import scene
import vispy.visuals.transforms as vist

from .VolumeBase import VolumeBase
from .projection import Projections
from ...objects import (CombineSources, CombineConnect, CombineTimeSeries,
                        CombinePictures, CombineVectors, BrainObj)

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
        # ---------- Initialize base ----------
        # Main brain object :
        if kwargs.get('brain_obj', None) is None:
            template = kwargs.get('brain_template', 'B1')
            translucent = kwargs.get('brain_translucent', True)
            hemisphere = kwargs.get('brain_hemisphere', 'both')
            self.atlas = BrainObj(template, translucent=translucent,
                                  hemisphere=hemisphere)
        else:
            self.atlas = kwargs['brain_obj']
        self.atlas.scale = self._gl_scale

        # Projection arguments :
        pj = dict(cmap=kwargs.get('project_cmap', 'inferno'),
                  clim=kwargs.get('project_clim', (0., 1.)),
                  vmin=kwargs.get('project_vmin', None),
                  vmax=kwargs.get('project_vmax', None),
                  under=kwargs.get('project_under', 'gray'),
                  over=kwargs.get('project_over', 'red'))

        # Initialize visbrain objects :
        self.volume = VolumeBase(parent_sp=parent_sp)
        self.sources = CombineSources(kwargs.get('source_obj', None), **pj)
        self.connect = CombineConnect(kwargs.get('connect_obj', None))
        self.tseries = CombineTimeSeries(kwargs.get('time_series_obj', None))
        self.pic = CombinePictures(kwargs.get('picture_obj', None))
        self.vectors = CombineVectors(kwargs.get('vector_obj', None))

        # Add projections :
        Projections.__init__(self, **kwargs)
        self._proj_obj['brain'] = self.atlas

        # ---------- Panel management ----------
        # Sources panel:
        if self.sources.name is None:
            self._obj_type_lst.model().item(0).setEnabled(False)
            # Disable menu :
            self.menuDispSources.setChecked(False)
            self.menuTransform.setEnabled(False)

        # Connectivity panel:
        if self.connect.name is None:
            self._obj_type_lst.model().item(1).setEnabled(False)
            self.menuDispConnect.setEnabled(False)

        # Time-series panel :
        if self.tseries.name is None:
            self._obj_type_lst.model().item(2).setEnabled(False)

        # Pictures panel :
        if self.pic.name is None:
            self._obj_type_lst.model().item(3).setEnabled(False)

        # Vectors panel :
        if self.vectors.name is None:
            self._obj_type_lst.model().item(4).setEnabled(False)
        # ---------- Put everything in a root node ----------
        # Here, each object is put in a root node so that each transformation
        # can be applied to all elements.

        # Create a root node :
        self._vbNode = scene.Node(name='*Brain*')
        logger.debug("Brain rescaled " + str([self._gl_scale] * 3))
        self._vbNode.transform = vist.STTransform(scale=[self._gl_scale] * 3)

        # Make this root node the parent of others Brain objects :
        self.volume.parent = self._vbNode
        self.sources.parent = self._vbNode
        self.connect.parent = self._vbNode
        self.tseries.parent = self._vbNode
        self.pic.parent = self._vbNode
        self.vectors.parent = self._vbNode
        self.atlas.parent = self._vbNode

        # Add XYZ axis (debugging : x=red, y=green, z=blue)
        # scene.visuals.XYZAxis(parent=self._vbNode)
