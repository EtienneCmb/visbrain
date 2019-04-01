"""Load data files.

This file contain functions to load :
- Matlab (*.mat)
- Pickle (*.pickle)
- NumPy (*.npy and *.npz)
- Text (*.txt)
- CSV (*.csv)
- JSON (*.json)
"""
import os
import logging

import numpy as np

from .dependencies import is_nibabel_installed

logger = logging.getLogger('visbrain')


__all__ = ('read_mat', 'read_pickle', 'read_npy', 'read_npz', 'read_txt',
           'read_csv', 'read_json', 'read_stc', 'read_x3d', 'read_gii',
           'read_obj', 'is_freesurfer_mesh_file', 'read_freesurfer_mesh')


def read_mat(path, vars=None):
    """Read data from a Matlab (mat) file."""
    from scipy.io import loadmat
    return loadmat(path, variable_names=vars)


def read_pickle(path, vars=None):
    """Read data from a Pickle (pickle) file."""
    # np.loads? ou depuis import pickle
    pass


def read_npy(path):
    """Read data from a NumPy (npy) file."""
    return np.load(path)


def read_npz(path, vars=None):
    """Read data from a Numpy (npz) file."""
    pass


def read_txt(path):
    """Read data from a text (txt) file."""
    pass


def read_csv(path):
    """Read data from a CSV (csv) file."""
    pass


def read_json(path):
    """Read data from a JSON (json) file."""
    pass


def read_stc(path):
    """Read an STC file from the MNE package.

    STC files contain activations or source reconstructions
    obtained from EEG and MEG data.

    This function is a copy from the PySurfer package. See :
    https://github.com/nipy/PySurfer/blob/master/surfer/io.py

    Parameters
    ----------
    path : string
        Path to STC file

    Returns
    -------
    data : dict
        The STC structure. It has the following keys:
           tmin           The first time point of the data in seconds
           tstep          Time between frames in seconds
           vertices       vertex indices (0 based)
           data           The data matrix (nvert * ntime)
    """
    fid = open(path, 'rb')

    stc = dict()

    fid.seek(0, 2)  # go to end of file
    file_length = fid.tell()
    fid.seek(0, 0)  # go to beginning of file

    # read tmin in ms
    stc['tmin'] = float(np.fromfile(fid, dtype=">f4", count=1))
    stc['tmin'] /= 1000.0

    # read sampling rate in ms
    stc['tstep'] = float(np.fromfile(fid, dtype=">f4", count=1))
    stc['tstep'] /= 1000.0

    # read number of vertices/sources
    vertices_n = int(np.fromfile(fid, dtype=">u4", count=1))

    # read the source vector
    stc['vertices'] = np.fromfile(fid, dtype=">u4", count=vertices_n)

    # read the number of timepts
    data_n = int(np.fromfile(fid, dtype=">u4", count=1))

    if ((file_length / 4 - 4 - vertices_n) % (data_n * vertices_n)) != 0:
        raise ValueError('incorrect stc file size')

    # read the data matrix
    stc['data'] = np.fromfile(fid, dtype=">f4", count=vertices_n * data_n)
    stc['data'] = stc['data'].reshape([data_n, vertices_n]).T

    # close the file
    fid.close()
    return stc


def read_x3d(path):
    """Read x3d files.

    This code has been adapted from :
    https://github.com/INCF/Scalable-Brain-Atlas

    Parameters
    ----------
    path : string
        Full path to a .x3d file.

    Returns
    -------
    vertices : array_like
        Array of vertices of shape (n_vertices, 3)
    faces : array_like
        Array of faces of shape (n_faces, 3)
    """
    from lxml import etree
    import re
    logger.info('    X3D file detected')

    # Read root node :
    tree = etree.parse(path, parser=etree.ETCompatXMLParser(huge_tree=True))
    root_node = tree.getroot()

    # Get mesh faces :
    face_node = root_node.find('.//IndexedFaceSet')
    faces = re.sub('[\s,]+', ',', face_node.attrib['coordIndex'].strip())
    faces = re.sub(',-1,', '\n', faces)
    faces = re.sub(',-1$', '', faces)
    faces = np.array(faces.replace('\n', ',').split(',')).astype(int)
    faces = faces.reshape(int(faces.shape[0] / 3), 3)

    # Get mesh vertices :
    vertex_node = face_node.find('Coordinate')
    vertices = re.sub('[\s,]+', ' ', vertex_node.attrib['point'].strip())
    vertices = np.array(vertices.split(' ')[0:-1]).astype(float)
    vertices = vertices.reshape(int(vertices.shape[0] / 3), 3)

    return vertices, faces


def read_gii(path):
    """Read GIFTI files.

    Parameters
    ----------
    path : string
        Full path to a .gii file.

    Returns
    -------
    vertices : array_like
        Array of vertices of shape (n_vertices, 3)
    faces : array_like
        Array of faces of shape (n_faces, 3)
    """
    is_nibabel_installed(raise_error=True)
    import nibabel
    logger.info('    GIFTI file detected')
    arch = nibabel.load(path)
    return arch.darrays[0].data, arch.darrays[1].data


def read_obj(path):
    """Read obj files.

    Parameters
    ----------
    path : string
        Full path to a .obj file.

    Returns
    -------
    vertices : array_like
        Array of vertices of shape (n_vertices, 3)
    faces : array_like
        Array of faces of shape (n_faces, 3)

    Notes
    -----
    https://en.wikibooks.org/wiki/OpenGL_Programming/Modern_OpenGL_Tutorial_Load_OBJ
    https://www.pygame.org/wiki/OBJFileLoader
    """
    logger.info('    OBJ file detected')
    vertices, faces = [], []
    for line in open(path, "r"):
        if line.startswith('#'): continue  # noqa
        values = line.split()
        if not values: continue  # noqa
        if values[0] == 'v':
            v = map(float, values[1:4])
            vertices.append(list(v))
        elif values[0] == 'f':
            _face = []
            for v in values[1:]:
                w = v.split('/')
                _face.append(int(w[0]))
            faces.append([_face])

    vertices = np.array(vertices)
    faces = np.array(faces).squeeze() - 1
    if faces.shape[-1] == 4:  # quad index -> triangles (0 as reference)
        faces = np.r_[faces[:, [0, 1, 2]], faces[:, [0, 2, 3]]]
    return vertices, faces


def is_freesurfer_mesh_file(files):
    """Test if a file or list of files are a Freesurfer meshes.

    Parameters
    ----------
    files : str | list
        File or list of files

    Returns
    -------
    is_file : bool
        Get if it's a Freesurfer file or not
    """
    files = [files] if isinstance(files, str) else files
    extensions = ['.inflated', '.curv', '.white', '.orig', '.pial']
    def _fcn_fs_file(file):  # noqa
        is_lr = any([k in file for k in ['lh.', 'rh.']])
        is_ext = os.path.splitext(file)[1] in extensions
        return is_lr and is_ext
    return all([_fcn_fs_file(k) for k in files])


def read_freesurfer_mesh(files):
    """Read Freesurfer mesh files and.

    Parameters
    ----------
    files : str | list
        Single Freesurfer file (e.g. 'lh.inflated') or list of files
        (e.g ['rh.inflated', 'lh.inflated'])

    Returns
    -------
    vert : array_like
        Vertices of shape (n_vertices, 3)
    faces : array_like
        Faces of shape (n_faces, 3)
    lr_index : array_like
        Left / right indices of shape (n_vertices,)
    """
    is_nibabel_installed(raise_error=True)
    logger.info('Freesurfer file detected')
    import nibabel as nib
    if isinstance(files, str):  # single file
        files = [files]
    assert len(files) in [1, 2], ("One or two freesurfer files should be "
                                  "provided")
    head = [os.path.split(k)[1] for k in files]
    hemi = dict()
    for f, h in zip(files, head):
        _hemi = h.split('.')[0]
        (_vert, _faces) = nib.freesurfer.read_geometry(f)
        if _hemi == 'lh':
            _vert[:, 0] -= np.max(_vert[:, 0])
        else:
            _vert[:, 0] -= np.min(_vert[:, 0])
        hemi[_hemi] = (_vert, _faces)
    # Vertices / faces construction depend on the number of files provided
    if len(hemi) == 1:  # one file provided
        _hemi = list(hemi.keys())[0]
        (vert, faces) = list(hemi.values())[0]
        fcn = np.ones if _hemi == 'lh' else np.zeros
        lr_index = fcn((vert.shape[0],), dtype=bool)
        logger.info('    Build the %s hemisphere' % _hemi)
    else:               # left and right hemisphere are provided
        # Vertices / faces construction
        (v_l, f_l), (v_r, f_r) = hemi['lh'], hemi['rh']
        vert = np.r_[v_l, v_r]
        faces = np.r_[f_l, f_r + f_l.max() + 1]
        # Left / right construction
        l_index = np.ones((v_l.shape[0],), dtype=bool)
        r_index = np.zeros((v_l.shape[0],), dtype=bool)
        lr_index = np.r_[l_index, r_index]
        logger.info('    Build left and right hemispheres')
    return vert, faces, lr_index
