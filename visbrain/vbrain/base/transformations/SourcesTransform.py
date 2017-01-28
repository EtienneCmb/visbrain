from warnings import warn
import numpy as np

from ...utils import slider2opacity, array2colormap, normalize

class SourcesTransform(object):

    """docstring for SourcesTransform
    """

    def __init__(self, t_radius=10.0, **kwargs):
        self.radius = t_radius
        self.current_mask = None


    # ***************************************************************
    # ***************************************************************
    # DISPLAY
    # ***************************************************************
    # ***************************************************************
    def s_display(self, select='all'):
        """Choose which elements to display
        """

        # All/None :
        if select in ['all', 'none']:
            if select == 'all': self.sources.data.mask = False
            elif select =='none': self.sources.data.mask = True

        # Left/Right hemisphere :
        elif select in ['left', 'right']:
            # Find where x is either > or < :
            if select == 'left': idx = self.sources.xyz[:, 0] >= 0
            elif select == 'right': idx = self.sources.xyz[:, 0] <= 0
            # Update data mask :
            self.sources.data.mask[idx] = True
            self.sources.data.mask[np.invert(idx)] = False

        elif select in ['inside', 'outside']:
            N = len(self.sources)
            self.progressbar.show()
            if select == 'inside':
                for k, i in enumerate(self.sources):
                    self.progressbar.setValue(100*k/N)
                    self.sources.data.mask[k] = ~self._isInside(self.atlas.vert, i, contribute=False)
            elif select == 'outside':
                for k, i in enumerate(self.sources):
                    self.progressbar.setValue(100*k/N)
                    self.sources.data.mask[k] = self._isInside(self.atlas.vert, i, contribute=False)
            self.progressbar.hide()

        # Finally update data :
        self.sources.update()
        self.sources.text_update()


    # ***************************************************************
    # ***************************************************************
    # PROJECTIONS
    # ***************************************************************
    # ***************************************************************

    # ________________ MAIN FUNCTIONS ________________

    def cortical_projection(self):
        """Project sources activity on the surface
        """
        if self.sources.xyz is not None:
            self.progressbar.show()
            # Switch between surface and deep projection :
            if self.sources.projecton == 'surface':
                nv, vertices = self.atlas._nv, self.atlas.vert
            elif self.sources.projecton == 'deep':
                vertices = self.area.mesh.get_vertices
                nv = vertices.shape[0]
            # Get data and proportional mask :
            prop, mask, smask = self._get_mask(nv, vertices, self.sources.xyz,
                                               self.sources.data, set_to=1, contribute=False)
            # Divide the mask by the number of contributed sources :
            cort_mask = np.divide(mask, prop)
            # Rescale cortical mask data :
            nnmasked = np.invert(self.sources.smask)
            cort_mask, non_zero = self._rescale_cmap(cort_mask, tomin=self.sources.data[nnmasked].min(),
                                                     tomax=self.sources.data[nnmasked].max(), val=0)
            # Save this current cmap (for colormap interaction) :
            self.current_mask = cort_mask
            self.current_non_zero = non_zero
            # Finally, set the mask to the surface :
            self._array2cmap(cort_mask, non_zero=non_zero, smask=smask, smaskcolor=self.sources.smaskcolor)
            # Update colorbar :
            if len(cort_mask[non_zero]):
                self.cb.cbupdate(cort_mask[non_zero], **self.sources._cb, label=self.cb['label'],
                                 fontsize=self.cb['fontsize'])
        else:
            warn("No sources detected. Use s_xyz input parameter to define source's coordinates")
        self.progressbar.hide()



    def cortical_repartition(self):
        """
        """
        if self.sources.xyz is not None:
            self.progressbar.show()
            # Get data and proportional mask :
            prop, _, smask = self._get_mask(self.atlas._nv, self.atlas.vert, self.sources.xyz,
                                            self.sources.data, set_to=0, contribute=False)
            # Finally, set the mask to the surface :
            non_zero = prop != 0
            self.sources['vmin'], self.sources['vmax'] = 0, prop.max()
            self._array2cmap(prop, non_zero=non_zero)
            # Save this current cmap (for colormap interaction) :
            self.current_mask = prop
            self.current_non_zero = non_zero
            # Update colorbar :
            self.cb.cbupdate(prop[non_zero], **self.sources._cb, label=self.cb['label'],
                             fontsize=self.cb['fontsize'])
        else:
            warn("No sources detected. Use s_xyz input parameter to define source's coordinates")
        self.progressbar.hide()



    # ________________ SUB VERTICES FUNCTIONS ________________

    def _get_mask(self, nv, vert, xyz, data, set_to=0, contribute=False):
        """Create the colormap mask of data to apply to the MNI brain
        """
        # Define empty proportional and data mask :
        prop = np.full((nv, 3), set_to, dtype=int)
        smasked = np.zeros(prop.shape, dtype=bool)
        mask = np.zeros((nv, 3), dtype=float)

        # Find unmasked proximal vertices for each source :
        idxunmasked = np.where(data.mask == False)[0]
        N = len(idxunmasked)
        for i, k in enumerate(idxunmasked):
            self.progressbar.setValue(100*k/N)
            # Find index :
            idx = self._proximal_vertices(vert, xyz[k, :], self.radius, contribute=contribute)
            # Add either to prop or to masked array :
            if not self.sources.smask[k]:
                mask[idx] += data[k]
                prop[idx] += 1
            else:
                smasked[idx] = True
        return prop, mask, smasked



    def _proximal_vertices(self, vert, xyz, radius, contribute=False):
        """Find vertices where the distance with xyz is under
        radius. Use contribute to tell if a source can contribute to the
        cortical activity from the other part of the brain.
        Return the index of under radius vertices.
        """
        # Compute manually the euclidian distance (much faster because don't need
        # the reduce function of numpy) :
        x = vert[:, :, 0] - xyz[0]
        y = vert[:, :, 1] - xyz[1]
        z = vert[:, :, 2] - xyz[2]
        eucl = np.sqrt(x**2 + y**2 + z**2)

        # Select under radius sources and those which contribute or not, to the
        # other brain hemisphere :
        if not contribute:
            idx = np.logical_and(eucl <= radius, np.sign(vert[:, :, 0]) == np.sign(xyz[0]))
        else:
            idx = eucl <= radius

        return idx #, eucl[idx]


    def _closest_vertex(self, vert, xyz, contribute=False):
        """Find the unique closest vertex from a source
        """
        # Compute manually the euclidian distance (much faster) :
        x = vert[:, :, 0] - xyz[0]
        y = vert[:, :, 1] - xyz[1]
        z = vert[:, :, 2] - xyz[2]
        eucl = np.sqrt(x**2 + y**2 + z**2)

        # Set if a source can contribute to the other part of the brain :
        if not contribute:
            idx = np.logical_and(eucl == eucl.min(), np.sign(vert[:, :, 0]) == np.sign(xyz[0]))
        else:
            idx = eucl == eucl.min()

        return idx


    def _isInside(self, vert, xyz, contribute=False):
        """Return if a source is inside the MNI brain :
        """
        # Get the index of the closest vertex :
        idx = self._closest_vertex(vert, xyz, contribute=contribute)

        # Compute euclidian distance between 0 and corresponding vertex and source :
        # Euclidian distance for the closest vertex :
        x_vert, y_vert, z_vert = vert[idx, 0][0], vert[idx, 1][0], vert[idx, 2][0]
        eucl_vert = np.sqrt(x_vert**2 + y_vert**2 + z_vert**2)

        # Euclidian distance for each source :
        eucl_xyz = np.sqrt(xyz[0]**2 + xyz[1]**2 + xyz[2]**2)

        # Find where eucl_xyz < eucl_vert :
        isInside = eucl_xyz < eucl_vert

        # Return if it's inside :
        return isInside


    # ________________ PROJECTION COLOR ________________


    def _rescale_cmap(self, cort, tomin=0, tomax=1, val=0):
        """Rescale colormap between tomin and tomax
        """
        # Find non-zero values :
        non_zero = cort != val

        # Rescale colormap :
        cort[non_zero] = normalize(cort[non_zero], tomin=tomin, tomax=tomax)

        return cort, non_zero


    def _array2cmap(self, x, non_zero=False, smask=None, smaskcolor=(.7, .7, .7)):
        """Convert the array x to cmap and mesh it
        """
        # Get alpha :
        alpha = slider2opacity(self.OpacitySlider.value(), thmin=0.0, thmax=100.0, vmin=self._slmin,
                               vmax=self._slmax, tomin=self.view.minOpacity, tomax=self.view.maxOpacity)

        # Get the colormap :
        if len(x[non_zero]):
            cmap = array2colormap(x[non_zero], alpha=alpha, **self.sources._cb)
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

        if self.sources.projecton == 'surface':
            # Apply generale color to the brain :
            cortmask[nnz, 0:3] = self.atlas.mesh.get_color[nnz, 0:3]
            # Update mesh with cmap :
            self.atlas.mesh.set_color(data=cortmask)
        elif self.sources.projecton == 'deep':
            # Apply generale color to the brain :
            cortmask[nnz, 0:3] = self.area.mesh.get_color[nnz, 0:3]
            # Update mesh with cmap :
            self.area.mesh.set_color(data=cortmask)
