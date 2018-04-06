"""Plot a forward solution.

Annalisa Pascarella
"""
import numpy as np
import logging
import os

from ..io import is_mne_installed

logger = logging.getLogger('visbrain')

__all__ = ['mne_plot_source_estimation']


def mne_plot_source_estimation(sbj, sbj_dir, fwd_file, stc_file=None,
                               hemisphere='both', parc='aparc',
                               kw_brain_obj={}, kw_source_obj={},
                               kw_activation={}, show=True):
    """Plot source estimation.

    Parameters
    ----------
    sbj : string
        The subject name.
    sbj_dir : string
        Path to the subject directory.
    fwd_file : string
        The file name of the forward solution, which should end with -fwd.fif
        or -fwd.fif.gz.
    stc_file : string | None
        Path to the *.stc inverse solution file.
    hemisphere : {'left', 'both', 'right'}
        The hemisphere to plot.
    parc : string | 'aparc'
        The parcellation to use, e.g., ‘aparc’ or ‘aparc.a2009s’.
    kw_brain_obj : dict | {}
        Additional inputs to pass to the `BrainObj` class.
    kw_source_obj : dict | {}
        Additional inputs to pass to the `SourceObj` class.
    kw_activation : dict | {}
        Additional inputs to pass to the `BrainObj.add_activation` method.
    show : bool | False
        If True, the window of the `Brain` module is automatically displayed.
        If False, a BrainObj and a SourceObj are returned. Finally, if 'scene'
        a SceneObj is returned.

    Returns
    -------
    b_obj : BrainObj
        A predefined `BrainObj` (if `show=False`)
    s_obj : SourceObj
        A predefined `SourceObj` (if `show=False`)
    """
    # Test that mne is installed and import :
    is_mne_installed(raise_error=True)
    import mne
    from mne.transforms import apply_trans, invert_transform
    from mne.source_space import _read_talxfm
    hemi_idx = {'left': [0], 'right': [1], 'both': [0, 1]}[hemisphere]
    # Read the forward solution :
    fwd = mne.read_forward_solution(fwd_file)
    logger.debug('Read the forward solution')
    # Get source space :
    fwd_src = fwd['src']
    # Get the MRI (surface RAS)-> head matrix
    mri_head_t = fwd['mri_head_t']
    head_mri_t = invert_transform(mri_head_t)  # head -> MRI (surface RAS)
    # Take point locations in MRI space and convert to MNI coordinates :
    trans = _read_talxfm(sbj, sbj_dir)['trans']
    mesh, sources, fact = [], [], 1000
    for hemi in hemi_idx:
        # Transform vertices :
        _mesh_mri = apply_trans(head_mri_t, fwd_src[hemi]['rr'])
        _mesh_mni = apply_trans(trans, _mesh_mri * fact)
        mesh.append(_mesh_mni)
        # Transform sources :
        _src = fwd_src[hemi]['rr'][fwd_src[hemi]['vertno']]
        _src_space_mri_ras = apply_trans(head_mri_t, _src)
        _src_space_coo_mni = apply_trans(trans, _src_space_mri_ras * fact)
        sources.append(_src_space_coo_mni)
    # Add data to the mesh :
    if isinstance(stc_file, str) and os.path.isfile(stc_file):
        # Get active data :
        data = mne.read_source_estimate(stc_file).data
        n_tp = 12
        active_data = np.abs(data[:, n_tp] / data[:, n_tp].max())
        # fwd_src contains the source spaces, the first 2 are the cortex
        # (left and right hemi, the others are related to the substructures)
        if len(hemi_idx) == 1:
            active_vert = fwd_src[hemi_idx[0]]['vertno']
        else:
            active_left = fwd_src[0]['vertno']
            active_right = fwd_src[1]['vertno'] + mesh[0].shape[0]
            active_vert = np.r_[active_left, active_right]
    else:
        active_data = active_vert = None
    # Concatenate vertices, faces and sources :
    vertices = np.concatenate(mesh)
    sources = np.concatenate(sources)
    # Get faces :
    if len(hemi_idx) == 1:
        faces = fwd_src[hemi_idx[0]]['tris']
    else:
        _faces_l = fwd_src[0]['tris']
        _faces_r = fwd_src[1]['tris'] + _faces_l.max() + 1
        faces = np.r_[_faces_l, _faces_r].astype(int)
    # Define a brain object and a source object :
    logger.info('Define a Brain and Source objects')
    from visbrain.objects import BrainObj, SourceObj, SceneObj
    b_obj = BrainObj(sbj + '_brain', vertices=vertices, faces=faces,
                     **kw_brain_obj)
    s_obj = SourceObj(sbj + '_src', sources, **kw_source_obj)
    s_obj.visible = False
    # Add data to the BrainObj if needed :
    if isinstance(active_data, np.ndarray):
        logger.info("Add active data between "
                    "[%2f, %2f]" % (active_data.min(), active_data.max()))
        b_obj.add_activation(data=active_data, vertices=active_vert,
                             **kw_activation)
    # Return either a scene or a BrainObj and SourceObj :
    if show:  # Display inside the Brain GUI
        from visbrain import Brain
        Brain(brain_obj=b_obj, source_obj=s_obj).show()
    elif show is 'scene':  # return a SceneObj
        logger.info('Define a unique scene for the Brain and Source objects')
        sc = SceneObj()
        sc.add_to_subplot(s_obj)
        sc.add_to_subplot(b_obj, use_this_cam=True)
        return sc
    else:  # return the BrainObj and SourceObj
        return b_obj, s_obj
