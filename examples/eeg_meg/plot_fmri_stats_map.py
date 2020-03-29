"""
Display a volumetric fmri-stats map across the brain surface
=============================================================

This example script does the following:
  1) Download a nifti file from nilearn data set
  2) Resample it on visbrain BrainObj
  3) Plot it in a thresholded fashion

Inspired by nilearn.plotting.plot_surf_stat_map

"""

from visbrain.objects import BrainObj, ColorbarObj, SceneObj
from nilearn import datasets, surface

sc = SceneObj(bgcolor='black', size=(1000, 500))

# Colorbar default arguments
CBAR_STATE = dict(cbtxtsz=20, txtsz=20., width=.1, cbtxtsh=3.,
                  rect=(-.3, -2., 1., 4.))
KW = dict(title_size=14., zoom=1.2)

motor_images = datasets.fetch_neurovault_motor_task()
stat_img     = motor_images.images[0]
# stat_img is a nifti file: "image_10426.nii.gz"

b_obj = BrainObj('white',
                 translucent=False)

mesh  = [b_obj.vertices, b_obj.faces]

# resample from nifti to mesh
texture = surface.vol_to_surf(stat_img, mesh)

# plot mesh across brain oject
b_obj.add_activation(-1 * texture,
                     cmap='Blues_r',
                     clim=(1, 7.9),
                     vmin=1,
                     vmax=7.9,
                     hide_under=1,)

cb_proj = ColorbarObj(b_obj,
                      cblabel='stats map (-)',
                      cmap='Blues',
                      vmin=-7.9,
                      vmax=-1,
                      clim=(-7.9, -1),
                      #over='gainsboro',
                      **CBAR_STATE)

b_obj.add_activation(texture,
                     cmap='Reds_r',
                     vmin=1,
                     vmax=7.9,
                     clim=(1, 7.9),
                     hide_under=1)

cb_proj_2 = ColorbarObj(b_obj,
                      cblabel='statsmap (+)',
                      cmap='Reds_r',
                      vmin = 1,
                      vmax=7.9,
                      #under='gainsboro',
                      **CBAR_STATE)

sc.add_to_subplot(b_obj, row=0, col=0, rotate='right')

sc.add_to_subplot(cb_proj,
                  row=0, col=1,
                  width_max=200)

sc.add_to_subplot(cb_proj_2,
                  row=0, col=2,
                  width_max=200)

sc.preview()
