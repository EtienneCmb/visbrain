"""Test functions in camera.py."""
import numpy as np
from vispy.scene.cameras import TurntableCamera

from visbrain.utils.cameras import (FixedCam, FIXED_CAM, rotate_turntable,
                                    merge_cameras)


class TestCamera(object):
    """Test functions in camera.py."""

    def test_fixed_camera(self):
        """Test fixed_camera function."""
        FixedCam()

    def test_rotate_turntable(self):
        """Test function rotate_turntable."""
        cam = TurntableCamera()
        xyz = [20, 40, 10]
        cs = (800, 600)
        cam_state = dict(elevation=180., azimuth=90)
        # Default views :
        for k in FIXED_CAM.keys():
            rotate_turntable(fixed=k)
            rotate_turntable(fixed=k, camera=cam, xyz=xyz)
            rotate_turntable(fixed=k, camera=cam, xyz=xyz, csize=cs,
                             camera_state=cam_state)

    def test_merge_cameras(self):
        """Test function merge_cameras."""
        cam_1 = TurntableCamera(center=(0., 0., 0.), scale_factor=100.,
                                distance=100.)
        cam_2 = TurntableCamera(center=(10., 10., 10.), scale_factor=10.,
                                distance=10.)
        cam_3 = TurntableCamera(center=(2., 20., 5.), scale_factor=20.,
                                distance=20.)
        m_cam = merge_cameras(cam_1, cam_2, cam_3)
        assert np.array_equal(m_cam.center, (4.0, 10.0, 5.0))
        assert m_cam.scale_factor == 100.
        assert m_cam.distance == 100.
