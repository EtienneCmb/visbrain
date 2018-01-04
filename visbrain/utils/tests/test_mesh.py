"""Test functions in mesh.py."""
import numpy as np

from visbrain.utils.mesh import (convert_meshdata, vispy_array, volume_to_mesh,
                                 mesh_edges, smoothing_matrix,
                                 laplacian_smoothing)


class TestMesh(object):
    """Test functions in mesh.py."""

    def _creation(self):
        """Create vertices, faces and normals."""
        # Define random
        self.vertices = np.array([[0., 1., 0.],
                                  [0., 2., 0.],
                                  [0., 3., 1.],
                                  [1., 4., 0.]])
        self.normals = np.array([[-1., 1., 2.],
                                 [-1., 1., 2.],
                                 [-2., -3., -1.],
                                 [-4., -5., -4.]])
        self.faces = np.array([[0, 1, 2], [0, 1, 3], [1, 2, 3]])
        self.template = 'TestTemplate.npz'

    def test_vispy_array(self):
        """Test vispy_array function."""
        mat = np.random.randint(0, 10, (10, 30))
        mat_convert = vispy_array(mat, np.float64)
        assert mat_convert.flags['C_CONTIGUOUS']
        assert mat_convert.dtype == np.float64

    def test_convert_meshdata(self):
        """Test convert_meshdata function."""
        from vispy.geometry import MeshData
        import vispy.visuals.transforms as vist
        # Force creation of vertices, faces and normals :
        self._creation()
        tup = (self.vertices, self.faces)
        # Compare (vertices + faces) Vs. MeshData :
        mesh1 = convert_meshdata(*tup)
        mesh2 = convert_meshdata(meshdata=MeshData(*tup))
        assert np.array_equal(mesh1[0], mesh2[0])
        assert np.array_equal(mesh1[1], mesh2[1])
        assert np.array_equal(mesh1[2], mesh2[2])
        # Invert normals :
        inv1 = convert_meshdata(*tup, invert_normals=True)[-1]
        assert np.array_equal(inv1, -mesh1[-1])
        # Create transformation :
        tr = vist.MatrixTransform()
        tr.rotate(90, (0, 0, 1))
        convert_meshdata(*tup, transform=tr)[-1]

    def test_volume_to_mesh(self):
        """Test function volume_to_mesh."""
        x = np.random.rand(10, 20, 30)
        volume_to_mesh(x)

    def test_mesh_edges(self):
        """Test function mesh_edges."""
        self._creation()
        mesh_edges(self.faces)

    def test_smoothing_matrix(self):
        """Test function smoothing_matrix."""
        self._creation()
        vertices = np.array([1, 3])
        smoothing_matrix(vertices, mesh_edges(self.faces))

    def test_laplacian_smoothing(self):
        """Test function laplacian_smoothing."""
        self._creation()
        laplacian_smoothing(self.vertices, self.faces)
        laplacian_smoothing(self.vertices, self.faces, n_neighbors=3)
