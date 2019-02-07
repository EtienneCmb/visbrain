"""
Region Of Interest object (RoiObj) : complete tutorial
======================================================

This example illustrate the main functionalities and inputs of the roi
object i.e :

  * Use either the Brodmann, AAL, Talairach or MIST atlases and select ROI
  * Color control of ROI
  * Analyse source's anatomical location using an RoiObj
  * Project source's activity onto ROI
  * Define a custom ROI object

List of supported ROI atlases :

  * Brodmann areas
  * AAL (Automated Anatomical Labeling)
  * Talairach
  * `MIST <https://mniopenresearch.org/articles/1-3/v1>`_ includes multiple
    resolutions that can be explored
    `here <https://simexp.github.io/multiscale_dashboard/index.html?tour=1>`_.
    Inside visbrain, supported levels are 7, 12, 20, 36, 64, 122 and ROI.

.. warning::
    ROI atlases are stored inside NumPy files that are downloaded when needed.
    Every ROI files is downloaded to the ~/visbrain_data/roi folder
"""
import numpy as np

from visbrain.objects import RoiObj, ColorbarObj, SceneObj, SourceObj, BrainObj
from visbrain.io import download_file, path_to_visbrain_data, read_nifti

###############################################################################
# Download data
###############################################################################
# In order to work, this example need to download some data i.e coordinates of
# intracranial sources and a parcellates atlas (MIST) to illustrate how to
# define your own RoiObj

# Get the path to the ~/visbrain_data/example_data folder
vb_path = path_to_visbrain_data(folder='example_data')
# Download (x, y, z) coordinates of intracranial sources
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
xyz, subjects = mat['xyz'], mat['subjects']
data = np.random.uniform(low=-1., high=1., size=(xyz.shape[0],))
# Download the MIST parcellates
download_file('MIST_ROI.zip', unzip=True, astype='example_data')

###############################################################################
# Scene creation
###############################################################################
# First, we need to create the scene that will host objects

# Scene creation with a dark background and a custom size
sc = SceneObj(size=(1400, 1000))
# In this example, we also illustrate the use of the colorbar object. Hence, we
# centralize colorbar properties inside a dictionary
CBAR_STATE = dict(cbtxtsz=12, txtsz=10., width=.1, cbtxtsh=3.,
                  rect=(-.3, -2., 1., 4.))

###############################################################################
# Find the index of a region of interest
###############################################################################
# ROIs are defined with two variables : 1) a volume which contains integers
# and 2) a vector of labels which link every integer inside the volume with a
# label (for example, with the brodmann atlas, the index 4 refers to the label
# brodmann 4). Here, we illustrate how to find the index of a region of
# interest

#####################################
# **Method 1 :** export all ROI labels and indices in an excel file
#
# This first method load a ROI atlas then, we use the
# :class:`visbrain.objects.RoiObj.get_labels` method to save every related ROI
# informations in an excel file. This first method implies that you manually
# inspect in this file the index of the ROI that you're looking for.

roi_to_find1 = RoiObj('brodmann')             # Use Brodmann areas
ref_brod = roi_to_find1.get_labels(vb_path)   # Save Brodmann
roi_to_find1('aal')                           # Switch to AAL
ref_aal = roi_to_find1.get_labels(vb_path)    # Save AAL
roi_to_find1('talairach')                     # Switch to Talairach
# ref_tal = roi_to_find1.get_labels(vb_path)    # Save Talairach

#####################################
# **Method 2 :** explicitly search where is the ROI that you're looking for
#
# Here, we use the :class:`visbrain.objects.RoiObj.where_is` method of the ROI
# object to explicitly search string patterns

# Method 2 : use the `where_is` method
roi_to_find1('brodmann')                      # Switch to Brodmann
idx_ba6 = roi_to_find1.where_is('BA6')        # Find only BA6
print(ref_brod.loc[idx_ba6])
roi_to_find1('aal')                           # Switch to AAL
idx_sma = roi_to_find1.where_is('Supp Motor Area')

###############################################################################
# Extract the mesh of an ROI
###############################################################################
# Once you have the index of the ROI that you want to plot, use the
# :class:`visbrain.objects.RoiObj.select_roi` method to extract the mesh (i.e
# vertices and faces) of the ROI. Here, we illustrate this question with the
# brodmann 6 ROI

# Load the brodmann 6 atlas, get the index of BA6 and extract the mesh
roi_brod = RoiObj('brodmann')
idx_ba6 = roi_brod.where_is('BA6')
roi_brod.select_roi(select=idx_ba6)
# Define a brain object and add this brain and ROI objects to the scene
b_obj = BrainObj('B1')
sc.add_to_subplot(b_obj, row=0, col=0, use_this_cam=True,
                  title='Brodmann area 6 mesh')
sc.add_to_subplot(roi_brod, row=0, col=0)

###############################################################################
# Set a unique color per ROI mesh
###############################################################################
# If you need, you can set a unique color per plotted ROI mesh. Here, we plot
# the left and right insula and thalamus and set a unique color to each

# Load the AAL atlas
roi_aal = RoiObj('aal')
# Select indicies 29, 30, 77 and 78 (respectively insula left, right and
# thalamus left and right)
roi_aal.select_roi(select=[29, 30, 77, 78], unique_color=True, smooth=11)
# Add the ROI to the scene
sc.add_to_subplot(roi_aal, row=0, col=1, rotate='top', zoom=.4,
                  title='Select and plot multiple ROI with unique colors')

###############################################################################
# Project source's data onto the surface of ROI mesh
###############################################################################
# Once you've extract the mesh of the ROI, you can explicitly specify to the
# :class:`visbrain.object.SourceObj.project_sources` to project the activity
# onto the surface of the ROI. Here, we extract the mesh of the default mode
# network (DMN) and project source's activity on it

# Define the roi object using the MIST at resolution 7
roi_dmn = RoiObj('mist_7')
roi_dmn.get_labels(save_to_path=vb_path)  # save the labels
dmn_idx = roi_dmn.where_is('Default mode network')
roi_dmn.select_roi(select=dmn_idx)
# Define the source object and project source's data on the DMN
s_dmn = SourceObj('SecondSources', xyz, data=data)
s_dmn.project_sources(roi_dmn, cmap='plasma', clim=(-1., 1.), vmin=-.5,
                      vmax=.7, under='gray', over='red')
# Get the colorbar of the projection
cb_dmn = ColorbarObj(s_dmn, cblabel='Source activity', **CBAR_STATE)
# Add those objects to the scene
sc.add_to_subplot(roi_dmn, row=0, col=2, rotate='top', zoom=.4,
                  title="Project source's activity onto the DMN")
sc.add_to_subplot(cb_dmn, row=0, col=3, width_max=200)


###############################################################################
# Get anatomical informations of sources
###############################################################################
# If you defined sources (like intracranial recording sites, MEG source
# reconstruction...) you can use the SourceObj to defined those sources and
# then, the RoiObj to identify where are those sources located using the ROI
# volume. Here, we use the MIST at the `ROI` resolution to identify where are
# located those sources

# Define the MIST object at the ROI level
roi_mist = RoiObj('mist_ROI')
# roi_mist.get_labels(save_to_path=vb_path)  # save the labels
# Define the source object and analyse those sources using the MIST
s_obj = SourceObj('anat', xyz, data=data)
analysis = s_obj.analyse_sources(roi_mist)
# print(analysis)  # anatomical informations are included in a dataframe
# Color those sources according to the anatomical informations
s_obj.color_sources(analysis=analysis, color_by='name_ROI')
# Add the source object to the scene
sc.add_to_subplot(s_obj, row=1, col=0, rotate='top', zoom=.6,
                  title='Get anatomical informations of sources')

###############################################################################
# .. note::
#     In the example above, we analyse sources using only one ROI object. But
#     you can also combine anatomical informations that come from several
#     ROI. For example, if you want to analyse your sources using brodmann
#     areas, AAL and MIST at level 7 :
#
#         brod_roi = RoiObj('brodmann')
#
#         brod_aal = RoiObj('aal')
#
#         brod_mist = RoiObj('mist_7')
#
#         s_obj.analyse_sources([brod_roi, brod_aal, brod_mist])

###############################################################################
# Select sources that are inside an ROI
###############################################################################
# Here, we illustrate how to only select sources that are inside the
# somatomotor network.

# Define the roi MIST object at level 7
somato_str = 'Somatomotor network'
roi_somato = RoiObj('mist_7')
idx_somato = roi_somato.where_is(somato_str)
roi_somato.select_roi(idx_somato, translucent=True)
# Define the source object and analyse anatomical informations
s_somato = SourceObj('somato', xyz, data=data)
analysis = s_somato.analyse_sources(roi_somato, keep_only=somato_str)
s_somato.color_sources(data=data, cmap='bwr')
# Add those objects to the scene
sc.add_to_subplot(roi_somato, row=1, col=1, use_this_cam=True, rotate='top',
                  title='Display only sources inside the\nsomatomotor network',
                  zoom=.6)
sc.add_to_subplot(s_somato, row=1, col=1)

###############################################################################
# Define and use your own region of interest
###############################################################################
# Visbrain comes with several ROI volumes, but you can define your own ROI
# object. To do this, you need a volume (i.e an array with three dimensions)
# and an array of labels. Here, for the sake of illustration, we explain how
# to rebuild the MIST at the ROI resolution.

# Download the MIST_ROI.zip archive. See the README inside the archive
nifti_file = path_to_visbrain_data(file='MIST_ROI.nii.gz',
                                   folder='example_data')
csv_file = path_to_visbrain_data(file='MIST_ROI.csv', folder='example_data')
# Read the .csv file :
arr = np.genfromtxt(csv_file, delimiter=';', dtype=str)
# Get column names, labels and index :
column_names = arr[0, :]
arr = np.delete(arr, 0, 0)
n_roi = arr.shape[0]
roi_index = arr[:, 0].astype(int)
roi_labels = arr[:, [1, 2]].astype(object)
# Build the struct array :
label = np.zeros(n_roi, dtype=[('label', object), ('name', object)])
label['label'] = roi_labels[:, 0]
label['name'] = roi_labels[:, 1]
# Get the volume and the hdr transformation :
vol, _, hdr = read_nifti(nifti_file, hdr_as_array=True)
# Define the ROI object and save it :
roi_custom = RoiObj('custom_roi', vol=vol, labels=label, index=roi_index,
                    hdr=hdr)
# Find thalamus entries :
idx_thalamus = roi_custom.where_is('THALAMUS')
colors = {55: 'slateblue', 56: 'olive', 63: 'darkred', 64: '#ab4642'}
roi_custom.select_roi(idx_thalamus, roi_to_color=colors)
sc.add_to_subplot(roi_custom, row=1, col=2, zoom=.5,
                  title='Plot dorsal and ventral thalamus with fixed colors')

###############################################################################
# .. note::
#     Once your RoiObj is defined, you can save it using
#     :class:`visbrain.objects.RoiObj.save`. Once the object is saved, you can
#     reload it using the name you've used (here we've used the `custom_roi`
#     name which means that you can reload it later using RoiObj('custom_roi'))

# Finally, display the scene
sc.preview()
