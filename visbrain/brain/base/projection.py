import numpy as np

from ...utils import array2colormap, normalize
from scipy.spatial.distance import cdist

__all__ = ['Projections']


class Projections(object):
    """Set of methods for sources projection.

    This class must be instantiate at the top level of Brain because need
    access to vertices & sources coordinates / data.
    """

    def __init__(self, t_radius=10.0, t_projecton='brain', **kwargs):
        """Init."""
        print('IM IN')
        self._tradius = t_radius
        self._tprojecton = t_projecton
        self.current_mask = None

    # ======================================================================
    # PROJECTIONS
    # ======================================================================
    def _projectOn(self):
        """Get the vertices to project sources activity or repartition."""
        # Check the projecton parameter :
        if self._tprojecton not in ['brain', 'roi']:
            raise ValueError("The projecton parameter must either be 'brain'"
                             " or 'roi'.")
        # Project on brain surface :
        if self._tprojecton == 'brain':
            vertices = self.atlas.vert
        # Project on deep areas :
        elif self._tprojecton == 'roi':
            vertices = self.area.mesh.get_vertices
        # Sources data :
        xyz = self.sources.xyz
        data = self.sources.data.data.astype(np.float32)

        return vertices, self._tradius, xyz, data

    def _cortProj(self):
        """Apply corticale projection."""
        from time import time
        st = time()
        # ============= VARIABLES =============
        # Get vertices, radius, locations and data :
        v, r, xyz, data = self._projectOn()

        # ============= MODULATIONS =============

        print('DATA : ', data.min(), data.max())
        mod = self.__modulation(v, xyz, data)
        # mod = self.__repartition(v, xyz, data)
        print(mod.min(), mod.max())

        color = array2colormap(mod, cmap='Spectral_r', clim=(-1., 1.))
        color[mod.mask, ...] = 1.
        self.atlas.mesh.set_color(data=color)
        print('END TIME : ', st-time())

    def _cortRepart(self):
        """Apply corticale repartition."""
        pass

    def __modulation(self, v, xyz, data):
        """Get data modulated by the euclidian distance.

        The vertices are indexed by face which means it's a (N, 3, 3).
        Depending on the number of sources, using broadcasting rules can
        be memory consuming. For that reason, we split computation for each
        face, using an ugly loop.

        Args:
            v: np.ndarray, float32
                The index faced vertices of shape (nv, 3, 3)

            xyz: np.ndarray, float32
                Sources locations of shape (N, 3)

            data: np.ndarray, float32
                Data per source of shape (N,)

        Return:
            modulation: masked np.ndarray, float32
                The index faced modulations of shape (N, 3). This is a masked
                array where the mask refer to sources that are over the radius.
        """
        # =============== PRE-ALLOCATION ===============
        modulation = np.ma.zeros((v.shape[0], v.shape[1]), dtype=np.float32)
        prop = np.zeros_like(modulation.data)
        minmax = np.zeros((3, 2), dtype=np.float32)

        # For each triangle :
        for k in range(3):
            # =============== EUCLIDIAN DISTANCE ===============
            # Compute euclidian distance and get sources under radius :
            eucl = cdist(v[:, k, :], xyz).astype(np.float32)
            mask = eucl <= self._tradius
            # Invert euclidian distance for modulation and mask it :
            np.multiply(eucl, -1. / eucl.max(), out=eucl)
            np.add(eucl, 1., out=eucl)
            eucl = np.ma.masked_array(eucl, mask=np.invert(mask),
                                      dtype=np.float32)

            # =============== MODULATION ===============
            # Modulate data by distance (only for sources under radius) :
            modulation[:, k] = np.ma.dot(eucl, data, strict=False)

            # =============== PROPORTIONS ===============
            np.sum(mask, axis=1, dtype=np.float32, out=prop[:, k])
            nnz = np.nonzero(mask.sum(0))
            minmax[k, :] = np.array([data[nnz].min(), data[nnz].max()])

        # Divide modulations by the number of contributing sources :
        prop[prop == 0.] = 1.
        np.divide(modulation, prop, out=modulation)
        # Normalize inplace modulations between under radius data :
        normalize(modulation, minmax.min(), minmax.max())

        return modulation

    def __repartition(self, v, xyz, data):
        """Get data repartition.

        The vertices are indexed by face which means it's a (N, 3, 3).
        Depending on the number of sources, using broadcasting rules can
        be memory consuming. For that reason, we split computation for each
        face, using an ugly loop.

        Args:
            v: np.ndarray, float32
                The index faced vertices of shape (nv, 3, 3)

            xyz: np.ndarray, float32
                Sources locations of shape (N, 3)

            data: np.ndarray, float32
                Data per source of shape (N,)

        Return:
            repartition: masked np.ndarray, float32
                The index faced repartition of shape (N, 3). This is a masked
                array where the mask refer to sources that are over the radius.
        """
        # =============== PRE-ALLOCATION ===============
        repartition = np.ma.zeros((v.shape[0], v.shape[1]), dtype=np.int)

        # For each triangle :
        for k in range(3):
            # =============== EUCLIDIAN DISTANCE ===============
            eucl = cdist(v[:, k, :], xyz).astype(np.float32)
            mask = eucl <= self._tradius

            # =============== REPARTITION ===============
            # Sum over sources dimension :
            sm = np.sum(mask, 1, dtype=np.int)
            smmask = np.invert(sm.astype(bool))
            repartition[:, k] = np.ma.masked_array(sm, mask=smmask)

        return repartition

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