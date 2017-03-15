import numpy as np

from visbrain import vbrain

s_xyz = np.loadtxt('thalamus.txt')
s_data = np.load('Px.npy').mean(1)

vb = vbrain(s_xyz=s_xyz, s_data=s_data, s_radius=16, s_cmap='viridis')
vb.rotate(fixed='axial')
vb.area_plot(selection=[77, 78], subdivision='aal')
vb.cortical_projection(project_on='deep')
# vb.screenshot('thalamus.png', region=(1000, 300, 570, 550), colorbar=False)
vb.show()