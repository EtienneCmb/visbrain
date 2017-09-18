"""Visual object creation."""
import numpy as np
from itertools import product

from vispy import scene
import vispy.visuals.transforms as vist

from ..visuals import GridSignalMesh, TFmapsMesh
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
        pos = np.random.rand(2, 2)
        self._annot_mark = scene.visuals.Markers(pos=pos, parent=parent)
        self._annot_mark.visible = False
        # Create text for annotations :
        self._annot_text = scene.visuals.Text(parent=parent, anchor_x='left',
                                              bold=True, font_size=14.)
        tr = (self._time.max() - self._time.min()) / 100.
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
            self._annot_text.color = color2vb('#ab4642')

    def select_annotation(self, signal, coord):
        """Select an annotation."""
        # Get coord index :
        row, coord = self._get_coord_index(signal, coord)
        is_coord = (row, coord) != (None, None)
        if is_coord:
            # Set text and position to scene.visuals.Text() :
            self._annot_text.text = self._annotations_txt[signal][row]
            self._annot_text.color = color2vb('#ab4642')
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
    parent : VisPy.parent | None
        Parent of the mesh.
    """

    def __init__(self, time, sf, sh, axis, form='line', color='black', lw=2.,
                 symbol='o', size=10., nbins=10, parent=None):
        """Init."""
        self.form = form
        self._time = time
        self._sf = sf
        self._axis = axis
        self._index = 0  # selected index of the 3-d array
        self.color = color2vb(color)
        self.lw = lw
        self.nbins = nbins
        self.symbol = symbol
        self.size = size
        self.rect = (0., 0., 1., 1.)
        self._prep = PrepareData()
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
        self._th = scene.visuals.Line(pos=pos, name='threshold', width=lw,
                                      parent=parent)
        self._line = scene.visuals.Line(pos=pos, name='line', parent=parent,
                                        width=lw)
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

    def set_data(self, data, index, color=None, lw=None, nbins=None,
                 symbol=None, size=None, form='line', th=None):
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
        """
        # Update variable :
        self.form = form
        self._index = index
        self.color = color if color is not None else self.color
        self.lw = lw if lw is not None else self.lw
        self.nbins = nbins if nbins is not None else self.nbins
        self.symbol = symbol if symbol is not None else self.symbol
        self.size = size if size is not None else self.size

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
        if form in ['line', 'marker']:  # line and marker
            # Get position array :
            pos = np.c_[self._time, _data]
            # Send position :
            if form == 'line':
                # Threshold :
                is_th = isinstance(th, (tuple, list, np.ndarray))
                col = color2vb(self.color, length=len(_data))
                if is_th:
                    # Build threshold segments :
                    t_min, t_max = self._time.min(), self._time.max()
                    pos_th = np.vstack(([t_min, th[0]], [t_max, th[0]],
                                        [t_min, th[1]], [t_max, th[1]]))
                    self._th.set_data(pos_th, connect='segments',
                                      color=color2vb('#ab4642'))
                    # Build line color :
                    col = color2vb(self.color, length=len(_data))
                    cond = np.logical_or(_data < th[0], _data > th[1])
                    col[cond, :] = color2vb('#ab4642')
                self._th.visible = is_th
                self._line.set_data(pos, width=self.lw, color=col)
                self._line.update()
            else:
                self._mark.set_data(pos, face_color=self.color,
                                    symbol=self.symbol, size=self.size,
                                    edge_width=0.)
                self._mark.update()
            # Get camera rectangle :
            t_min, t_max = self._time.min(), self._time.max()
            d_min, d_max = _data.min(), _data.max()
            off = .05 * (d_max - d_min)
            self.rect = (t_min, d_min - off, t_max - t_min,
                         d_max - d_min + 2 * off)
        elif form == 'histogram':  # histogram
            # Compute the mesh :
            mesh = scene.visuals.Histogram(_data, self.nbins)
            # Get the vertices and faces of the mesh :
            vert = mesh.mesh_data.get_vertices()
            faces = mesh.mesh_data.get_faces()
            # Pass vertices and faces to the histogram :
            self._hist.set_data(vert, faces, color=color)
            # Compute the histogram :
            raw, xvec = np.histogram(_data, self.nbins)
            # Get camera rectangle :
            t_min, t_max = xvec.min(), xvec.max()
            d_min, d_max = 0.9 * raw[np.nonzero(raw)].min(), 1.01 * raw.max()
            self.rect = (t_min, d_min, t_max - t_min, d_max - d_min)
            # Update object :
            self._hist.update()
        elif form == 'tf':  # time-frequency map
            self._tf.set_data(_data, self._sf, cmap='viridis')
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
            self._annot_mark.set_data(c, face_color=color2vb('#ab4642'),
                                      edge_width=0., size=13)
        self._annot_mark.visible = is_annotated
        self._annot_text.visible = is_annotated

    def clean_annotations(self):
        """Clean annotations."""
        self._annot_mark.set_data(pos=np.random.rand(1, 2))
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
        self._line.visible = self.form == 'line'
        self._mark.visible = self.form == 'marker'
        self._hist.visible = self.form == 'histogram'
        self._tf.visible = self.form == 'tf'


class Visuals(object):
    """Create visual objects for th grid and the signal.

    Parameters
    ----------
    """

    def __init__(self, data, time, sf, axis, form, color, lw, symbol, size,
                 nbins, parent_grid, parent_signal):
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
            self._grid = GridSignalMesh(data, axis=axis, sf=sf)
            self._grid.parent = parent_grid

        # ========================== SIGNAL ==========================
        self._signal = SignalVisual(time, sf, data.shape, axis, form=form,
                                    color=color, lw=lw, symbol=symbol,
                                    size=size, nbins=nbins,
                                    parent=parent_signal)
