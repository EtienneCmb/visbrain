import numpy as np

from ...utils import array2colormap


__all__ = ['Projections']


class Projections(object):
    """Set of methods for sources projection.

    This class must be instantiate at the top level of Brain because need
    access to vertices & sources coordinates / data.
    """

    def __init__(self, t_radius=10.0, t_projecton='brain',
                 t_projectas='activity', **kwargs):
        """Init."""
        self._tradius = t_radius
        self._tprojecton = t_projecton
        self._tprojectas = t_projectas
        self._idxmasked = None
        self._modproj = None

    # ======================================================================
    # PROJECTIONS
    # ======================================================================
    def _sourcesProjection(self):
        """Apply corticale projection."""
        # =============== CHECKING ===============
        # Check projection radius :
        if isinstance(self._tradius, (int, float)):
            self._tradius = float(self._tradius)
        else:
            raise ValueError("The radius parameter must be a integer or a "
                             "float number.")

        # Check the projecton parameter :
        if self._tprojecton not in ['brain', 'roi']:
            raise ValueError("The projecton parameter must either be 'brain'"
                             " or 'roi'.")

        # Check projection type :
        if self._tprojectas not in ['activity', 'repartition']:
            raise ValueError("The t_projectas parameter must either be "
                             "'activity' to project source's activity or "
                             "'repartition' to explore the number of "
                             "contributing sources per vertex.")

        # =============== VERTICES ===============
        # Project on brain surface :
        if self._tprojecton == 'brain':
            v = self.atlas.vert
        # Project on deep areas :
        elif self._tprojecton == 'roi':
            v = self.area.mesh.get_vertices
        self._vsh = v.shape

        # ============= MODULATIONS =============
        if self._tprojectas == 'activity':
            mod = self.sources._modulation(v, self._tradius)
        elif self._tprojectas == 'repartition':
            mod = self.sources._repartition(v, self._tradius)
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
        self.atlas.mesh.set_color(data=color)

    def _cleanProj(self):
        """Clean projection variables."""
        self._idxmasked = None
        self._modproj = None

    # ======================================================================
    # DISPLAY
    # ======================================================================
    def s_display(self, select='all'):
        """Choose which part of sources to display.

        Kargs:
            select: string, optional, (def: 'all')
                Sources selection to display. Use 'all' or 'none' to display
                respectively all or none of the sources, 'left' or 'right' for
                sources in the left or right hemisphere or 'inside' / 'outside'
                for sources that are inside or outide the brain.
        """
        # Display either All / None :
        if select in ['all', 'none']:
            if select == 'all':
                self.sources.data.mask = False
            elif select == 'none':
                self.sources.data.mask = True

        # Display sources that are either in the Left / Right hemisphere :
        elif select in ['left', 'right']:
            # Find where x is either >= or =< :
            if select == 'left':
                idx = self.sources.xyz[:, 0] >= 0
            elif select == 'right':
                idx = self.sources.xyz[:, 0] <= 0
            # Update data mask :
            self.sources.data.mask[idx] = True
            self.sources.data.mask[np.invert(idx)] = False

        # Display sources that are either in the inside / outside the brain :
        elif select in ['inside', 'outside']:
            # Get the number of sources :
            N = len(self.sources)
            # Display the progress bar :
            self.progressbar.show()
            # Create an empty mask :
            mask = np.zeros_like(self.sources.data.mask)
            # Loop over sources to find if it's inside :
            for k, i in enumerate(self.sources):
                # Update progress bar :
                self.progressbar.setValue(100*k/N)
                # Find if it's inside :
                mask[k] = self._isInside(self.atlas.vert, i, contribute=False)
            # Set mask according to inside / outside :
            if select == 'inside':
                self.sources.data.mask = np.invert(mask)
            elif select == 'outside':
                self.sources.data.mask = mask
            # Finally, hide the progressbar :
            self.progressbar.hide()

        # Finally update data sources and text :
        self.sources.update()
        self.sources.text_update()

    def _isInside(self, vert, xyz, contribute=False):
        """Find if a source is inside or outside the MNI brain.

        [EXPERIMENTAL].

        Args:
            vert: ndarray
                The vertices.

            xyz: ndarray
                The source's coordinates.

            contribute: bool, optional, (def: False)
                Boolean value to indicate if projected source's activity have
                to be projected on opposite hemisphere.

        Returns:
            isInside: bool
                True if the source is inside, False if it's outside.

        Note:
            For instance, this function is not really working...
        """
        # Get the index of the closest vertex :
        idx = self._closest_vertex(vert, xyz, contribute=contribute)

        # Euclidian distance for the closest vertex :
        x_vert = vert[idx, 0][0]
        y_vert = vert[idx, 1][0]
        z_vert = vert[idx, 2][0]
        eucl_vert = np.sqrt(x_vert**2 + y_vert**2 + z_vert**2)

        # Euclidian distance for each source :
        eucl_xyz = np.sqrt(xyz[0]**2 + xyz[1]**2 + xyz[2]**2)

        # Find where eucl_xyz < eucl_vert :
        isInside = eucl_xyz < eucl_vert

        # Return if it's inside :
        return isInside