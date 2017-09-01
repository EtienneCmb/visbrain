
import vispy.scene.visuals as visu

from ...visuals import PicMesh, CbarArgs


class PicBase(CbarArgs):
    """docstring for PicBase."""

    def __init__(self, pic_xyz=None, pic_data=None, pic_dxyz=(0., 0., 1.),
                 pic_width=7., pic_height=7., pic_select=None,
                 pic_cmap='viridis', pic_clim=None, pic_vmin=None,
                 pic_vmax=None, pic_under='gray', pic_over='red', **kwargs):
        """Init."""
        if (pic_xyz is not None) and (pic_data is not None):
            # Get (min, max) :
            self._minmax = (pic_data.min(), pic_data.max())
            # Define clim :
            clim = pic_clim if pic_clim is not None else self._minmax
            # Create the mesh :
            self.mesh = PicMesh(pic_data, pic_xyz, width=pic_width,
                                height=pic_height, dxyz=pic_dxyz,
                                select=pic_select, name='Pictures', clim=clim,
                                cmap=pic_cmap, vmin=pic_vmin, vmax=pic_vmax,
                                under=pic_under, over=pic_over)
        else:
            self.mesh = visu.Image(name='NonePic')
            clim = (0., 1.)
        # Vmin/Vmax only active if not None and in [clim[0], clim[1]] :
        isvmin = (pic_vmin is not None) and (clim[0] < pic_vmin < clim[1])
        isvmax = (pic_vmax is not None) and (clim[0] < pic_vmax < clim[1])
        # Initialize colorbar elements :
        CbarArgs.__init__(self, pic_cmap, clim, isvmin, pic_vmin,
                          isvmax, pic_vmax, pic_under, pic_over)

    def set_camera(self, camera):
        """Set the camera to the mesh."""
        if self.mesh.name == 'NonePic':
            pass
        else:
            self.mesh.camera = camera
