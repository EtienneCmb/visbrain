"""Main class for managing sub-structures (ROI).

Areas are sub-divided parts of the brain. The present file display those areas
using either Automated Anatomical Labeling (AAL) or Brodmann area labeling.
"""

import numpy as np
from scipy.signal import fftconvolve

import warnings

from vispy.geometry.isosurface import isosurface

from ...visuals import BrainMesh
from ...utils import array2colormap, color2vb, color2faces

# warnings.filterwarnings('ignore', r'with ndim')
__all__ = ['RoiBase']


class RoiBase(object):
    """Main class for managing sub-division brain areas.

    This class contains several method for managing areas (loading, color,
    ploting...)
    """

    def __init__(self, select=None, color='white', cmap=None, name='',
                 smooth=3, parent=None):
        """Init."""
        self._select_roi = select
        self._selectAll = True
        self._unicolor = True
        self._color_roi = color
        self.cmap = cmap
        self.name_roi = name
        self._smooth_roi = smooth
        self._parent = parent

    def __str__(self):
        """Return labels of selected ROI type."""
        return '\n'.join(self.roi_labels)

    def __len__(self):
        """Return the number of ROI's."""
        return len(self.roi_labels)

    # ========================================================================
    # PROCESSING FUNCTIONS
    # ========================================================================
    def _preprocess(self):
        """Pre-processing function.

        This method can be used to manage area selection (select some areas,
        all of them...). Then, pre-process color (unique color, colormap...).
        Finally, find the index of the selected areas and corresponding labels.
        """
        # ====================== Manage area selection ======================
        # Select is None -> Select all areas :
        if self._select_roi is None:
            self._select_roi = self.roi_values
            self._selectAll = True
        # Select is a list of integers :
        elif not isinstance(self._select_roi, list):
            self._select_roi = list(self._select_roi)
            self._selectAll = False
        else:
            self._selectAll = False
        # Check if every selected element is present in the possibilities :
        for k in self._select_roi:
            if k not in self.roi_values:
                raise ValueError(str(k) + ' not in :', self.roi_values)

        # ====================== Manage color ======================
        # Use a list of colors (uniform color) :
        if not isinstance(self._color_roi, list):
            self._color_roi = list([self._color_roi])
            self._unicolor = True
        # Non-uniform color :
        else:
            self._unicolor = False
        # Check if the length of color is the same as the number of selected
        # areas. Otherwise, use only the first color in the list :
        if len(self._color_roi) != len(self._select_roi):
            self._color_roi = [self._color_roi[0]] * len(self._select_roi)
            self._unicolor = True
        else:
            self._unicolor = False
        # Use a colormap for the area color :
        if self.cmap is not None:
            # Generate an array of colors using a linearly spaced vector :
            self._color_roi = array2colormap(np.arange(len(self._select_roi)),
                                             cmap=self.cmap)
            # Turn it into a list :
            self._color_roi = list(self._color_roi)
            self._unicolor = False
            self._selectAll = False

        # ====================== Manage index ======================
        # Find selected areas in the unique list :
        self._selectedIndex = [np.argwhere(self.roi_values == k)[0][
            0] for k in self._select_roi]
        # Select labels :
        self._selectedLabels = self.roi_labels[self._selectedIndex]
        # Transform each color into a RGBA format :
        self._color_roi = [color2vb(k) for k in self._color_roi]
        # Initialize variables :
        self._color_idx, self.vertex_colors = np.array([]), np.array([])

    def _get_vertices(self):
        """Get vertices and faces of selected areas and pre-allocate color.

        Description
        """
        # --------------------------------------------------------------------
        # The volume array (self.vol) is composed with integers where each
        # integer encode for a specific area.
        # The isosurface turn a 3D array into a surface mesh compatible.
        # Futhermore, this function use a level parameter in order to get
        # vertices and faces of specific index. Unfortunately, the level can
        # only be >=, it's not possible to only select some specific levels.
        # --------------------------------------------------------------------
        # ============ Unicolor ============
        if self._unicolor:
            if not self._selectAll:
                # Create an empty volume :
                vol = np.zeros_like(self.vol)
                # Build the condition list :
                cd_lst = ['(self.vol==' + str(k) + ')' for k
                          in self._select_roi]
                # Set vol to 1 for selected index :
                vol[eval(' | '.join(cd_lst))] = 1
            else:
                vol = self.vol
            # Extract the vertices / faces of non-zero values :
            self.vert, self.faces = isosurface(self._smooth(vol), level=.5)
            # Turn the unique color tuple into a faces compatible ndarray:
            self.vertex_colors = color2faces(self._color_roi[0],
                                             self.faces.shape[0])
            # Unique color per ROI :
            self._color_idx = np.zeros((self.faces.shape[0],))

        # ============ Specific selection + specific colors ============
        # This is where problems begin. In this part, there's a specific area
        # selection with each one of them having a specific color. The program
        # below loop over areas, make a copy of the volume, turn all
        # non-desired area index to 0, transform into an isosurface and finally
        # concatenate vertices / faces / color. This is is very slow and it's
        # only because of the color.
        else:
            self.vert, self.faces = np.array([]), np.array([])
            q = 0
            for num, k in enumerate(self._select_roi):
                # Remove unecessary index :
                vol = np.zeros_like(self.vol)
                vol[self.vol == k] = 1
                # Get vertices/faces for this structure :
                vertT, facesT = isosurface(self._smooth(vol), level=.5)
                # Update faces index :
                facesT += (q + 1)
                # Concatenate vertices/faces :
                self.vert = np.concatenate(
                    (self.vert, vertT)) if self.vert.size else vertT
                self.faces = np.concatenate(
                    (self.faces, facesT)) if self.faces.size else facesT
                # Update colors and index :
                idxt = np.full((facesT.shape[0],), k, dtype=np.int64)
                self._color_idx = np.concatenate(
                    (self._color_idx, idxt)) if self._color_idx.size else idxt
                color = color2faces(self._color_roi[num], facesT.shape[0])
                self.vertex_colors = np.concatenate(
                    (self.vertex_colors,
                     color)) if self.vertex_colors.size else color
                # Update maximum :
                q = self.faces.max()

    def _smooth(self, data):
        """Volume smoothing.

        Parameters
        ----------
        data : array_like
            Data volume (M, N, P)

        Returns
        -------
        data_sm : array_like
            The smoothed data with the same shape as the data (M, N, P)
        """
        if self._smooth_roi >= 3:
            # Define smooth arguments :
            sz = np.full((3,), self._smooth_roi, dtype=int)
            smooth = np.ones([self._smooth_roi] * 3) / np.prod(sz)
            return fftconvolve(data, smooth, mode='same')
        else:
            return data

    def _plot(self):
        """Plot deep areas.

        This method use the BrainMesh class, which is the same as the class
        used for plotting the main MNI brain.
        """
        if not hasattr(self, 'mesh'):
            self.mesh = BrainMesh(vertices=self.vert, faces=self.faces,
                                  scale_factor=1., name=self.name_roi,
                                  recenter=False, parent=self._parent,
                                  vertfcn=self.transform)
            self.name_roi = 'ROI'
        else:
            self.mesh.set_data(vertices=self.vert, faces=self.faces)
        self.mesh.set_color(self.vertex_colors)

    def _get_idx_mask(self, index):
        """Get a boolean array where each structure is located.

        For a list of index, this function return where those index are
        located.

        Parameters
        ----------
        index : list
            List of index. Each index must be an integer. If this parameter
            is None, the entire list is returned.

        Returns
        -------
        mask : array_like
            An array of boolean values.
        """
        # Get list of unique index :
        uindex = np.unique(self._color_idx)
        # Create an empty mask :
        mask = np.zeros((len(self._color_idx),), dtype=bool)
        # Convert index :
        if index is None:
            index = list(uindex)
        if not isinstance(index, list):
            index = [index]
        # Check if index exist :
        for k in index:
            if k not in uindex:
                warnings.warn(str(k) + " not found in the list of existing "
                              "areas")
            else:
                mask[self._color_idx == k] = True
        return mask

    # ========================================================================
    # SET FUNCTIONS
    # ========================================================================
    def set_roi_alpha(self, alpha, index=None):
        """Set the transparency level of selected areas.

        This method can be used to set the transparency of deep structures.

        Parameters
        ----------
        alpha : float
            The transparency level. This number must be between 0 and 1.
        index : list | None
            List of structures to modify their transparency. This parameter
            must be a list of integers. If index is None, the transparency
            is applied to all structures.
        """
        # Get corresponding index of areas :
        mask = self._get_idx_mask(index)
        # Set alpha :
        self.mesh.set_alpha(alpha, index=np.tile(mask[:, np.newaxis], (1, 3)))

    def set_roi_color(self, color, index=None):
        """Set the color of selected areas.

        This method can be used to set the color of deep structures.

        Parameters
        ----------
        color: string/tuple
            The color to use. This parameter can either be a matplotlib
            color or a RGB tuple.
        index : list | None
            List of structures to modify their color. This parameter must
            be a list of integers. If index is None, the color is applied
            to all structures.
        """
        # Get corresponding index of areas :
        mask = self._get_idx_mask(index)
        # Get RGBA color :
        color = color2vb(color)
        # Set color to vertex color :
        self.vertex_colors[mask, ...] = color
        self.mesh.set_color(self.vertex_colors)
        # Update the mesh :
        self.mesh.update()

    def set_roi_camera(self, camera):
        """Set a camera to the area mesh.

        The camera is essential to get the rotation / translation
        transformations that are then applied to each vertex for adapting the
        color.
        """
        self.mesh.set_camera(camera)

    def update_roi(self):
        """Update ROI."""
        pass

    def plot_roi(self):
        """Plot ROI."""
        self._preprocess()
        self._get_vertices()
        self._plot()
