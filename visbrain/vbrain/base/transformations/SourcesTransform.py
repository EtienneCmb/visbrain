"""
"""

from warnings import warn
import numpy as np

from ....utils import slider2opacity, array2colormap, normalize


class SourcesTransform(object):

    """docstring for SourcesTransform.
    """

    def __init__(self, t_radius=10.0, t_projecton='brain', t_smooth=0.,
                 **kwargs):
        """Init."""
        self._tradius = t_radius
        self._tprojecton = t_projecton
        self._tsmooth = t_smooth
        self.current_mask = None
        print('SMOOTH : ', self._tsmooth)

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
            nv, vertices = self.atlas._nv, self.atlas.vert
        # Project on deep areas :
        elif self._tprojecton == 'roi':
            vertices = self.area.mesh.get_vertices
            nv = vertices.shape[0]

        return vertices, nv

    def _cortical_projection(self):
        """Project sources activity.

        This function can be used to project sources activity either on surface
        or on deep sources.
        """
        if self.sources.xyz is not None:
            self.progressbar.show()
            # Get vertices of surface / deep :
            vertices, nv = self._projectOn()
            # Get data and proportional mask :
            prop, mask, smask = self._get_mask(nv, vertices, self.sources.xyz,
                                               self.sources.data, set_to=1,
                                               contribute=False)
            # Divide the mask by the number of contributed sources :
            cort_mask = np.divide(mask, prop)
            # Rescale cortical mask data :
            nnmasked = np.invert(self.sources.smask)
            # Get mi / max of non-masked sources :
            nnmasked_min = self.sources.data[nnmasked].min()
            nnmasked_max = self.sources.data[nnmasked].max()
            # Rescale the colormap :
            cort_mask, non_zero = self._rescale_cmap(cort_mask,
                                                     tomin=nnmasked_min,
                                                     tomax=nnmasked_max, val=0)
            # Save this current cmap (for colormap interaction) :
            self.current_mask = cort_mask
            self.current_non_zero = non_zero
            # Finally, set the mask to the surface :
            self._array2cmap(cort_mask, non_zero=non_zero, smask=smask,
                             smaskcolor=self.sources.smaskcolor)
            # Update colorbar :
            if len(cort_mask[non_zero]):
                self.cb.cbupdate(cort_mask[non_zero], **self.sources._cb,
                                 label=self.cb['label'],
                                 fontsize=self.cb['fontsize'])
        else:
            warn("No sources detected. Use s_xyz input parameter to define "
                 "source's coordinates")
        self.progressbar.hide()

    def _cortical_repartition(self):
        """Get the number of contributing sources per vertex.

        This method evaluate the number of sources that are contrbuting to each
        vertex, either on the surface or on deep sources.
        """
        if self.sources.xyz is not None:
            self.progressbar.show()
            # Get vertices of surface / deep :
            vertices, nv = self._projectOn()
            # Get data and proportional mask :
            prop, _, smask = self._get_mask(nv, vertices, self.sources.xyz,
                                            self.sources.data, set_to=0,
                                            contribute=False)
            # Finally, set the mask to the surface :
            non_zero = prop != 0
            self.sources['vmin'], self.sources['vmax'] = 0, prop.max()
            self._array2cmap(prop, non_zero=non_zero)
            # Save this current cmap (for colormap interaction) :
            self.current_mask = prop
            self.current_non_zero = non_zero
            # Update colorbar :
            self.cb.cbupdate(prop[non_zero], **self.sources._cb,
                             label=self.cb['label'],
                             fontsize=self.cb['fontsize'])
        else:
            warn("No sources detected. Use s_xyz input parameter to define "
                 "source's coordinates")
        self.progressbar.hide()

    # ======================================================================
    # SUB-FONCTIONS
    # ======================================================================
    def _get_mask(self, nv, vert, xyz, data, set_to=0, contribute=False):
        """Create the colormap maskof sources activity.

        Args:
            nv: int
                The number of vertices.

            vert: ndarray
                The vertices.

            xyz: ndarray
                The source's coordinates.

            data: ndarray
                The source's data

        Kargs:
            set_to: int/float, optional, (def: 0)
                Value for setting unused values.

            contribute: bool, optional, (def: False)
                Boolean value to indicate if projected source's activity have
                to be projected on opposite hemisphere.

        Returns:
            prop: ndarray
                Array of integers in order to count the number of contributing
                sources per vertex.

            mask: ndarray
                Array of float containing the sum of all activitiesfor
                contributing sources.

            smasked: ndarray
                Array of bool in order to indicate if this vertex has to be
                masked or not.
        """
        # Define empty proportional and data mask :
        prop = np.full((nv, 3), set_to, dtype=float)
        smasked = np.zeros(prop.shape, dtype=bool)
        mask = np.zeros((nv, 3), dtype=float)

        # Find unmasked proximal vertices for each source :
        idxunmasked = np.where(np.invert(data.mask))[0]
        N = len(idxunmasked)
        for i, k in enumerate(idxunmasked):
            self.progressbar.setValue(100*k/N)
            # Find index :
            idx, eucl = self._proximal_vertices(vert, xyz[k, :], self._tradius,
                                                contribute=contribute)
            # Smoothing :
            # if len(eucl) and (eucl.max() is not 0):
            #     smooth = 1-normalize(np.exp(eucl), 1-self._tsmooth, 1.)
            #     # smooth = 1-np.sin(normalize(eucl**2, 0, np.pi/2))
            # else:
            #     smooth = 1.
            # Add either to prop or to masked array :
            if not self.sources.smask[k]:
                mask[idx] += data[k]   # * smooth
                prop[idx] += 1.
            else:
                smasked[idx] = True
        return prop, mask, smasked

    def _proximal_vertices(self, vert, xyz, radius, contribute=False):
        """Find vertices where the distance with xyz is under radius.

        Arround each source we define a sphere of activity. Then, we look for
        vertices that are contained inside this sphere.

        Args:
            vert: ndarray
                The vertices.

            xyz: ndarray
                The source's coordinates.

            radius: int
                The radius of the sphere.

            contribute: bool, optional, (def: False)
                Boolean value to indicate if projected source's activity have
                to be projected on opposite hemisphere.

        Returns:
            idx: ndarray
                The index of vertices that are contained inside the sphere of
                activity of this source.

            eucl: ndarray
                Euclidian distance between the source and vertices that are
                only under radius.
        """
        # Compute manually the euclidian distance (much faster because don't
        # need the reduce function of numpy) :
        x = vert[:, :, 0] - xyz[0]
        y = vert[:, :, 1] - xyz[1]
        z = vert[:, :, 2] - xyz[2]
        eucl = np.sqrt(x**2 + y**2 + z**2)

        # Select under radius sources and those which contribute or not, to the
        # other brain hemisphere :
        if not contribute:
            idx = np.logical_and(
                eucl <= radius, np.sign(vert[:, :, 0]) == np.sign(xyz[0]))
        else:
            idx = eucl <= radius

        return idx, eucl[idx]

    def _closest_vertex(self, vert, xyz, contribute=False):
        """Find the unique closest vertex from a source.

        This method is used to find if a source is inside or outside of the
        brain [EXPERIMENTAL].

        Args:
            vert: ndarray
                The vertices.

            xyz: ndarray
                The source's coordinates.

            contribute: bool, optional, (def: False)
                Boolean value to indicate if projected source's activity have
                to be projected on opposite hemisphere.

        Returns:
            idx: ndarray
                The index of the closest vertex to this source.
        """
        # Compute manually the euclidian distance (much faster) :
        x = vert[:, :, 0] - xyz[0]
        y = vert[:, :, 1] - xyz[1]
        z = vert[:, :, 2] - xyz[2]
        eucl = np.sqrt(x**2 + y**2 + z**2)

        # Set if a source can contribute to the other part of the brain :
        if not contribute:
            idx = np.logical_and(
                eucl == eucl.min(), np.sign(vert[:, :, 0]) == np.sign(xyz[0]))
        else:
            idx = eucl == eucl.min()

        return idx

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

    # ======================================================================
    # PROJECTION COLOR
    # ======================================================================
    def _rescale_cmap(self, cort, tomin=0., tomax=1., val=0):
        """Rescale colormap between tomin and tomax without touching val.

        Args:
            cort: ndarray
                The cortical mask.

        Kargs:
            tomin: int/float, optional, (def: 0.)
                Minimum value of the returned mask.

            tomax: int/float, optional, (def: 1.)
                Maximum value of the returned mask.

            val: int/float, optional, (def: 0)
                Value that have not to be rescaled.

        Returns:
            cort: ndarray
                The rescaled cortical mask between tomin and tomax.

            non_val: ndarray
                A boolean array where the mask is not val. A true indicate that
                this vertex contains some source's activity. A False means that
                this vertex have to be colored with the defaults brain color.
        """
        # Find non-zero values :
        non_val = cort != val

        # Rescale colormap :
        cort[non_val] = normalize(cort[non_val], tomin=tomin, tomax=tomax)

        return cort, non_val

    def _array2cmap(self, x, non_zero=False, smask=None,
                    smaskcolor=(.7, .7, .7)):
        """Convert the array x into a proper colormap and set it to the mesh.

        Args:
            x: ndarray
                The brut data to convert.

        Kargs:
            non_zero: ndarray, optional, (def: False)
                Boolean array of non-touched brain values.

            smask: ndaray, optional, (def: None)
                Array containing the index of masked vertices.

            smaskcolor: tuple, optional, (def: (.7, .7, .7))
                The color to use for masked sources.
        """
        # Get alpha :
        alpha = slider2opacity(self.OpacitySlider.value(), thmin=0.0,
                               thmax=100.0, vmin=self._slmin, vmax=self._slmax,
                               tomin=self.view.minOpacity,
                               tomax=self.view.maxOpacity)

        # Get the colormap :
        if len(x[non_zero]):
            cmap = array2colormap(x[non_zero], alpha=alpha, **self.sources._cb)
            self.sources._MinMax = (x[non_zero].min(), x[non_zero].max())
        else:
            cmap = np.array([])

        # Define cortical mask :
        cortmask = np.ones((x.shape[0], 3, 4))
        cortmask[..., 3] = alpha

        # Manage masked sources :
        if np.any(smask):
            cortmask[smask, 0:3] = smaskcolor[0, 0:-1]
        if len(x[non_zero]):
            cortmask[non_zero, :] = cmap
        # cortmask = cmap

        # Set ~non_zero to default brain color :
        if np.any(smask):
            nnz = np.logical_and(np.invert(non_zero), np.invert(smask))
        else:
            nnz = np.invert(non_zero)

        if self._tprojecton == 'brain':
            # Apply generale color to the brain :
            cortmask[nnz, 0:3] = self.atlas.mesh.get_color[nnz, 0:3]
            # Update mesh with cmap :
            self.atlas.mesh.set_color(data=cortmask)
        elif self._tprojecton == 'roi':
            # Apply generale color to the brain :
            cortmask[nnz, 0:3] = self.area.mesh.get_color[nnz, 0:3]
            # Update mesh with cmap :
            self.area.mesh.set_color(data=cortmask)
