"""
Brain object
============

Default brain templates :

    * B1
    * B2
    * B3
    * Inflated (fsaverage)
    * White
    * Sphere
"""
from visbrain.objects import BrainObj, SceneObj
from visbrain.io import download_file


"""Create a scene. By default, we fix the top view of the camera
"""
cam_state = dict(azimuth=0,        # azimuth angle
                 elevation=90,     # elevation angle
                 scale_factor=180  # ~distance to the camera
                 )
sc = SceneObj(camera_state=cam_state, bgcolor=(.1, .1, .1))

"""default inflated brain template
"""
b_obj_fs = BrainObj('inflated')
sc.add_to_subplot(b_obj_fs, row=0, col=0, row_span=2,
                  title='Inflated (fsaverage) brain template')

"""Left and right hemispheres of the white template
"""
b_obj_lw = BrainObj('white', hemisphere='left', translucent=False)
sc.add_to_subplot(b_obj_lw, row=0, col=1, rotate='right',
                  title='Left hemisphere')
b_obj_rw = BrainObj('white', hemisphere='right', translucent=False)
sc.add_to_subplot(b_obj_rw, row=0, col=2, rotate='left',
                  title='Right hemisphere')

"""Parcellize the brain (using all parcellates)
"""
path_to_file1 = download_file('lh.aparc.a2009s.annot')
b_obj_parl = BrainObj('inflated', hemisphere='left', translucent=False)
# print(b_obj_parl.get_parcellates(path_to_file1))  # available parcellates
b_obj_parl.parcellize(path_to_file1)
sc.add_to_subplot(b_obj_parl, row=1, col=1, rotate='left',
                  title='Parcellize using the Desikan Atlas')

"""Send data to parcellates
"""
path_to_file2 = download_file('rh.aparc.annot')
b_obj_parr = BrainObj('inflated', hemisphere='right', translucent=False)
print(b_obj_parr.get_parcellates(path_to_file2))  # available parcellates
select_par = ['paracentral', 'precentral', 'fusiform', 'postcentral',
              'superiorparietal', 'superiortemporal', 'inferiorparietal',
              'inferiortemporal']
data_par = [10., .1, 5., 7., 11., 8., 4., 6.]
b_obj_parr.parcellize(path_to_file2, select=select_par, hemisphere='right',
                      cmap='viridis', data=data_par)
sc.add_to_subplot(b_obj_parr, row=1, col=2, rotate='right',
                  title='Send data to Desikan-Killiany parcellates')

# # Get the path to the files :
# path_to_file1 = path_to_visbrain_data(file1)
#  = path_to_visbrain_data(file2)

"""Link brain rotations
"""
sc.link((0, 1), (1, 2))
sc.link((0, 2), (1, 1))

sc.preview()
