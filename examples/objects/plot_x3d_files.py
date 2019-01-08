"""
Plot x3d files
==============

This example illustrate how to plot .x3d files. 6 brain templates are going to
be downloaded (total of 26.3Mo). Additional templates can be downloaded from :
https://scalablebrainatlas.incf.org
"""
from visbrain.objects import BrainObj, SceneObj
from visbrain.io import download_file


sc = SceneObj(size=(1500, 800))


###############################################################################
# Ferret brain
###############################################################################
# Hutchinson EB, Schwerin SC, Radomski KL, Sadeghi N, Jenkins J, Komlosh ME,
# Irfanoglu MO, Juliano SL, Pierpaoli C (2017) "Population based MRI and DTI
# templates of the adult ferret brain and tools for voxelwise analysis"
# Neuroimage 152:575–589. [doi 10.1016/j.neuroimage.2017.03.009]

ferret_file = download_file('ferret.x3d', astype='example_data')
b_ferret_obj = BrainObj(ferret_file, translucent=False)
sc.add_to_subplot(b_ferret_obj, title='Ferret brain (Hutchinson et al. 2017)')


###############################################################################
# Macaque brain (1)
###############################################################################
# Markov NT, Ercsey-Ravasz MM, Ribeiro Gomes AR, Lamy C, Magrou L, Vezoli J,
# Misery P, Falchier A, Quilodran R, Gariel MA, Sallet J, Gamanut R,
# Huissoud C, Clavagnier S, Giroud P, Sappey-Marinier D, Barone P, Dehay C,
# Toroczkai Z, Knoblauch K, Van Essen DC, Kennedy H (2014) "A weighted and
# directed interareal connectivity matrix for macaque cerebral cortex." Cereb
# Cortex 24(1):17-36. [doi 10.1093/cercor/bhs270]

macaque_file_1 = download_file('macaque_1.x3d', astype='example_data')
b_macaque_obj_1 = BrainObj(macaque_file_1, translucent=False)
sc.add_to_subplot(b_macaque_obj_1, col=1,
                  title='Macaque brain (Markov et al. 2014)')

###############################################################################
# Macaque brain (2)
###############################################################################
# [1] Dubach MF, Bowden DM (2009) "BrainInfo online 3D macaque brain atlas: a
# database in the shape of a brain" Society for Neuroscience Annual Meeting,
# Chicago, IL Abstract No. 199.5.
# [2] Rohlfing T, Kroenke CD, Sullivan EV, Dubach MF, Bowden DM, Grant KA,
# Pfefferbaum A (2012) "The INIA19 Template and NeuroMaps Atlas for Primate
# Brain Image Parcellation and Spatial Normalization." Frontiers in
# Neuroinformatics 6:27. [doi 10.3389/fninf.2012.00027]

macaque_file_2 = download_file('macaque_2.x3d', astype='example_data')
b_macaque_obj_2 = BrainObj(macaque_file_2, translucent=False)
sc.add_to_subplot(b_macaque_obj_2, col=2,
                  title="Macaque brain (Dubach et al. 2014),\n(Rohlfing et al."
                  " 2012)")

###############################################################################
# Mouse brain
###############################################################################
# Lein ES, Hawrylycz MJ, Ao N, et al. (2007) "Genome-wide atlas of gene
# expression in the adult mouse brain." Nature 445(7124):168-76.
# [doi 10.1038/nature05453]

mouse_file = download_file('mouse.x3d', astype='example_data')
b_mouse_obj = BrainObj(mouse_file, translucent=False)
sc.add_to_subplot(b_mouse_obj, row=1, title='Mouse brain (Lein et al. 2007)')

###############################################################################
# Rat brain
###############################################################################
# [1] Papp EA, Leergaard TB, Calabrese E, Johnson GA, Bjaalie JG (2014)
# "Waxholm Space atlas of the Sprague Dawley rat brain" NeuroImage 97:374-386.
# [doi 10.1016/j.neuroimage.2014.04.001]
# [2] Kjonigsen LJ, Lillehaug S, Bjaalie JG, Witter MP, Leergaard TB (2015)
# "Waxholm Space atlas of the rat brain hippocampal region: Three-dimensional
# delineations based on magnetic resonance and diffusion tensor imaging."
# NeuroImage 108:441–449. [doi 10.1016/j.neuroimage.2014.12.080]
# [3] Sergejeva M, Papp EA, Bakker R, Gaudnek MA, Okamura-Oho Y, Boline J,
# Bjaalie JG, Hess A (2015) "Anatomical landmarks for registration of
# experimental image data to volumetric rodent brain atlasing templates."
# Journal of Neuroscience Methods 240:161-169.
# [doi 10.1016/j.jneumeth.2014.11.005]

rat_file = download_file('rat.x3d', astype='example_data')
b_rat_obj = BrainObj(rat_file, translucent=False)
sc.add_to_subplot(b_rat_obj, row=1, col=1, zoom=.9,
                  title="Rat brain (Papp et al. 2014),\n(Kjonigsen et al. "
                  "2015), (Sergejeva et al. 2015)")

###############################################################################
# Human brain
###############################################################################
# [1] Makris N, Goldstein JM, Kennedy D, Hodge SM, Caviness VS, Faraone SV,
# Tsuang MT, Seidman LJ (2006) "Decreased volume of left and total anterior
# insular lobule in schizophrenia." Schizophr Res. 83(2-3):155-171.
# [doi 10.1016/j.schres.2005.11.020]
# [2] Frazier JA, Chiu S, Breeze JL, Makris N, Lange N, Kennedy DN, Herbert MR,
# Bent EK, Koneru VK, Dieterich ME, Hodge SM, Rauch SL, Grant PE, Cohen BM,
# Seidman LJ, Caviness VS, Biederman J (2005) "Structural brain magnetic
# resonance imaging of limbic and thalamic volumes in pediatric bipolar
# disorder." Am J Psychiatry 162(7):1256-1265
# [3] Desikan RS, Ségonne F, Fischl B, Quinn BT, Dickerson BC, Blacker D,
# Buckner RL, Dale AM, Maguire RP, Hyman BT, Albert MS, Killiany RJ (2006)
# "An automated labeling system for subdividing the human cerebral cortex on
# MRI scans into gyral based regions of interest." Neuroimage 31(3):968-980
# [4] Goldstein JM, Seidman LJ, Makris N, Ahern T, O'Brien LM, Caviness VS Jr,
# Kennedy DN, Faraone SV, Tsuang MT (2007) "Hypothalamic abnormalities in
# schizophrenia: sex effects and genetic vulnerability." Biol Psychiatry
# 61(8):935-945

human_file = download_file('human.x3d', astype='example_data')
b_human_obj = BrainObj(human_file, translucent=False)
sc.add_to_subplot(b_human_obj, row=1, col=2, zoom=.9,
                  title="Human brain (Makris et al. 2006), (Frazier et al. "
                  "2005),\n(Desikan et al. 2006), (Goldstein et al. 2007)")

sc.preview()
