"""
Brain object (BrainObj) : complete tutorial
===========================================

This example illustrate the main functionalities and inputs of the brain
object i.e :

  * Use included MNI brain template
  * Select the hemisphere ('both', 'left', 'right')
  * Use a translucent or opaque brain
  * Project source's activity on the surface of the brain
  * Parcellize the brain and send data to selected parcellates
  * Add fMRI activation and MEG inverse solution

Data for fMRI activations and MEG inverse solutoin comes from the PySurfer
software (https://github.com/nipy/PySurfer/). Parcellation file comes from
MNE-Python (https://github.com/mne-tools/mne-python).
"""
import numpy as np

from visbrain.objects import BrainObj, ColorbarObj, SceneObj, SourceObj
from visbrain.io import download_file, read_stc

###############################################################################
# Scene creation
###############################################################################
# The SceneObj is Matplotlib subplot like in which, you can add visbrain's
# objects. We first create the scene with a black background, a fixed size

# Scene creation
sc = SceneObj(bgcolor='black', size=(1400, 1000))
# Colorbar default arguments. See `visbrain.objects.ColorbarObj`
CBAR_STATE = dict(cbtxtsz=12, txtsz=10., width=.1, cbtxtsh=3.,
                  rect=(-.3, -2., 1., 4.))
KW = dict(title_size=14., zoom=1.2)

###############################################################################
# .. note::
#     The BrainObj can interact with sources (SourceObj). For example, if the
#     source object represent intracranial data (e.g iEEG) those sources can
#     be projected on the surface of the brain. This is an important feature
#     because intracranial implantations is usually subject dependant and the
#     projection is a good way to plot results across subjects. To illustrate
#     this feature, we provide a set of intracranial MNI coordinates.

# Download iEEG coordinates and define some random data
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
xyz, subjects = mat['xyz'], mat['subjects']
data = np.random.rand(xyz.shape[0])


###############################################################################
# Basic brain using MNI template
###############################################################################
# By default, Visbrain include several MNI brain templates (B1, B3, B3,
# inflated, white and shere).

# Translucent inflated BrainObj with both hemispheres displayed
b_obj_fs = BrainObj('inflated', translucent=True, hemisphere='both')
# Add the brain to the scene. Note that `row_span` means that the plot will
# occupy two rows (row 0 and 1)
sc.add_to_subplot(b_obj_fs, row=0, col=0, row_span=2,
                  title='Translucent inflated brain template', **KW)

###############################################################################
# Select the left or the right hemisphere
###############################################################################
# You can use the `hemisphere` input to select either the 'left', 'right' or
# 'both' hemispheres.

# Opaque left hemispehre of the white matter
b_obj_lw = BrainObj('white', hemisphere='left', translucent=False)
sc.add_to_subplot(b_obj_lw, row=0, col=1, rotate='right',
                  title='Left hemisphere', **KW)

###############################################################################
# Projection iEEG data on the surface of the brain
###############################################################################
# As explain above, we define a source object and project the source's activity
# on the surface of the brain

# First, define a brain object used for the projection
b_obj_proj = BrainObj('B3', hemisphere='both', translucent=False)
# Define the source object
s_obj = SourceObj('iEEG', xyz, data=data, cmap='inferno')
# Just for fun, color sources according to the data :)
s_obj.color_sources(data=data)
# Project source's activity
s_obj.project_sources(b_obj_proj, cmap='plasma')
# Finally, add the source and brain objects to the subplot
sc.add_to_subplot(s_obj, row=0, col=2, title='Project iEEG data', **KW)
sc.add_to_subplot(b_obj_proj, row=0, col=2, rotate='left', use_this_cam=True)
# Finally, add the colorbar :
cb_proj = ColorbarObj(s_obj, cblabel='Projection of niEEG data', **CBAR_STATE)
sc.add_to_subplot(cb_proj, row=0, col=3, width_max=200)

###############################################################################
# .. note::
#     Here, we used s_obj.project_sources(b_obj) to project source's activity
#     on the surface. We could also have used to b_obj.project_sources(s_obj)

###############################################################################
# Parcellize the brain
###############################################################################
# Here, we parcellize the brain (using all parcellated included in the file).
# Note that those parcellates files comes from MNE-python.

# Download the annotation file of the left hemisphere lh.aparc.a2009s.annot
path_to_file1 = download_file('lh.aparc.a2009s.annot', astype='example_data')
# Define the brain object (now you should know how to do it)
b_obj_parl = BrainObj('inflated', hemisphere='left', translucent=False)
# Print parcellates included in the file
# print(b_obj_parl.get_parcellates(path_to_file1))
# Finally, parcellize the brain and add the brain to the scene
b_obj_parl.parcellize(path_to_file1)
sc.add_to_subplot(b_obj_parl, row=1, col=1, rotate='left',
                  title='Parcellize using the Desikan Atlas', **KW)

###############################################################################
# .. note::
#     Those annotations files from MNE-python are only compatibles with the
#     inflated, white and sphere templates

###############################################################################
# Send data to parcellates
###############################################################################
# Again, we download an annotation file, but this time for the right hemisphere
# The difference with the example above, is that this time we send some data
# to some specific parcellates

# Download the annotation file of the right hemisphere rh.aparc.annot
path_to_file2 = download_file('rh.aparc.annot', astype='example_data')
# Define the brain object (again... I know, this is redundant)
b_obj_parr = BrainObj('inflated', hemisphere='right', translucent=False)
# Print parcellates included in the file
# print(b_obj_parr.get_parcellates(path_to_file2))
# From the list of printed parcellates, we only select a few of them
select_par = ['paracentral', 'precentral', 'fusiform', 'postcentral',
              'superiorparietal', 'superiortemporal', 'inferiorparietal',
              'inferiortemporal']
# Now we define some data for each parcellates (one value per pacellate)
data_par = [10., .1, 5., 7., 11., 8., 4., 6.]
# Parcellize the brain with the selected parcellates. The data range is
# between [.1, 11.]. Then, we use `vmin` and `vmax` to specify that we want
# every parcellates under vmin to be gray and every parcellates over vmax
# darkred
b_obj_parr.parcellize(path_to_file2, select=select_par, hemisphere='right',
                      cmap='viridis', data=data_par, clim=[.1, 11.], vmin=1.,
                      vmax=10, under='gray', over='darkred')
# Add the brain object to the scene
sc.add_to_subplot(b_obj_parr, row=1, col=2, rotate='right',
                  title='Send data to Desikan-Killiany parcellates', **KW)
# Get the colorbar of the brain object and add it to the scene
cb_parr = ColorbarObj(b_obj_parr, cblabel='Data to parcellates', **CBAR_STATE)
sc.add_to_subplot(cb_parr, row=1, col=3, width_max=200)

###############################################################################
# Custom brain template
###############################################################################
# All of the examples above use MNI brain templates that are included inside
# visbrain. But you can define your own brain template using vertices and faces

# Download the vertices, faces and normals
mat = np.load(download_file('Custom.npz', astype='example_data'))
vert, faces, norms = mat['vertices'], mat['faces'], mat['normals']
# By default, vertices are in millimeters so we multiply by 1000.
vert *= 1000.
# If your template represent a brain with both hemispheres, you can use the
# `lr_index` to specify which vertices belong to the left or the right
# hemisphere. Basically, `lr_index` is a boolean vector of shape (n_vertices,)
# where True reflect locatino of the left hemisphere and False, the right
# hemisphere
lr_index = vert[0, :] <= 0.
# Create the brain object and add it to the scene (this time it's a bit
# different)
b_obj_custom = BrainObj('Custom', vertices=vert, faces=faces,
                        normals=norms, translucent=False)
sc.add_to_subplot(b_obj_custom, row=2, col=0, title='Use a custom template',
                  rotate='left', **KW)

###############################################################################
# .. note::
#     If you doesn't have the normals, it's not a big deal because if no
#     normals are provided, normals are going to be computed but it's a bit
#     slower. Then, you can save your template using `BrainObj.save`. This can
#     be convenient to reload your template later.

###############################################################################
# fMRI activation
###############################################################################
# Add fMRI activations (included in a nii.gz file) to the surface. The provided
# file comes from MNE-python

# Download the lh.sig.nii.gz file
file = download_file('lh.sig.nii.gz', astype='example_data')
# Define the [...] you know
b_obj_fmri = BrainObj('inflated', translucent=False, sulcus=True)
# Add fMRI activation and hide every activation that is under 5.
b_obj_fmri.add_activation(file=file, clim=(5., 20.), hide_under=5,
                          cmap='viridis', hemisphere='left')
sc.add_to_subplot(b_obj_fmri, row=2, col=1, title='Add fMRI activation',
                  rotate='left', **KW)

###############################################################################
# MEG inverse solution
###############################################################################
# Finally, plot MEG inverse solution. The provided file comes from MNE-python

# Dowload meg_source_estimate-rh.stc file and load the data
file = read_stc(download_file('meg_source_estimate-rh.stc',
                              astype='example_data'))
# Get the data of index 2 and the vertices
data = file['data'][:, 2]
vertices = file['vertices']
# You know...
b_obj_meg = BrainObj('inflated', translucent=False, hemisphere='right',
                     sulcus=True)
# Add MEG data to the surface and hide every values under 5.
b_obj_meg.add_activation(data=data, vertices=vertices, hemisphere='right',
                         smoothing_steps=21, clim=(5., 17.), hide_under=5.,
                         cmap='plasma')
# Add the brain and the colorbar object to the scene
sc.add_to_subplot(b_obj_meg, row=2, col=2, title='MEG inverse solution',
                  rotate='right', **KW)
cb_parr = ColorbarObj(b_obj_meg, cblabel='MEG data', **CBAR_STATE)
sc.add_to_subplot(cb_parr, row=2, col=3, width_max=200)

###############################################################################
# "Fun" stuff
###############################################################################
# You can link 3D rotations of subplots which means that if you rotate one
# brain, the other linked object inherit from the same rotations. Finally, you
# can take a screenshot of the scene, without the need to open the window.
# This can be particulary convenient when scenes are included inside loops to
# automatize figure generation.

# Link the rotation of subplots (row=0, col=1) and (row=1, col=2)
# sc.link((0, 1), (1, 2))
# Screenshot of the scene
# sc.screenshot('ex_brain_obj.png', transparent=True)

sc.preview()
