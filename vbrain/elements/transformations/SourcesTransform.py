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
        """
        """
        if self.sources.xyz is not None:
            self.progressbar.show()
            # Get data and proportional mask :
            prop, mask = self._get_mask(self.atlas._nv, self.atlas.vert, self.sources.xyz,
                                        self.sources.data, set_to=1, contribute=False)
            # Divide the mask by the number of contributed sources :
            cort_mask = np.divide(mask, prop)
            # Rescale cortical mask data :
            cort_mask, non_zero = self._rescale_cmap(cort_mask, tomin=self.sources.data.min(),
                                                     tomax=self.sources.data.max(), val=0)
            # Finally, set the mask to the surface :
            self._array2cmap(cort_mask, non_zero=non_zero, vmin=self.sources['vmin'], vmax=self.sources['vmax'],
                             under=self.sources['under'], over=self.sources['over'])
            # Save this current cmap (for colormap interaction) :
            self.current_mask = cort_mask
            self.current_non_zero = non_zero
            # Update colorbar :
            self.cb.cbupdate(cort_mask[non_zero], self.sources['cmap'], vmin=self.sources['vmin'], vmax=self.sources['vmax'],
                          under=self.sources['under'], over=self.sources['over'], label=self.cb['cblabel'],
                          fontsize=self.cb['cbfontsize'])
        else:
            warn("No sources detected. Use s_xyz input parameter to define source's coordinates")
        self.progressbar.hide()



    def cortical_repartition(self):
        """
        """
        if self.sources.xyz is not None:
            self.progressbar.show()
            # Get data and proportional mask :
            prop, _ = self._get_mask(self.atlas._nv, self.atlas.vert, self.sources.xyz,
                                     self.sources.data, set_to=0, contribute=False)
            # Finally, set the mask to the surface :
            non_zero = prop != 0
            self._array2cmap(prop, non_zero=non_zero, vmin=0, vmax=prop.max())
            # Save this current cmap (for colormap interaction) :
            self.current_mask = prop
            self.current_non_zero = non_zero
            # Update colorbar :
            self.cb.cbupdate(prop[non_zero], self.sources['cmap'], vmin=self.sources['vmin'], vmax=self.sources['vmax'],
                          under=self.sources['under'], over=self.sources['over'], label=self.cb['cblabel'],
                          fontsize=self.cb['cbfontsize'])
        else:
            warn("No sources detected. Use s_xyz input parameter to define source's coordinates")
        self.progressbar.hide()



    # ________________ SUB VERTICES FUNCTIONS ________________

    def _get_mask(self, nv, vert, xyz, data, set_to=0, contribute=False):
        """Create the colormap mask of data to apply to the MNI brain
        """
        # Define empty proportional and data mask :
        if set_to == 0:
            prop = np.zeros((nv, 3), dtype=int)
        else:
            prop = set_to*np.ones((nv, 3), dtype=int)
        mask = np.zeros((nv, 3), dtype=float)
        idxunmasked = np.where(data.mask == False)[0]
        N = len(idxunmasked)
        # Find unmasked proximal vertices for each source :
        for i, k in enumerate(idxunmasked):
            self.progressbar.setValue(100*k/N)
            # Find index :
            idx = self._proximal_vertices(vert, xyz[k, :], self.radius, contribute=contribute)
            # Update mask :
            # fact = 1-(eucl/self.radius)
            # fact = normalize(fact, tomin=0., tomax=1.)
            mask[idx] += data[k]#*fact
            prop[idx] += 1
        return prop, mask



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


    def _array2cmap(self, x, non_zero=False, vmin=0, vmax=1, under=None, over=None):
        """Convert the array x to cmap and mesh it
        """
        # Get alpha :
        alpha = slider2opacity(self.OpacitySlider.value(), thmin=0.0, thmax=100.0, vmin=self._slmin,
                               vmax=self._slmax, tomin=self.view.minOpacity, tomax=self.view.maxOpacity)

        # Get the colormap :
        cmap = array2colormap(x, cmap=self.sources['cmap'], alpha=alpha, vmin=vmin, vmax=vmax, under=under, over=over)

        # Set ~non_zero to default brain color :
        if non_zero is not False:
            cmap[np.invert(non_zero), 0:3] = self.atlas.mesh.get_color[np.invert(non_zero), 0:3]

        # Update mesh with cmap :
        self.atlas.mesh.set_color(data=cmap)
