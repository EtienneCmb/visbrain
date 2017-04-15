import numpy as np

from ...utils import array2colormap


__all__ = ['Projections']


class Projections(object):
    """Set of methods for sources projection.

    This class must be instantiate at the top level of Brain because need
    access to vertices & sources coordinates / data.
    """

    def __init__(self, t_radius=10.0, t_projecton='brain', t_contribute=False,
                 t_projectas='activity', t_fitto='brain', **kwargs):
        """Init."""
        self._tobj = {}
        self._tradius = t_radius
        self._tprojecton = t_projecton
        self._tprojectas = t_projectas
        self._tcontribute = t_contribute
        self._tfitto = 'brain'
        self._idxmasked = None
        self._modproj = None

    # ======================================================================
    # PROJECTIONS
    # ======================================================================
    def _findVertices(self, obj):
        """Find the vertices from the object."""
        if obj in self._tobj.keys():
            return self._tobj[obj].mesh.get_vertices
        else:
            raise ValueError(obj + " not found. USe : " +
                             list(self._tobj.keys))

    def _sourcesProjection(self):
        """Apply corticale projection."""
        # =============== CHECKING ===============
        # Check projection radius :
        if isinstance(self._tradius, (int, float)):
            self._tradius = float(self._tradius)
        else:
            raise ValueError("The radius parameter must be a integer or a "
                             "float number.")

        # Check projection type :
        if self._tprojectas not in ['activity', 'repartition']:
            raise ValueError("The t_projectas parameter must either be "
                             "'activity' to project source's activity or "
                             "'repartition' to explore the number of "
                             "contributing sources per vertex.")

        # =============== VERTICES ===============
        v = self._findVertices(self._tprojecton)
        self._vsh = v.shape

        # ============= MODULATIONS =============
        r, c = self._tradius, self._tcontribute
        if self._tprojectas == 'activity':
            mod = self.sources._modulation(v, r, c)
        elif self._tprojectas == 'repartition':
            mod = self.sources._repartition(v, r, c)
        self._modproj = mod
        self.sources._MinMax = (mod.min(), mod.max())

        # ============= MASKED =============
        if self.sources and (self._idxmasked is None):
            self._idxmasked = self.sources._MaskedEucl(v, self._tradius)

        # ============= COLOR =============
        self._proj2Color()

    def _proj2Color(self):
        """Turn the projection into colormap."""
        color = array2colormap(self._modproj, **self.sources._cb)
        color[self._modproj.mask, ...] = 1.

        if self.sources:
            # Set them color to the mask color :
            color[self._idxmasked, ...] = self.sources.smaskcolor

        # ============= MESH =============
        self._tobj[self._tprojecton].mesh.set_color(data=color)

    def _cleanProj(self):
        """Clean projection variables."""
        self._idxmasked = None
        self._modproj = None
