import numpy as np
import vispy
import sys

from visbrain.objects import SourceObj, CombineSources, SceneObj, TimeSeriesObj, PictureObj

# c = VisbrainCanvas(show=True, )
# c.camera = 'turntable'

s1 = SourceObj('Source1', np.random.rand(100, 3), symbol='disc', color='red', radius_min=30)
s2 = SourceObj('Source2', np.random.rand(100, 3), symbol='x', color='blue', radius_min=30)
s3 = SourceObj('Source3', np.random.rand(100, 3), symbol='arrow', color='green', radius_min=30)

# ts = TimeSeriesObj('ts', np.random.rand(10, 100), np.random.rand(10, 3), color='black')

data = np.random.rand(10, 100, 200)
xyz = np.random.rand(10, 3)
p = PictureObj('Pic', data, xyz)
p.width = 100
# ts.preview()
p.preview()

# p = PictureObj()

# sc = SceneObj()
# sc.add_to_subplot(s1, 0, 0)
# sc.add_to_subplot(ts, 0, 0)

# sc.add_to_subplot(s2, 0, 1)
# sc.add_to_subplot(s3, 0, 2)

# s = CombineSources([s1, s2, s3])
# print(s.analyse_sources())
# sc = SceneObj()
# sc.add_to_subplot(s, 0, 0)

# meshdata = vispy.geometry.create_sphere(100, 100)
# v = meshdata.get_vertices()
# mesh = vispy.scene.visuals.Mesh(meshdata=meshdata, parent=c.wc.scene, color=(.3, .3, .3, .8))
# mesh.set_gl_state('translucent', depth_test=False, cull_face=False)

# s.set_visible_sources(v, 'close', .1)
# s.fit_to_vertices(v)
# print(s.xyz.shape, s._xyz.shape)

if sys.flags.interactive != 1:
    vispy.app.run()