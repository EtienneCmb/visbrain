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
        # ________ Connectivity ________
        if self.connect.name is not None:
            for k in self.connect:
                cbconnect = CbarBase(**self.connect[k.name].to_kwargs(True))
                self.cbobjs.add_object(k.name, cbconnect)
                obj = self.cbobjs._objs[k.name]
                obj._fcn = self._fcn_link_connect(k.name)
                obj._minmaxfcn = self._fcn_minmax_connect(k.name)

        # ________ Pictures ________
        if self.pic.name is not None:
            for k in self.pic:
                cbpic = CbarBase(**self.pic[k.name].to_kwargs(True))
                self.cbobjs.add_object(k.name, cbpic)
                obj = self.cbobjs._objs[k.name]
                obj._fcn = self._fcn_link_pic(k.name)
                obj._minmaxfcn = self._fcn_minmax_pic(k.name)

        # ------------------- CBQT -------------------
        # Add colorbar and interactions :
        self.cbqt = CbarQt(self._cbarWidget, self.cbpanel, self.cbobjs)
        is_cbqt = bool(self.cbqt)
        if is_cbqt:
            self.cbqt.select(0)
            self.cbqt._fcn_change_object()
        self.menuDispCbar.setEnabled(is_cbqt)

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
    def _fcn_link_connect(self, name):
        """Executed function when connectivity need updates."""
        def _get_connect_fcn():
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs(True)
            self.connect[name].update_from_dict(kwargs)
            self.connect[name]._build_line()
        return _get_connect_fcn

    def _fcn_minmax_connect(self, name):
        """Executed function for autoscale connectivity."""
        def _get_minmax_connect_fcn():
            self.cbqt.cbobjs._objs[name]._clim = self.connect[name]._minmax
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs(True)
            self.connect[name].update_from_dict(kwargs)
            self.connect[name]._build_line()
        return _get_minmax_connect_fcn

    ###########################################################################
    #                              PICTURES
    ###########################################################################
    def _fcn_link_pic(self, name):
        """Executed function when pictures need updates."""
        def _get_pic_fcn():
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs()
            self.pic[name].update_from_dict(kwargs)
            self.pic[name]._pic.set_data(**kwargs)
        return _get_pic_fcn

    def _fcn_minmax_pic(self, name):
        """Executed function for autoscale pictures."""
        def _get_minmax_pic_fcn():
            self.cbqt.cbobjs._objs[name]._clim = self.pic[name]._minmax
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs()
            self.pic[name].update_from_dict(kwargs)
            self.pic[name]._pic.set_data(**kwargs)
        return _get_minmax_pic_fcn
