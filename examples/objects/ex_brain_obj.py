"""
Brain object
============

This example illustrate the main functionalities and inputs of the brain
object i.e :

  * Use a default brain template
  * Select the hemisphere ('both', 'left', 'right')
  * Use a translucent or opaque brain
  * Parcellize the brain and send data to selected parcellates
  * Add fMRI activation and MEG inverse solution

List of the brain templates supported by default :

    * B1
    * B2
    * B3
    * Inflated (fsaverage)
    * White
    * Sphere

.. image:: ../../picture/picobjects/ex_brain_obj.png
"""
import numpy as np

import vispy.visuals.transforms as vist

from visbrain.objects import BrainObj, ColorbarObj, SceneObj, SourceObj
from visbrain.io import download_file, read_stc


print("-> Create a scene. By default, we fix the top view of the camera")
CAM_STATE = dict(azimuth=0,        # azimuth angle
                 elevation=90,     # elevation angle
                 )
CBAR_STATE = dict(cbtxtsz=12, txtsz=10., width=.1, cbtxtsh=3.,
                  rect=(-.3, -2., 1., 4.))
sc = SceneObj(camera_state=CAM_STATE, bgcolor=(.1, .1, .1), size=(1400, 1000))

print("\n-> Translucent inflated brain template")
b_obj_fs = BrainObj('inflated', translucent=True)
b_obj_fs.alpha = 0.03
sc.add_to_subplot(b_obj_fs, row=0, col=0, row_span=2,
                  title='Translucent inflated brain template')

print("\n-> Left and right hemispheres of the white template")
b_obj_lw = BrainObj('white', hemisphere='left', translucent=False)
sc.add_to_subplot(b_obj_lw, row=0, col=1, rotate='right',
                  title='Left hemisphere')
b_obj_rw = BrainObj('white', hemisphere='both', translucent=True)

# Define a source object and project data on the right hemisphere:
mat = np.load(download_file('xyz_sample.npz'))
xyz, subjects = mat['xyz'], mat['subjects']
data = np.random.rand(xyz.shape[0])
s_obj = SourceObj('Sources', xyz, data=data, cmap='inferno')
s_obj.color_sources(data=data)
b_obj_rw.project_sources(s_obj, cmap='viridis')
sc.add_to_subplot(s_obj, row=0, col=2)
sc.add_to_subplot(b_obj_rw, row=0, col=2, rotate='left',
                  title='Right hemisphere', use_this_cam=True)

print("\n-> Parcellize the brain (using all parcellates)")
path_to_file1 = download_file('lh.aparc.a2009s.annot')
b_obj_parl = BrainObj('inflated', hemisphere='left', translucent=False)
# print(b_obj_parl.get_parcellates(path_to_file1))  # available parcellates
b_obj_parl.parcellize(path_to_file1)
sc.add_to_subplot(b_obj_parl, row=1, col=1, rotate='left',
                  title='Parcellize using the Desikan Atlas')

print("\n-> Send data to parcellates")
path_to_file2 = download_file('rh.aparc.annot')
b_obj_parr = BrainObj('inflated', hemisphere='right', translucent=False)
# print(b_obj_parr.get_parcellates(path_to_file2))  # available parcellates
select_par = ['paracentral', 'precentral', 'fusiform', 'postcentral',
              'superiorparietal', 'superiortemporal', 'inferiorparietal',
              'inferiortemporal']
data_par = [10., .1, 5., 7., 11., 8., 4., 6.]
b_obj_parr.parcellize(path_to_file2, select=select_par, hemisphere='right',
                      cmap='inferno', data=data_par, vmin=1., vmax=10,
                      under='gray', over='darkred')
sc.add_to_subplot(b_obj_parr, row=1, col=2, rotate='right',
                  title='Send data to Desikan-Killiany parcellates')
cb_parr = ColorbarObj(b_obj_parr, cblabel='Data to parcellates', **CBAR_STATE)
sc.add_to_subplot(cb_parr, row=1, col=3, width_max=200)

print("\n-> Add a custom brain template")
mat = np.load(download_file('Custom.npz'))
vert, faces = mat['coord'], mat['tri']
z90_rotation = vist.MatrixTransform()
z90_rotation.rotate(90, (0, 0, 1))
vert = z90_rotation.map(vert)[:, 0:-1]
b_obj_custom = BrainObj('Custom', vertices=1000 * vert, faces=faces,
                        translucent=False, invert_normals=True)
sc.add_to_subplot(b_obj_custom, row=2, col=0, title='Use a custom template',
                  rotate='left')

print("\n-> fMRI activation")
file = download_file('lh.sig.nii.gz')
b_obj_fmri = BrainObj('white', translucent=False)
b_obj_fmri.add_activation(file=file, clim=(5., 20.), hide_under=5,
                          cmap='viridis', hemisphere='left')
sc.add_to_subplot(b_obj_fmri, row=2, col=1, title='Add fMRI activation',
                  rotate='left')

print("\n-> MEG inverse solution")
file = read_stc(download_file('meg_source_estimate-rh.stc'))
data = file['data'][:, 2]
vertices = file['vertices']
b_obj_meg = BrainObj('inflated', translucent=False, hemisphere='right')
b_obj_meg.add_activation(data=data, vertices=vertices, hemisphere='right',
                         smoothing_steps=5, clim=(7., 17.), hide_under=7.,
                         cmap='plasma', vmin=9, vmax=15.)
sc.add_to_subplot(b_obj_meg, row=2, col=2, title='MEG inverse solution',
                  rotate='right')
cb_parr = ColorbarObj(b_obj_meg, cblabel='MEG data', **CBAR_STATE)
sc.add_to_subplot(cb_parr, row=2, col=3, width_max=200)

"""Link brain rotations
"""
sc.link((0, 1), (1, 2))
# sc.link((0, 2), (1, 1))

"""Screenshot of the scene
"""
# sc.screenshot('ex_brain_obj.png', transparent=True)

sc.preview()
