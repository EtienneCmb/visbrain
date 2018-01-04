"""Mehods to manage interactions between the GUI and objects."""
from functools import wraps

from .gui import CbarForm
from .CbarVisual import CbarVisual
from ...utils import color2json, mpl_cmap, mpl_cmap_index, disconnect_all

__all__ = ['CbarQt']


def _run_method_if_needed(fn):
    @wraps(fn)
    def wrapper(self):
        if self._trigger_cbar:
            fn(self)
    return wrapper


def _update_obj(fn):
    @wraps(fn)
    def wrapper(self):
        if self._update_obj:
            fn(self)
    return wrapper


class CbarQt(object):
    """Link the GUI colorbar with the VisPy based colorbar.

    self[obj_name] : get the item from the GUI
    self[obj_name] = value : set the value to the VisPy based colorbar.

    Parameters
    ----------
    gui_w: PyQt widget
        The widget for adding the GUI colorar properties.
    viz_w: PyQt widget
        The widget for adding the VisPy based colorbar.
    """

    def __init__(self, gui_w, viz_w, cbobjs, parent=None, camera=None):
        """Init."""
        # --------------------------------------------------------------------
        #                          GUI COMPONENTS
        # --------------------------------------------------------------------
        # Add colorbar properties to gui_w :
        self.cbui = CbarForm()
        self.cbui.setupUi(gui_w)
        # Add VisPy based colorbar :
        self.cbviz = CbarVisual(parent=parent)
        viz_w.addWidget(self.cbviz._canvas.native)
        self.cbobjs = cbobjs
        # Add items contains in the cbobs :
        self['object'].addItems(self.cbobjs.keys())

        # --------------------------------------------------------------------
        #                         CONNECT GUI ELEMENTS
        # --------------------------------------------------------------------
        self['object'].currentIndexChanged.connect(self._fcn_change_object)
        self['bckCol'].editingFinished.connect(self._fcn_bgcolor)
        self['txtCol'].editingFinished.connect(self._fcn_text_color)
        self['ndigits'].valueChanged.connect(self._fcn_n_digits)
        self['width'].valueChanged.connect(self._fcn_width)
        self['border'].clicked.connect(self._fcn_border)
        self['bw'].valueChanged.connect(self._fcn_bw)
        self['limTxt'].clicked.connect(self._fcn_limits)
        self['ndigits'].setKeyboardTracking(False)
        self['width'].setKeyboardTracking(False)

        # _____________ COLORMAPS _____________
        self._cmaps = mpl_cmap()
        self['cmap'].addItems(self._cmaps)
        self['cmap'].currentIndexChanged.connect(self._fcn_cmap_changed)
        self['cmapRev'].clicked.connect(self._fcn_cmap_changed)

        # _____________ CLIM _____________
        self['climm'].valueChanged.connect(self._fcn_clim_changed)
        self['climM'].valueChanged.connect(self._fcn_clim_changed)
        self['climm'].setKeyboardTracking(False)
        self['climM'].setKeyboardTracking(False)

        # _____________ VMIN/VMAX _____________
        # Vmin :
        self['isvmin'].clicked.connect(self._fcn_vmin_changed)
        self['vmin'].valueChanged.connect(self._fcn_vmin_changed)
        self['under'].editingFinished.connect(self._fcn_vmin_changed)
        self['vmin'].setKeyboardTracking(False)
        # Vmax :
        self['isvmax'].clicked.connect(self._fcn_vmax_changed)
        self['vmax'].valueChanged.connect(self._fcn_vmax_changed)
        self['over'].editingFinished.connect(self._fcn_vmax_changed)
        self['vmax'].setKeyboardTracking(False)

        # _____________ TEXT _____________
        # Colorbar label :
        self['cblabel'].editingFinished.connect(self._fcn_cb_title)
        self['cbTxtSz'].valueChanged.connect(self._fcn_cb_txt_size)
        self['cbTxtSh'].valueChanged.connect(self._fcn_cb_txt_shift)
        self['cbTxtSz'].setKeyboardTracking(False)
        self['cbTxtSh'].setKeyboardTracking(False)
        # Limits label :
        self['txtSz'].valueChanged.connect(self._fcn_txt_size)
        self['txtSh'].valueChanged.connect(self._fcn_txt_shift)
        self['txtSz'].setKeyboardTracking(False)
        self['txtSh'].setKeyboardTracking(False)

        # _____________ AUTOSCALE _____________
        self['autoscale'].clicked.connect(self._fcn_cb_autoscale)
        self._trigger_cbar = True

    ###########################################################################
    ###########################################################################
    #                            GET / SET ITEMS
    ###########################################################################
    ###########################################################################
    def __getitem__(self, key):
        """Get the item from the GUI."""
        return eval('self.cbui.' + key)

    def __setitem__(self, key, value):
        """Set VisPy based colormap item from GUI properties."""
        if not isinstance(value, str):
            exec('self.cbviz.' + key + '=' + str(value))
        else:
            exec("self.cbviz." + key + "='" + value + "'")

    def __bool__(self):
        """Test if there's objects defined."""
        return bool(len(self.cbobjs.keys()))

    ###########################################################################
    ###########################################################################
    #                            LOAD / SAVE
    ###########################################################################
    ###########################################################################
    def save(self, filename):
        """Save all colorbar configurations.

        Parameters
        ----------
        filename : string
            Name of the file to be saved.
        """
        self.cbobjs.save(filename)

    def load(self, filename, **kwargs):
        """Load a colorbar configuration file.

        Parameters
        ----------
        filename : string
            Name of the file to load.
        kwargs : dict, optional, (def: {})
            Further arguments to pass to the CbarObjects class.
        """
        self.cbobjs.load(filename, **kwargs)

    def add_camera(self, camera):
        """Add a camera to the VisPy based colorbar."""
        self.cbviz._wc.camera = camera

    def to_dict(self):
        """Return a dictionary of the current visual state."""
        self.cbviz.to_dict()

    def link(self, name, fcn, minmaxfcn):
        """Link an object with a function.

        When an colormap argument changed, a function associated to the object
        is executed (only for colormap arguments i.e. cmap, clim, vmin, vmax,
        under, over).
        """
        self.cbobjs._objs[name]._fcn = fcn
        self.cbobjs._objs[name]._minmaxfcn = minmaxfcn

    def select(self, name):
        """Select an object.

        Parameters
        ----------
        name : string
            Name of the object to select.
        """
        # Get the list of all current objects :
        all_items = [self['object'].itemText(i) for i in range(
            self['object'].count())]
        if isinstance(name, str):
            idx = all_items.index(name)
        elif isinstance(name, int):
            idx = name
            name = all_items[name]
        assert name in all_items
        # Select object in the cbar object manager :
        self.cbobjs.select(name)
        self['object'].setCurrentIndex(idx)

    def setEnabled(self, name, enable=True):  # noqa
        """Deactivate an object."""
        # Get the list of all current objects :
        all_items = [self['object'].itemText(i) for i in range(
            self['object'].count())]
        if name in all_items:
            # Find the index and set it in the combobox :
            idx = all_items.index(name)
            self['object'].model().item(idx).setEnabled(enable)

    ###########################################################################
    ###########################################################################
    #                CONNECT / DISCONNECT / INITIALIZE
    ###########################################################################
    ###########################################################################
    # --------------------------------------------------------------------
    #                          INITIALIZE GUI
    # --------------------------------------------------------------------
    def _initialize(self):
        # _____________ SETTINGS _____________
        self['bckCol'].setText(str(self.cbobjs['bgcolor']))
        self['txtCol'].setText(str(self.cbobjs['txtcolor']))
        self['ndigits'].setValue(self.cbobjs['ndigits'])
        self['width'].setValue(self.cbobjs['width'])
        self['border'].setChecked(self.cbobjs['border'])
        self['bw'].setValue(self.cbobjs['bw'])
        self['limTxt'].setChecked(self.cbobjs['limtxt'])

        # _____________ COLORMAPS _____________
        idx, rev = mpl_cmap_index(self.cbobjs['cmap'])
        self['cmap'].setCurrentIndex(idx)
        self['cmapRev'].setChecked(rev)

        # _____________ CLIM _____________
        # Clim should never be None :
        self['climm'].setValue(self.cbobjs['clim'][0])
        self['climM'].setValue(self.cbobjs['clim'][1])

        # _____________ VMIN/VMAX _____________
        # Set vmin/vmax limits :
        self._check_vmin_vmax()
        # Vmin/under :
        self['isvmin'].setChecked(self.cbobjs['isvmin'])
        self['vmin'].setValue(self.cbobjs['vmin'])
        self['under'].setText(str(self.cbobjs['under']))
        # Vmax/over :
        self['isvmax'].setChecked(self.cbobjs['isvmax'])
        self['vmax'].setValue(self.cbobjs['vmax'])
        self['over'].setText(str(self.cbobjs['over']))

        # _____________ TEXT _____________
        # Colorbar :
        self['cblabel'].setText(str(self.cbobjs['cblabel']))
        self['cbTxtSz'].setValue(self.cbobjs['cbtxtsz'])
        self['cbTxtSh'].setValue(self.cbobjs['cbtxtsh'])
        # Text limits :
        self['txtSz'].setValue(self.cbobjs['txtsz'])
        self['txtSh'].setValue(self.cbobjs['txtsh'])

        # Enable to run methods to update the CbarVisual :
        self._trigger_cbar = True
        self._gui_to_visual()

    # --------------------------------------------------------------------
    #                             GUI -> VISUAL
    # --------------------------------------------------------------------
    def _gui_to_visual(self):
        # Settings :
        self._fcn_bgcolor()
        self._fcn_text_color()
        self._fcn_n_digits()
        self._fcn_width()
        self._fcn_border()
        self._fcn_bw()
        self._fcn_limits()
        # Cmap/Clim/Vmin/Vmax :
        self._fcn_cmap_changed()
        self._fcn_clim_changed()
        self._fcn_vmin_changed()
        self._fcn_vmax_changed()
        # Text :
        self._fcn_cb_title()
        self._fcn_cb_txt_size()
        self._fcn_cb_txt_shift()
        self._fcn_txt_size()
        self._fcn_txt_shift()

    ###########################################################################
    ###########################################################################
    #                              SUB-FONCTION
    ###########################################################################
    ###########################################################################
    # --------------------------------------------------------------------
    #                             SETTINGS
    # --------------------------------------------------------------------
    def _fcn_change_object(self, *args, clean=False):
        """Change colorbar object."""
        # Disconnect interactions :
        self._trigger_cbar = False
        disconnect_all(self['object'])
        # Clean drowdown box for object selection :
        if clean:
            self['object'].clear()
            self['object'].addItems(self.cbobjs.keys())
        # Get the current selected text :
        name = str(self['object'].currentText())
        # Select this object :
        self.cbobjs.select(name)
        # Update GUI :
        self._initialize()
        # Re-connect interactions :
        self._trigger_cbar = True
        self['object'].currentIndexChanged.connect(self._fcn_change_object)

    @_run_method_if_needed
    def _fcn_bgcolor(self):
        """Change background color."""
        bgcolor = color2json(self['bckCol'])
        self['bgcolor'] = bgcolor
        self.cbobjs['bgcolor'] = self.cbviz.bgcolor

    @_run_method_if_needed
    def _fcn_n_digits(self):
        """Change the number of digits."""
        ndigits = self['ndigits'].value()
        if ndigits > 0:
            self['ndigits'] = ndigits
            self.cbobjs['ndigits'] = self.cbviz.ndigits
            self['climm'].setDecimals(ndigits)
            self['climM'].setDecimals(ndigits)
            self['vmin'].setDecimals(ndigits)
            self['vmax'].setDecimals(ndigits)

    @_run_method_if_needed
    def _fcn_width(self):
        """Change colorbar width."""
        self['width'] = self['width'].value()
        self.cbobjs['width'] = self.cbviz.width

    @_run_method_if_needed
    def _fcn_border(self):
        """Set the border."""
        viz = self['border'].isChecked()
        self['border'] = viz
        self.cbobjs['border'] = self.cbviz.border
        self['bw'].setEnabled(viz)

    @_run_method_if_needed
    def _fcn_bw(self):
        """Change border width."""
        self['bw'] = self['bw'].value()
        self.cbobjs['bw'] = self.cbviz.bw

    # --------------------------------------------------------------------
    #                                CMAP
    # --------------------------------------------------------------------
    @_run_method_if_needed
    def _fcn_cmap_changed(self):
        """Change the colormap."""
        rv = self['cmapRev'].isChecked() * '_r'
        self['cmap'] = str(self['cmap'].currentText()) + rv
        self.cbobjs['cmap'] = self.cbviz.cmap
        # Run object's update function :
        self.cbobjs.update()

    # --------------------------------------------------------------------
    #                             CLIM
    # --------------------------------------------------------------------
    @_run_method_if_needed
    def _fcn_clim_changed(self):
        """Update colorbar limits."""
        # Get value (climm, climM):
        climm = float(self['climm'].value())
        clim_max = float(self['climM'].value())
        # Fix (climm, climM) limits :
        if climm < clim_max:
            # Update clim :
            self['clim'] = (climm, clim_max)
            self.cbobjs['clim'] = self.cbviz.clim
            # Update vmin/vmax limits :
            self._check_vmin_vmax()
            # Run object's update function :
            self.cbobjs.update()
        else:
            raise ValueError(str(tuple((climm, clim_max))) + " : clim.min() "
                             "> clim.max().")

    # --------------------------------------------------------------------
    #                   VMIN / VMAX / UNDER / OVER
    # --------------------------------------------------------------------
    def _check_vmin_vmax(self):
        """Activate checkboxs if vmin/vmax not None."""
        # Get clim and define step :
        climm = float(self['climm'].value())
        clim_max = float(self['climM'].value())
        step = (clim_max - climm) / 100.
        # -------------- Vmin --------------
        if not isinstance(self.cbobjs['vmin'], (int, float)):
            self.cbobjs['vmin'] = climm - 1.
        self['vmin'].setMinimum(climm)
        self['vmin'].setMaximum(clim_max)
        self['vmin'].setSingleStep(step)

        # -------------- Vmax --------------
        if not isinstance(self.cbobjs['vmax'], (int, float)):
            self.cbobjs['vmax'] = clim_max + 1.
        self['vmax'].setMinimum(climm)
        self['vmax'].setMaximum(clim_max)
        self['vmax'].setSingleStep(step)

    @_run_method_if_needed
    def _fcn_vmin_changed(self):
        """Change vmin/vmax/under/over."""
        isvmin = self['isvmin'].isChecked()
        # Enable/Disable panels :
        self['vminW'].setEnabled(isvmin)
        # Vmin :
        self['isvmin'] = isvmin
        self['vmin'] = self['vmin'].value()
        self['under'] = color2json(self['under'])
        self.cbobjs['isvmin'] = self.cbviz.isvmin
        self.cbobjs['vmin'] = self.cbviz.vmin
        self.cbobjs['under'] = self.cbviz.under
        # Run object's update function :
        self.cbobjs.update()

    @_run_method_if_needed
    def _fcn_vmax_changed(self):
        """Change vmin/vmax/under/over."""
        isvmax = self['isvmax'].isChecked()
        self['vmaxW'].setEnabled(isvmax)
        # Vmax
        self['isvmax'] = isvmax
        self['vmax'] = self['vmax'].value()
        self['over'] = color2json(self['over'])
        self.cbobjs['isvmax'] = self.cbviz.isvmax
        self.cbobjs['vmax'] = self.cbviz.vmax
        self.cbobjs['over'] = self.cbviz.over
        # Run object's update function :
        self.cbobjs.update()

    @_run_method_if_needed
    def _fcn_limits(self):
        """Display/hide vmin/vmax."""
        self['limtxt'] = self['limTxt'].isChecked()
        self.cbobjs['limtxt'] = self.cbviz.limtxt

    # --------------------------------------------------------------------
    #                             TEXT
    # --------------------------------------------------------------------
    @_run_method_if_needed
    def _fcn_cb_title(self):
        """Change colorbar title."""
        self['cblabel'] = str(self['cblabel'].text())
        self.cbobjs['cblabel'] = self.cbviz.cblabel

    @_run_method_if_needed
    def _fcn_cb_txt_size(self):
        """Change colorbar text size."""
        self['cbtxtsz'] = self['cbTxtSz'].value()
        self.cbobjs['cbtxtsz'] = self.cbviz.cbtxtsz

    @_run_method_if_needed
    def _fcn_cb_txt_shift(self):
        """Change cblabel shift."""
        self['cbtxtsh'] = self['cbTxtSh'].value()
        self.cbobjs['cbtxtsh'] = self.cbviz.cbtxtsh

    @_run_method_if_needed
    def _fcn_txt_size(self):
        """Change text size for limits."""
        self['txtsz'] = self['txtSz'].value()
        self.cbobjs['txtsz'] = self.cbviz.txtsz

    @_run_method_if_needed
    def _fcn_txt_shift(self):
        """Change text shift."""
        self['txtsh'] = self['txtSh'].value()

    @_run_method_if_needed
    def _fcn_text_color(self):
        """Change text color."""
        txtcolor = color2json(self['txtCol'])
        self['txtcolor'] = txtcolor
        self.cbobjs['txtcolor'] = self.cbviz.txtcolor
        self.cbobjs['txtsh'] = self.cbviz.txtsh

    # --------------------------------------------------------------------
    #                             TEXT
    # --------------------------------------------------------------------
    def _fcn_cb_autoscale(self, *args, name=None):
        """Autoscale limits to data (Min, Max)."""
        # Select object if it's not the current one :
        if (name is not None) and self.cbobjs.name != name:
            self.select(name)
        # Disconnect clim buttons :
        self._trigger_cbar = False
        # Run the auto-scaling function :
        self['isvmin'] = False
        self['isvmax'] = False
        self.cbobjs['isvmin'] = False
        self.cbobjs['isvmax'] = False
        self.cbobjs.autoscale()
        # Set clim to the gui :
        self['climm'].setValue(self.cbobjs['clim'][0])
        self['climM'].setValue(self.cbobjs['clim'][1])
        # Check vmin/vmax values :
        self._check_vmin_vmax()
        # Set clim to the VisPy based colorbar :
        self['clim'] = self.cbobjs['clim']
        # Deactivate vmin/vmax :
        self['isvmin'].setChecked(False)
        self['isvmax'].setChecked(False)
        self['isvmin'] = self['isvmax'] = False
        self._trigger_cbar = True
