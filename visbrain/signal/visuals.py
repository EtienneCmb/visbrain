"""Visual object creation."""
import numpy as np
from scipy.signal import welch
from itertools import product

from vispy import scene
import vispy.visuals.transforms as vist

from ..visuals import GridSignal, TFmapsMesh
from ..utils import color2vb, vispy_array, PrepareData

__all__ = ('Visuals')


class SignalAnnotations(object):
    """Add annotations to the signal layout."""

    def __init__(self, parent=None):
        """Init."""
        # Create two dictionaries (for coordinates and text) :
        self._annotations = {}
        self._annotations_txt = {}
        # Create markers for annotations :
        pos = np.random.rand(2, 3)
        self._annot_mark = scene.visuals.Markers(pos=pos, parent=parent)
        self._annot_mark.visible = False
        # Create text for annotations :
        self._annot_text = scene.visuals.Text(parent=parent, anchor_x='left',
                                              bold=True, font_size=14.)
        tr = (self._time.max() - self._time.min()) / 50.
        self._annot_text.transform = vist.STTransform(translate=(tr, 0., 0.))
        self._annot_text.visible = False

    def add_annotations(self, signal, coord, text='Enter annotation'):
        """Add new annotation.

        Parameters
        ----------
        signal : string
            Representation of the curently selected signal (e.g '(0, 0, :)')
        coord : array_like
            Array of coordinates (x, y) of shape (2,)
        text : string
            Text associated to the annoations.
        """
        coord = np.asarray(coord).reshape(-1)
        if signal in self._annotations.keys():
            m = self._annotations[signal]
            self._annotations[signal] = np.vstack((m, coord))
            self._annotations_txt[signal].append(text)
        else:
            self._annotations[signal] = coord.reshape(1, -1)
            self._annotations_txt[signal] = [text]

    def is_event_annotated(self, name):
        """Get if the present has been annotated."""
        return name in self._annotations.keys()

    def get_event_coord(self, name):
        """Get coordinates of the annotated event."""
        m = np.array([])
        return self._annotations[name] if self.is_event_annotated(name) else m

    def set_text(self, signal, coord, text):
        """Update annotation text."""
        row, _ = self._get_coord_index(signal, coord)
        if row is not None:
            self._annotations_txt[signal][row] = text
            self._annot_text.text = text

    def select_annotation(self, signal, coord):
        """Select an annotation."""
        # Get coord index :
        row, coord = self._get_coord_index(signal, coord)
        is_coord = (row, coord) != (None, None)
        if is_coord:
            # Set text and position to scene.visuals.Text() :
            self._annot_text.text = self._annotations_txt[signal][row]
            self._annot_text.pos = np.append(coord, -20).astype(np.float32)
        # Set text visible / hide :
        self._annot_text.visible = is_coord

    def _coord_to_tuple(self, coord):
        """Transform coord into a compatible tuple of floats."""
        if isinstance(coord, str):
            return tuple(float(k) for k in coord[1:-1].split(', '))
        else:
            assert len(coord) == 2
            return coord

    def _get_coord_index(self, signal, coord):
        # Select if annotated :
        if self.is_event_annotated(signal):
            # Find coordinates :
            coords = self._annotations[signal]
            coord = self._coord_to_tuple(coord)
            idx = np.where(coords == coord)
            if idx and np.array_equal(idx[1], [0, 1]):
                row = idx[0][0]
                return row, coord
            else:
                return (None, None)
        else:
            return (None, None)


class SignalVisual(SignalAnnotations):
    """1-D signal class creation.

    Parameters
    ----------
    time : array_like
        Time vector of shape (N,)
    sf : float
        The sampling frequency.
    sh : tuple
        Shape of the 2-D array.
    form : {'line', 'marker', 'histogram'}
        Plotting type.
    color : array_like/string/tuple | 'black'
        Color of the plot.
    lw : float | 2.
        Line width (form='line').
    symbol : string | 'o'
        Marker symbol (form='marker').
    size : float | 10.
        Marker size (form='marker').
    nbins : int | 10
        Number of bins for the histogram (form='histogram')
    line_rendering : {'gl', 'agg'}
        Specify the line rendering method. Use 'gl' for a fast but lower
        quality lines and 'agg', looks better but slower.
    parent : VisPy.parent | None
        Parent of the mesh.
    """

    def __init__(self, time, sf, sh, axis, form='line', line_rendering='gl',
                 parent=None):
        """Init."""
        self.form = form
        self._time = time
        self._sf = sf
        self._axis = axis
        self._index = 0  # selected index of the 3-d array
        self.rect = (0., 0., 1., 1.)
        self._prep = PrepareData(way='filtfilt')
        # Build navigation index :
        if len(sh) in [2, 3]:
            sh = list(sh)
            del sh[axis]
            self._navidx = list(product(*tuple(range(k) for k in sh)))
        else:
            self._navidx = [[]]

        # Create visuals :
        pos = np.random.rand(2, 2)
        posh = np.random.rand(2,)
        self._th = scene.visuals.Line(pos=pos, name='threshold', parent=parent)
        self._line = scene.visuals.Line(pos=pos, name='line', parent=parent,
                                        method=line_rendering)
        self._mark = scene.visuals.Markers(pos=pos, name='marker',
                                           parent=parent)
        self._hist = scene.visuals.Histogram(data=posh, orientation='h',
                                             parent=parent, name='histogram')
        self._tf = TFmapsMesh(parent=parent)
        self._th.visible = False

        # Initialize annotations :
        SignalAnnotations.__init__(self, parent)

    def __str__(self):
        """String representation of the currently selected index."""
        lst = [str(k) for k in self._navidx[self._index]]
        lst.insert(self._axis, ':')
        return '(' + ', '.join(lst) + ')'

    def set_data(self, data, index, color='black', lw=2., nbins=10,
                 symbol='disc', size=10., form='line', th=None, norm=None,
                 window=None, overlap=0., baseline=None, clim=None,
                 cmap='viridis', interpolation='gaussian', nperseg=256,
                 noverlap=128):
        """Set data to the plot.

        Parameters
        ----------
        data : array_like
            Raw data vector of shape (N,)
        index : int | 0
            Index of the 3-d array.
        color : array_like/string/tuple | None
            Color of the plot.
        lw : float | None
            Line width (form='line').
        symbol : string | None
            Marker symbol (form='marker').
        size : float | None
            Marker size (form='marker').
        nbins : int | None
            Number of bins for the histogram (form='histogram')
        form : {'line', 'marker', 'histogram', 'tf'}
            Plotting type.
        th : tuple | None
            Tuple of floats for line thresholding.
        norm : int | None
            Normalization method for (form='tf').
        window : tuple | None
            Averaging window (form='tf').
        overlap : float | 0.
            Overlap between successive windows (form='tf').
        baseline : tuple | None
            Baseline period for the normalization (form='tf').
        """
        # Update variable :
        self.form = form
        self._index = index
        color = color2vb(color)

        # Get data index :
        if data.ndim == 1:
            idx = slice(None)
        elif data.ndim in [2, 3]:
            idx = list(self._navidx[index])
            idx.insert(self._axis, slice(None))

        # Convert data to be compatible with VisPy and prepare data :
        data_c = vispy_array(data[idx]).copy()
        _data = self._prep._prepare_data(self._sf, data_c, self._time)

        # Set data :
        if form in ['line', 'marker', 'psd', 'butterfly']:  # line and marker
            # Get position array :
            pos = np.c_[self._time, _data]
            # Send position :
            if form in ['line', 'psd']:
                if form == 'psd':
                    fmax = self._sf / 4.
                    f, pxx = welch(_data, self._sf, nperseg=nperseg,
                                   noverlap=noverlap)
                    f_sf4 = abs(f - fmax)
                    f_1 = abs(f - 1.)
                    fidx_sf4 = np.where(f_sf4 == f_sf4.min())[0][0]
                    fidx_1 = np.where(f_1 == f_1.min())[0][0]
                    pos = np.c_[f[fidx_1:-fidx_sf4], pxx[fidx_1:-fidx_sf4]]
                # Threshold :
                is_th = isinstance(th, (tuple, list, np.ndarray))
                col = color2vb(color, length=pos.shape[0])
                if is_th:
                    # Build threshold segments :
                    t_min, t_max = self._time.min(), self._time.max()
                    pos_th = np.vstack(([t_min, th[0]], [t_max, th[0]],
                                        [t_min, th[1]], [t_max, th[1]]))
                    self._th.set_data(pos_th, connect='segments',
                                      color=color2vb('#ab4642'))
                    # Build line color :
                    col = color2vb(color, length=len(_data))
                    cond = np.logical_or(_data < th[0], _data > th[1])
                    col[cond, :] = color2vb('#ab4642')
                self._th.visible = is_th
                self._line.set_data(pos, width=lw, color=col)
                self._line.update()
            elif form == 'marker':
                self._mark.set_data(pos, face_color=color, symbol=symbol,
                                    size=size, edge_width=0.)
                self._mark.update()
            elif form == 'butterfly':
                # Get soe shape related variables :
                n, m = len(self._time), int(np.prod(data.shape))
                n_rep = int(m / n)
                data = vispy_array(data)
                # Build position :
                pos = np.c_[np.tile(self._time.ravel(), n_rep), data.ravel()]
                # Disconnect some points :
                connect = np.c_[np.arange(m - 1), np.arange(1, m)]
                to_delete = np.linspace(n - 1, m - 1, n_rep)
                connect = np.delete(connect, to_delete, axis=0)
                # Build color :
                col = color2vb(color, length=m)
                # singcol = np.random.uniform(size=(n_rep, 3), low=.2,
                #                             high=.8).astype(np.float32)
                # col = np.repeat(singcol, n, 0)
                # Send data :
                self._line.set_data(pos, width=lw, color=col, connect=connect)
                self._line.update()
            # Get camera rectangle :
            t_min, t_max = pos[:, 0].min(), pos[:, 0].max()
            d_min, d_max = pos[:, 1].min(), pos[:, 1].max()
            off = .05 * (d_max - d_min)
            self.rect = (t_min, d_min - off, t_max - t_min,
                         d_max - d_min + 2 * off)
        elif form == 'histogram':  # histogram
            # Compute the mesh :
            mesh = scene.visuals.Histogram(_data, nbins)
            # Get the vertices and faces of the mesh :
            vert = mesh.mesh_data.get_vertices()
            faces = mesh.mesh_data.get_faces()
            # Pass vertices and faces to the histogram :
            self._hist.set_data(vert, faces, color=color)
            # Compute the histogram :
            raw, xvec = np.histogram(_data, nbins)
            # Get camera rectangle :
            t_min, t_max = xvec.min(), xvec.max()
            d_min, d_max = 0.9 * raw[np.nonzero(raw)].min(), 1.01 * raw.max()
            self.rect = (t_min, d_min, t_max - t_min, d_max - d_min)
            # Update object :
            self._hist.update()
        elif form == 'tf':  # time-frequency map
            self._tf.set_data(_data, self._sf, cmap=cmap, contrast=.5,
                              norm=norm, baseline=baseline, n_window=window,
                              overlap=overlap, window='hanning', clim=clim)
            self._tf.interpolation = interpolation
            self.rect = self._tf.rect

        # Hide non form elements :
        self._visibility()

        # Update annotations :
        self.update_annotations(str(self))

    def update_annotations(self, name):
        """Update annotations."""
        is_annotated = self.is_event_annotated(name)
        if is_annotated:
            c = self.get_event_coord(name)
            z = np.full((c.shape[0],), -10.)
            c = np.c_[c, z].astype(np.float32)
            msize = self._annot_mark._data['a_size'][0]
            mcolor = self._annot_mark._data['a_bg_color'][0, :]
            self._annot_mark.set_data(c, face_color=mcolor, edge_width=0.,
                                      size=msize)
        self._annot_mark.visible = is_annotated
        self._annot_text.visible = is_annotated

    def clean_annotations(self):
        """Clean annotations."""
        self._annot_mark.set_data(pos=np.random.rand(2, 2))
        self._annotations = {}
        self._annotations_txt = {}

    def _get_signal_index(self, signal):
        """Get index of a signal.

        This method turn a '(k, n, :)' string into an index used by the
        instance _navidx.
        """
        # Process signal :
        signal = signal.replace(', :', '').replace(':, ', '')[1:-1]
        # Find index :
        idx = tuple(int(k) for k in signal.split(', '))
        return self._navidx.index(idx)

    def _visibility(self):
        self._line.visible = self.form in ['line', 'psd', 'butterfly']
        self._mark.visible = self.form == 'marker'
        self._hist.visible = self.form == 'histogram'
        self._tf.visible = self.form == 'tf'


class Visuals(object):
    """Create visual objects for th grid and the signal."""

    def __init__(self, data, time, sf, axis, grid_titles, grid_color,
                 grid_shape, grid_parent, signal_parent):
        """Init."""
        # ========================== CHECK ==========================
        # ----------- AXIS -----------
        if (np.sign(axis) == 1) and (axis > data.ndim - 1):
            raise ValueError("The axis parameter can not be bigger than the "
                             "number of dimensions of the data.")
        axis = data.ndim - 1 if axis == -1 else axis
        # ----------- TIME -----------
        if time is None:
            time = np.arange(data.shape[axis]) / sf
        if (time.ndim > 1 and len(time)) > data.shape[axis]:
            raise ValueError("The length of the time vector must be the same "
                             "as the one specified by axis (" + str(axis
                                                                    ) + ")")

        # ========================== GRID ==========================
        if self._enable_grid:  # don't create grid for 1-D signals
            self._grid = GridSignal(data, axis=axis, sf=sf, title=grid_titles,
                                    color=grid_color, force_shape=grid_shape,
                                    parent=grid_parent)
            self._grid._txt.parent = grid_parent

        # ========================== SIGNAL ==========================
        self._signal = SignalVisual(time, sf, data.shape, axis,
                                    parent=signal_parent)
