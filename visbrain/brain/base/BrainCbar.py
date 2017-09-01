"""Colorbar management for the Brain module."""
from ...visuals import CbarQt, CbarObjetcs, CbarBase

__all__ = ['BrainCbar']


class BrainCbar(object):
    """Create the colorbar, the objects and updating functions."""

    def __init__(self, camera):
        """Init."""
        # ------------------- CBOBJS -------------------
        # Create the cbar objects manager :
        self.cbobjs = CbarObjetcs()

        # ------------------- CBARBASE -------------------
        # Cbarbase for the projection :
        cbproj = CbarBase(**self.sources.to_kwargs(True))
        self.cbobjs.add_object('Projection', cbproj)
        # Cbarbase for the connectivity :
        cbconnect = CbarBase(**self.connect.to_kwargs(True))
        self.cbobjs.add_object('Connectivity', cbconnect)
        # Cbarbase for the pictures :
        cbpic = CbarBase(**self.pic.to_kwargs(True))
        self.cbobjs.add_object('Pictures', cbpic)

        # ------------------- CBQT -------------------
        # Add colorbar and interactions :
        self.cbqt = CbarQt(self._cbarWidget, self.cbpanel, self.cbobjs)

        # ------------------- LINK -------------------
        # ________ Sources ________
        if self.sources.name != 'NoneSources':
            # ________ Connectivity ________
            if self.connect.name != 'NoneConnect':
                # Link the colorbase with connectivity :
                self.cbqt.link('Connectivity', self._fcn_link_connect,
                               self._fcn_minmax_connect)
            else:
                self.cbqt.setEnabled('Connectivity', False)
            # ________ Pictures ________
            if self.pic.mesh.name != 'NonePic':
                # Link the colorbase with connectivity :
                self.cbqt.link('Pictures', self._fcn_link_pic,
                               self._fcn_minmax_pic)
            else:
                self.cbqt.setEnabled('Pictures', False)

            # Connect graphical buttons :
            self.cbqt.select('Projection', onload=False)
            self.cbqt._connect()
        else:
            self.cbqt.setEnabled('Connectivity', False)
            self.cbqt.setEnabled('Pictures', False)
        self.cbqt.setEnabled('Projection', False)

        # Add the camera to the colorbar :
        self.cbqt.add_camera(camera)

    ###########################################################################
    #                              PROJECTION
    ###########################################################################
    def _fcn_link_proj(self):
        """Executed function when projection need updates."""
        self._proj2Color()

    def _fcn_minmax_proj(self):
        """Executed function for autoscale projections."""
        self.cbqt.cbobjs._objs['Projection']._clim = self.sources._minmax
        self._proj2Color()

    ###########################################################################
    #                              CONNECTIVITY
    ###########################################################################
    def _fcn_link_connect(self):
        """Executed function when connectivity need updates."""
        kwargs = self.cbqt.cbobjs._objs['Connectivity'].to_kwargs()
        self.connect.update_from_dict(kwargs)
        self.connect.update()

    def _fcn_minmax_connect(self):
        """Executed function for autoscale connectivity."""
        self.connect.needupdate = True
        self.connect.update()
        self.cbqt.cbobjs._objs['Connectivity']._clim = self.connect._minmax

    ###########################################################################
    #                              PICTURES
    ###########################################################################
    def _fcn_link_pic(self):
        """Executed function when pictures need updates."""
        kwargs = self.cbqt.cbobjs._objs['Pictures'].to_kwargs()
        self.pic.mesh.set_data(**kwargs)
        self.pic.mesh.update()

    def _fcn_minmax_pic(self):
        """Executed function for autoscale pictures."""
        self.cbqt.cbobjs._objs['Pictures']._clim = self.pic._minmax
        kwargs = self.cbqt.cbobjs._objs['Pictures'].to_kwargs()
        self.pic.mesh.set_data(**kwargs)
        self.pic.mesh.update()
