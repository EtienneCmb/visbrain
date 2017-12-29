"""Surfaces (mesh) and volume utility functions."""
import logging

import numpy as np
from scipy.spatial.distance import cdist

from vispy.geometry import MeshData
from vispy.geometry.isosurface import isosurface

from .sigproc import smooth_3d


__all__ = ('vispy_array', 'convert_meshdata', 'volume_to_mesh',
           'smoothing_matrix', 'mesh_edges', 'laplacian_smoothing')


logger = logging.getLogger('visbrain')


def vispy_array(data, dtype=np.float32):
    """Check and convert array to be compatible with buffers.

    Parameters
    ----------
    data : array_like
        Array of data.
    dtype : type | np.float32
        Futur type of the array.

    Returns
    -------
    data : array_like
        Contiguous array of type dtype.
    """
    if not data.flags['C_CONTIGUOUS']:
        data = np.ascontiguousarray(data, dtype=dtype)
    if data.dtype != dtype:
        data = data.astype(dtype, copy=False)
    return data


def convert_meshdata(vertices=None, faces=None, normals=None, meshdata=None,
                     invert_normals=False, transform=None):
    """Convert mesh data to be compatible with visbrain.

    Parameters
    ----------
    vertices : array_like | None
        Vertices of the template of shape (N, 3) or (N, 3, 3) if indexed by
        faces.
    faces : array_like | None
        Faces of the template of shape (M, 3)
    normals : array_like | None
        The normals to each vertex, with the same shape as vertices.
    meshdata : VisPy.MeshData | None
        VisPy MeshData object.
    invert_normals : bool | False
        If the brain appear to be black, use this parameter to invert normals.
    transform : visPy.transform | None
        VisPy transformation to apply to vertices ans normals.

    Returns
    -------
    vertices : array_like
        Vertices of shape (N, 3)
    faces : array_like
        Faces of the template of shape (M, 3)
    normals : array_like
        The normals of shape (M, 3, 3).
    """
    # Priority to meshdata :
    if meshdata is not None:
        vertices = meshdata.get_vertices()
        faces = meshdata.get_faces()
        normals = meshdata.get_vertex_normals()
        logger.debug('Indexed faces normals converted // extracted')
    else:
        # Check if faces index start at zero (Matlab like):
        if faces.min() != 0:
            faces -= faces.min()
        # Get normals if None :
        if (normals is None) or (normals.ndim != 2):
            md = MeshData(vertices=vertices, faces=faces)
            normals = md.get_vertex_normals()
            logger.debug('Indexed faces normals converted // extracted')
    assert vertices.ndim == 2

    # Invert normals :
    norm_coef = -1. if invert_normals else 1.
    normals *= norm_coef

    # Apply transformation :
    if transform is not None:
        vertices = transform.map(vertices)[..., 0:-1]
        normals = transform.map(normals)[..., 0:-1]

    # Type checking :
    vertices = vispy_array(vertices)
    faces = vispy_array(faces, np.uint32)
    normals = vispy_array(normals)

    return vertices, faces, normals


def volume_to_mesh(vol, smooth_factor=3, level=None, **kwargs):
    """Convert a volume into a mesh with vertices, faces and normals.

    Parameters
    ----------
    vol : array_like
        The volume of shape (N, M, P)
    smooth_factor : int | 3
        The smoothing factor to apply to the volume.
    level : int | None
        Level to extract.
    kwargs : dict | {}
        Optional arguments to pass to convert_meshdata.

    Returns
    -------
    vertices : array_like
        Mesh vertices.
    faces : array_like
        Mesh faces.
    normals : array_like
        Mesh normals.
    """
    # Smooth the volume :
    vol_s = smooth_3d(vol, smooth_factor)
    # Extract vertices and faces :
    if level is None:
        level = .5
    elif isinstance(level, int):
        vol_s[vol_s != level] = 0
        level = .5
    vert_n, faces_n = isosurface(vol_s, level=level)
    # Convert to meshdata :
    vertices, faces, normals = convert_meshdata(vert_n, faces_n, **kwargs)
    return vertices, faces, normals


def smoothing_matrix(vertices, adj_mat, smoothing_steps=20):
    """Create a smoothing matrix.

    This function  can be used to interpolate data defined for a subset of
    vertices onto mesh with an adjancency matrix given by adj_mat.

    This function is a copy from the PySurfer package. See :
    https://github.com/nipy/PySurfer/blob/master/surfer/utils.py

    Parameters
    ----------
    vertices : array_like
        Vertex indices of shape (N,)
    adj_mat : sparse matrix
        N x N adjacency matrix of the full mesh.
    smoothing_steps : int
        Number of smoothing steps. If smoothing_steps is None, as many
        smoothing steps are applied until the whole mesh is filled with
        with non-zeros. Only use this option if the vertices correspond to a
        subsampled version of the mesh.
    Returns
    -------
    smooth_mat : sparse matrix
        smoothing matrix with size N x len(vertices)
    """
    from scipy import sparse

    e = adj_mat.copy()
    e.data[e.data == 2] = 1
    n_vertices = e.shape[0]
    e = e + sparse.eye(n_vertices, n_vertices)
    idx_use = vertices
    smooth_mat = 1.0
    n_iter = smoothing_steps if smoothing_steps is not None else 1000
    for k in range(n_iter):
        e_use = e[:, idx_use]

        data1 = e_use * np.ones(len(idx_use))
        idx_use = np.where(data1)[0]
        scale_mat = sparse.dia_matrix((1 / data1[idx_use], 0),
                                      shape=(len(idx_use), len(idx_use)))

        smooth_mat = scale_mat * e_use[idx_use, :] * smooth_mat

        if smoothing_steps is None and len(idx_use) >= n_vertices:
            break

    # Make sure the smoothing matrix has the right number of rows
    # and is in COO format
    smooth_mat = smooth_mat.tocoo()
    smooth_mat = sparse.coo_matrix((smooth_mat.data,
                                    (idx_use[smooth_mat.row],
                                     smooth_mat.col)),
                                   shape=(n_vertices,
                                          len(vertices)))

    return smooth_mat


def mesh_edges(faces):
    """Get sparse matrix with edges as an adjacency matrix.

    This function is a copy from the PySurfer package. See :
    https://github.com/nipy/PySurfer/blob/master/surfer/utils.py

    Parameters
    ----------
    faces : array_like
        The mesh faces of shape (n_faces, 3).
    Returns
    -------
    edges : sparse matrix
        The adjacency matrix.
    """
    from scipy import sparse
    npoints = np.max(faces) + 1
    nfaces = len(faces)
    a, b, c = faces.T
    edges = sparse.coo_matrix((np.ones(nfaces), (a, b)),
                              shape=(npoints, npoints))
    edges = edges + sparse.coo_matrix((np.ones(nfaces), (b, c)),
                                      shape=(npoints, npoints))
    edges = edges + sparse.coo_matrix((np.ones(nfaces), (c, a)),
                                      shape=(npoints, npoints))
    edges = edges + edges.T
    edges = edges.tocoo()
    return edges


def laplacian_smoothing(vertices, faces, n_neighbors=-1):
    """Apply a laplacian smoothing to vertices.

    Parameters
    ----------
    vertices : array_like
        Array of vertices.
    vertices : array_like
        Array of faces.
    n_neighbors : int | -1
        Specify maximum number of closest neighbors to take into account in the
        mean.

    Returns
    -------
    new_vertices : array_like
        New smoothed vertices.
    """
    assert vertices.ndim == 2 and vertices.shape[1] == 3
    assert faces.ndim == 2 and faces.shape[1] == 3
    assert n_neighbors >= -1 and isinstance(n_neighbors, int)
    n_vertices = vertices.shape[0]
    new_vertices = np.zeros_like(vertices)
    for k in range(n_vertices):
        # Find connected vertices :
        faces_idx = np.where(faces == k)[0]
        u_faces_idx = np.unique(np.ravel(faces[faces_idx, :])).tolist()
        u_faces_idx.remove(k)
        # Select closest connected vertices :
        if n_neighbors == -1:
            to_smooth = u_faces_idx
        else:
            norms = cdist(vertices[[k], :], vertices[u_faces_idx, :]).ravel()
            n_norm = min(n_neighbors, len(norms))
            to_smooth = np.array(u_faces_idx)[np.argsort(norms)[0:n_norm]]
        # Take the mean of selected vertices :
        new_vertices[k, :] = vertices[to_smooth, :].mean(0).reshape(1, -1)
    return new_vertices
