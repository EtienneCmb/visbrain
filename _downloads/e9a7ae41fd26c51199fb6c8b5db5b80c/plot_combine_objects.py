"""
Combine multiple objects
========================

This example illustrate the feasibility to combine multiple objects in the same
scene.

fMRI activations comes from the PySurfer software
(https://github.com/nipy/PySurfer/).
"""
import numpy as np

from visbrain.objects import (BrainObj, SceneObj, SourceObj, RoiObj,
                              ConnectObj, CrossSecObj, TimeSeries3DObj,
                              Picture3DObj)
from visbrain.io import download_file
from visbrain.utils import generate_eeg

# Get the path to Visbrain data and download deep sources
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
xyz, subjects = mat['xyz'], mat['subjects']
data = np.random.uniform(low=-1., high=1., size=(xyz.shape[0],))

###############################################################################
# Scene creation
###############################################################################

CAM_STATE = dict(azimuth=0,        # azimuth angle
                 elevation=90,     # elevation angle
                 )
CBAR_STATE = dict(cbtxtsz=12, txtsz=10., width=.1, cbtxtsh=3.,
                  rect=(-.3, -2., 1., 4.))
sc = SceneObj(camera_state=CAM_STATE, size=(1400, 1000))

###############################################################################
# fMRI activation
###############################################################################

file = download_file('lh.sig.nii.gz', astype='example_data')
b_obj_fmri = BrainObj('inflated', translucent=False, sulcus=True)
b_obj_fmri.add_activation(file=file, clim=(5., 20.), hide_under=5,
                          cmap='viridis', hemisphere='left')
sc.add_to_subplot(b_obj_fmri, row=0, col=0, row_span=2,
                  title='fMRI activation', rotate='top')

###############################################################################
# Region Of Interest (ROI)
###############################################################################

roi_aal = RoiObj('aal')
roi_aal.select_roi(select=[29, 30], unique_color=True, smooth=11)
sc.add_to_subplot(roi_aal, row=0, col=1, title='Region Of Interest (ROI)')
sc.add_to_subplot(BrainObj('B1'), use_this_cam=True, row=0, col=1)

###############################################################################
# Sources
###############################################################################

s_obj = SourceObj('FirstSources', xyz, data=data)
s_obj.color_sources(data=data, cmap='Spectral_r')
sc.add_to_subplot(s_obj, row=1, col=1, title='Sources')
sc.add_to_subplot(BrainObj('B3'), use_this_cam=True, row=1, col=1)

###############################################################################
# 3D Time-series
###############################################################################

ts, _ = generate_eeg(n_pts=100, n_channels=xyz.shape[0])
select = np.zeros((xyz.shape[0],), dtype=bool)
select[slice(0, 100, 10)] = True
ts_obj = TimeSeries3DObj('TS3D', ts, xyz, select=select, color='pink',
                         ts_amp=24.)
sc.add_to_subplot(ts_obj, row=0, col=2, title='3D time series')
sc.add_to_subplot(BrainObj('B2'), use_this_cam=True, row=0, col=2)

###############################################################################
# 3D Pictures
###############################################################################

pic = np.random.rand(xyz.shape[0], 20, 20)
pic_obj = Picture3DObj('PIC', pic, xyz, select=select, pic_width=21.,
                       pic_height=21., cmap='viridis')
sc.add_to_subplot(pic_obj, row=1, col=2, title='3D pictures')
sc.add_to_subplot(BrainObj('B2'), use_this_cam=True, row=1, col=2)

###############################################################################
# Connectivity
###############################################################################

arch = np.load(download_file('phase_sync_delta.npz', astype='example_data'))
nodes, edges = arch['nodes'], arch['edges']
c_count = ConnectObj('default', nodes, edges, select=edges > .7,
                     color_by='count', antialias=True, line_width=2.,
                     dynamic=(.1, 1.))
s_obj_c = SourceObj('sources', nodes, color='#ab4642', radius_min=5.)
sc.add_to_subplot(c_count, row=2, col=0, row_span=2, title='3D connectivity')
sc.add_to_subplot(s_obj_c, row=2, col=0)
sc.add_to_subplot(BrainObj('B3'), use_this_cam=True, row=2, col=0)

###############################################################################
# Cross-sections
###############################################################################

cs_brod = CrossSecObj('brodmann', interpolation='nearest',
                      coords=(70, 80, 90), cmap='viridis')
cs_brod.localize_source((-10., -15., 20.))
sc.add_to_subplot(cs_brod, row=2, col=1, col_span=2, row_span=2,
                  title='Cross-sections')


sc.preview()
