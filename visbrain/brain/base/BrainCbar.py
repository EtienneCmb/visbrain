"""Colorbar management for the Brain module."""
from ...utils import CbarQt, CbarObjetcs, CbarBase

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

        # ------------------- CBQT -------------------
        # Add colorbar and interactions :
        self.cbqt = CbarQt(self._cbarWidget, self.cbpanel, self.cbobjs)

        # ------------------- LINK -------------------
        if self.sources.name != 'NoneSources':
            if self.connect.name != 'NoneConnect':
                # Link the colorbase with connectivity :
                self.cbqt.link('Connectivity', self._fcn_link_connect,
                               self._fcn_minmax_connect)
            else:
                self.cbqt.setEnabled('Connectivity', False)
                self.menuDispCbar.setEnabled(False)

            # Connect graphical buttons :
            self.cbqt.select('Projection', onload=False)
            self.cbqt._connect()
        else:
            self.cbqt.setEnabled('Connectivity', False)
            self.menuDispCbar.setEnabled(False)
        self.cbqt.setEnabled('Projection', False)

        # Add the camera to the colorbar :
        self.cbqt.add_camera(camera)

    def _fcn_link_proj(self):
        """Executed function when projection need updates."""
        self._proj2Color()

    def _fcn_minmax_proj(self):
        """Executed function for autoscale projections."""
        self.cbqt.cbobjs._objs['Projection']._clim = self.sources._minmax
        self._proj2Color()

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
