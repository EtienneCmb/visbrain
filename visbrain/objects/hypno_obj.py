"""Hypnogram object."""
import os

import numpy as np
from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals import Hypnogram
from ..io import read_hypno


class HypnogramObj(VisbrainObject):
    """Hypnogram object.

    Parameters
    ----------
    name : string
        Name of the hypnogram object or path to a *.txt or *.csv file.
    data : array_like
        Array of data of shape (n_pts,).
    time : array_like | None
        Array of time points of shape (n_pts,)
    datafile : string | None
        Path to the data file.
    art, wake, rem, n1, n2, n3 :
        Stage identification inside the data array.
    art_visual, wake_visual, rem_visual, n1_visual, n2_visual, n3_visual :
        Stage order when plotting.
    art_color, wake_color, rem_color, n1_color, n2_color, n3_color :
        Stage color.
    line_width : float | 2.
        Line with of the hypnogram.
    antialias : bool | False
        Use anti-aliasing line.
    unicolor : bool | False
        Use a uni black color for the hypnogram.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Hypnogram object parent.
    verbose : string
        Verbosity level.
    kw : dict | {}
        Optional arguments are used to control the colorbar
        (See :class:`ColorbarObj`).

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import HypnogramObj
    >>> data = np.repeat(np.arange(6), 100) - 1.
    >>> h_obj = HypnogramObj('hypno', data)
    >>> h_obj.preview(axis=True)
    """

    def __init__(self, name, data=None, time=None, datafile=None, art=-1,
                 wake=0, n1=1, n2=2, n3=3, rem=4, art_visual=1, wake_visual=0,
                 rem_visual=-1, n1_visual=-2, n2_visual=-3, n3_visual=-4,
                 art_color='#8bbf56', wake_color='#56bf8b',
                 rem_color='#bf5656', n1_color='#aabcce', n2_color='#405c79',
                 n3_color='#0b1c2c', line_width=2., antialias=False,
                 unicolor=False, transform=None, parent=None, verbose=None,
                 **kw):
        """Init."""
        # Load *.txt, *.csv and *.hyp files :
        file, ext = os.path.splitext(name)
        if ext in ['.csv', '.txt', '.hyp', '.xlsx', '.edf']:
            if (ext == '.xlsx') and (time is None):
                raise ValueError("The `time` input should not be None with "
                                 "excel files. Use a NumPy array instead.")
            data, sf = read_hypno(name, time=time, datafile=datafile)
            name, time = os.path.split(name)[1], np.arange(len(data)) / sf
        # Initialize VisbrainObject and Hypnogram visuam creation :
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        self.line = Hypnogram(data, time, art, wake, n1, n2, n3, rem,
                              art_visual, wake_visual, rem_visual, n1_visual,
                              n2_visual, n3_visual, art_color, wake_color,
                              rem_color, n1_color, n2_color, n3_color,
                              line_width, antialias, unicolor,
                              parent=self._node)

    def _get_camera(self):
        t_min, t_max = self.line.time.min(), self.line.time.max()
        d_min, d_max = self.line.min_visual(), self.line.max_visual()
        rect = (t_min, d_min - .5, t_max - t_min, d_max - d_min + 1.)
        return scene.cameras.PanZoomCamera(rect=rect)

    def set_stage(self, stage, idx_start, idx_end):
        """Set stage.

        Parameters
        ----------
        stage : str, int
            Stage to define. Should either be a string (e.g 'art', 'rem'...) or
            an integer.
        idx_start : int
            Index where the stage begin.
        idx_end : int
            Index where the stage finish.
        """
        self.line.set_stage(stage, idx_start, idx_end)

    # ----------- LINE_WIDTH -----------
    @property
    def line_width(self):
        """Get the line_width value."""
        return self.line._line_width

    @line_width.setter
    def line_width(self, value):
        """Set line_width value."""
        self.line.line_width = value

    # ----------- UNICOLOR -----------
    @property
    def unicolor(self):
        """Get the unicolor value."""
        return self.line._unicolor

    @unicolor.setter
    def unicolor(self, value):
        """Set unicolor value."""
        self.line.unicolor = value
