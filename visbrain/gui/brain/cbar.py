"""Colorbar management for the Brain module."""
import logging

from visbrain.visuals import CbarQt, CbarObjetcs, CbarBase

logger = logging.getLogger('visbrain')

__all__ = ['BrainCbar']


class BrainCbar(object):
    """Create the colorbar, the objects and updating functions."""

    def __init__(self, camera):
        """Init."""
        # ------------------- CBOBJS -------------------
        # Create the cbar objects manager :
        self.cbobjs = CbarObjetcs()

        # ------------------- CBARBASE -------------------
        # ________ BRAIN ________
        cbproj = CbarBase(**self.atlas.to_dict())
        self.cbobjs.add_object('brain', cbproj)
        obj = self.cbobjs._objs['brain']
        obj._fcn = self._fcn_link_brain
        obj._minmaxfcn = self._fcn_minmax_brain

        # ________ ROI ________
        cbproj = CbarBase(**self.roi.to_dict())
        self.cbobjs.add_object('roi', cbproj)
        obj = self.cbobjs._objs['roi']
        obj._fcn = self._fcn_link_roi
        obj._minmaxfcn = self._fcn_minmax_roi

        # ________ Connectivity ________
        if self.connect.name is not None:
            for k in self.connect:
                cbconnect = CbarBase(**self.connect[k.name].to_dict())
                self.cbobjs.add_object(k.name, cbconnect)
                obj = self.cbobjs._objs[k.name]
                obj._fcn = self._fcn_link_connect(k.name)
                obj._minmaxfcn = self._fcn_minmax_connect(k.name)

        # ________ Pictures ________
        if self.pic.name is not None:
            for k in self.pic:
                cbpic = CbarBase(**self.pic[k.name].to_dict())
                self.cbobjs.add_object(k.name, cbpic)
                obj = self.cbobjs._objs[k.name]
                obj._fcn = self._fcn_link_pic(k.name)
                obj._minmaxfcn = self._fcn_minmax_pic(k.name)

        # ________ Default ________
        if all([k.name is None for k in (self.sources, self.pic,
                                         self.connect)]):
            cbproj = CbarBase()
            self.cbobjs.add_object('default', cbproj)

        # ------------------- CBQT -------------------
        # Add colorbar and interactions :
        self.cbqt = CbarQt(self._cbarWidget, self.cbpanel, self.cbobjs)
        is_cbqt = bool(self.cbqt)
        if is_cbqt:
            self.cbqt.select(0)
            self.cbqt._fcn_change_object()
        self.menuDispCbar.setEnabled(is_cbqt)
        self.cbqt.setEnabled('roi', hasattr(self.roi, 'mesh'))

        # Add the camera to the colorbar :
        self.cbqt.add_camera(camera)
        self.cbqt.cbui._cbar_grp.clicked.connect(self._fcn_cbar_display_grp)

    def _fcn_cbar_display_grp(self):
        """Display colorbar using the checkbox display."""
        viz = self.cbqt.cbui._cbar_grp.isChecked()
        self.menuDispCbar.setChecked(viz)
        self._fcn_menu_disp_cbar()

    ###########################################################################
    #                              BRAIN
    ###########################################################################
    def _fcn_link_brain(self):
        """Executed function when projection need updates."""
        kwargs = self.cbqt.cbobjs._objs['brain'].to_kwargs(True)
        self.atlas.update_from_dict(kwargs)
        self.atlas._update_cbar()

    def _fcn_minmax_brain(self):
        """Executed function for autoscale projections."""
        self.atlas._update_cbar_minmax()
        self.cbqt.cbobjs._objs['brain']['clim'] = self.atlas._clim
        kwargs = self.cbqt.cbobjs._objs['brain'].to_kwargs(True)
        self.atlas.update_from_dict(kwargs)
        self.atlas._update_cbar()

    ###########################################################################
    #                              ROI
    ###########################################################################
    def _fcn_link_roi(self):
        """Executed function when projection need updates."""
        kwargs = self.cbqt.cbobjs._objs['roi'].to_kwargs(True)
        self.roi.update_from_dict(kwargs)
        self.roi._update_cbar()

    def _fcn_minmax_roi(self):
        """Executed function for autoscale projections."""
        self.roi._update_cbar_minmax()
        self.cbqt.cbobjs._objs['roi']['clim'] = self.roi._clim
        kwargs = self.cbqt.cbobjs._objs['roi'].to_kwargs(True)
        self.roi.update_from_dict(kwargs)
        self.roi._update_cbar()

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
