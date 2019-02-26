"""Test BrainObj."""
import numpy as np

from visbrain.objects import BrainObj, SourceObj
from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.io import read_stc, clean_tmp


NEEDED_FILES = dict(ANNOT_FILE_1='lh.aparc.annot',
                    ANNOT_FILE_2='rh.aparc.annot',
                    MEG_INVERSE='meg_source_estimate-lh.stc',
                    OVERLAY_1='lh.sig.nii.gz',
                    OVERLAY_2='lh.alt_sig.nii.gz',
                    PARCELLATES_1='lh.aparc.a2009s.annot',
                    PARCELLATES_2='rh.aparc.annot',
                    X3D_FILE='ferret.x3d',
                    GII_FILE='lh.bert.inflated.gii',
                    GII_OVERLAY='lh.bert.thickness.gii',
                    OBJ_FILE='brain.obj',
                    LH_FREESURFER='lh.inflated',
                    RH_FREESURFER='rh.inflated'
                    )

# BRAIN :
b_obj = BrainObj('B1')
n_vertices, n_faces = 100, 50
vertices_x3 = 20. * np.random.rand(n_vertices, 3, 3)
vertices = 20. * np.random.rand(n_vertices, 3)
normals = (vertices >= 0).astype(float)
faces = np.random.randint(0, n_vertices, (n_faces, 3))

# SOURCES :
xyz = np.random.uniform(-20, 20, (50, 3))
mask = xyz[:, 0] > 10
s_obj = SourceObj('xyz', xyz, mask=mask)


class TestBrainObj(_TestObjects):
    """Test BrainObj."""

    OBJ = b_obj

    def test_rotation(self):
        """Test function rotation."""
        # Test fixed rotations :
        f_rot = ['sagittal_0', 'left', 'sagittal_1', 'right', 'coronal_0',
                 'front', 'coronal_1', 'back', 'axial_0', 'top', 'axial_1',
                 'bottom']
        for k in f_rot:
            b_obj.rotate(k)
        # Test custom rotation :
        for k in [(0, 90), (170, 21), (45, 65)]:
            b_obj.rotate(custom=k)

    def test_definition(self):
        """Test function definition."""
        BrainObj('inflated', sulcus=True)
        # Test default templates :
        for k, i in zip(['B1', 'B2', 'B3'], ['left', 'both', 'right']):
            b_obj.set_data(name=k, hemisphere=i)

    def test_supported_format(self):
        """Test for input formats."""
        for k in ['X3D_FILE', 'GII_FILE', 'OBJ_FILE']:
            file = self.need_file(NEEDED_FILES[k])
            BrainObj(file)
        # Test Freesurfer files
        _lh = self.need_file(NEEDED_FILES['LH_FREESURFER'])
        _rh = self.need_file(NEEDED_FILES['RH_FREESURFER'])
        BrainObj(_lh)
        BrainObj(_rh)
        BrainObj((_lh, _rh))

    def test_custom_templates(self):
        """Test passing vertices, faces and normals."""
        BrainObj('Custom', vertices=vertices, faces=faces)
        BrainObj('Custom', vertices=vertices, faces=faces, normals=normals)

    def test_get_parcellates(self):
        """Test function get_parcellates."""
        # Prepare the brain :
        b_obj = BrainObj('inflated')
        import pandas as pd
        file_1 = self.need_file(NEEDED_FILES['ANNOT_FILE_1'])
        file_2 = self.need_file(NEEDED_FILES['ANNOT_FILE_2'])
        df_1 = b_obj.get_parcellates(file_1)
        df_2 = b_obj.get_parcellates(file_2)
        assert all([isinstance(k, pd.DataFrame) for k in [df_1, df_2]])

    def test_overlay_from_file(self):
        """Test add_activation method."""
        # Prepare the brain :
        b_obj = BrainObj('inflated')
        file_1 = self.need_file(NEEDED_FILES['OVERLAY_1'])
        file_2 = self.need_file(NEEDED_FILES['OVERLAY_2'])
        # NIFTI Overlay :
        b_obj.add_activation(file=file_1, clim=(4., 30.), hide_under=4,
                             cmap='Reds_r', hemisphere='left')
        b_obj.add_activation(file=file_2, clim=(4., 30.), hide_under=4,
                             cmap='Blues_r', hemisphere='left', n_contours=10)
        # Meg inverse :
        file_3 = read_stc(self.need_file(NEEDED_FILES['MEG_INVERSE']))
        data = file_3['data'][:, 2]
        vertices = file_3['vertices']
        b_obj.add_activation(data=data, vertices=vertices, smoothing_steps=3)
        b_obj.add_activation(data=data, vertices=vertices, smoothing_steps=5,
                             clim=(13., 22.), hide_under=13., cmap='plasma')
        # GII overlays :
        gii = self.need_file(NEEDED_FILES['GII_FILE'])
        gii_overlay = self.need_file(NEEDED_FILES['GII_OVERLAY'])
        b_gii = BrainObj(gii)
        b_gii.add_activation(file=gii_overlay)

    def test_parcellize(self):
        """Test function parcellize."""
        b_obj = BrainObj('inflated')
        file_1 = self.need_file(NEEDED_FILES['PARCELLATES_1'])
        file_2 = self.need_file(NEEDED_FILES['PARCELLATES_2'])
        b_obj.parcellize(file_1, hemisphere='left')
        select = ['insula', 'paracentral', 'precentral']
        data = np.arange(len(select))
        b_obj.parcellize(file_2, select=select, data=data, cmap='Spectral_r')

    def test_projection(self):
        """Test cortical projection and repartition."""
        b_obj.project_sources(s_obj, 'modulation')
        b_obj.project_sources(s_obj, 'repartition')

    def test_properties(self):
        """Test BrainObj properties (setter and getter)."""
        self._tested_obj = b_obj
        self.assert_and_test('translucent', True)
        self.assert_and_test('alpha', .03)
        self.assert_and_test('hemisphere', 'both')
        self.assert_and_test('scale', 1.)
        assert b_obj.camera is not None
        assert isinstance(b_obj.vertices, np.ndarray)
        # Test if getting vertices and faces depends on the selected hemisphere
        b_obj.hemisphere = 'both'
        n_vertices_both = b_obj.vertices.shape[0]
        n_faces_both = b_obj.faces.shape[0]
        n_normals_both = b_obj.normals.shape[0]
        for k in ['left', 'right']:
            b_obj.hemisphere = k
            assert b_obj.vertices.shape[0] < n_vertices_both
            assert b_obj.faces.shape[0] < n_faces_both
            assert b_obj.normals.shape[0] < n_normals_both

    def test_clean(self):
        """Test function clean."""
        b_obj.clean()

    def test_list(self):
        """Test function list."""
        assert isinstance(b_obj.list(), list)

    def test_save(self):
        """Test function save."""
        b_cust = BrainObj('Custom', vertices=vertices, faces=faces)
        b_cust.save()
        b_cust_tmp = BrainObj('CustomTmp', vertices=vertices, faces=faces)
        b_cust_tmp.save(tmpfile=True)

    def test_reload_saved_template(self):
        """Test function reload_saved_template."""
        BrainObj('Custom')
        BrainObj('CustomTmp')

    def test_remove(self):
        """Test function remove."""
        BrainObj('Custom').remove()
        clean_tmp()
