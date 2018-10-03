"""Plot a forward solution.

Annalisa Pascarella
"""
import numpy as np
import logging
import os

from ..io import is_mne_installed

logger = logging.getLogger('visbrain')

__all__ = ['mne_plot_source_estimation', 'mne_plot_source_space']


def _extract_arrays_from_src(src, hemisphere='both', fact=1.):
    """Get vertices, faces, active vertices and sources from SourceSpace."""
    logger.debug("Loading vert, faces, activ and sources from src structure.")
    # Define usefull variables :
    _l_nb, _r_nb = src[0]['rr'].shape[0], src[1]['rr'].shape[0]
    _f_off, _act_off = [0, src[0]['tris'].max() + 1], [0, _l_nb]
    _hemi = {'left': [0], 'right': [1], 'both': [0, 1]}[hemisphere]
    # Get vertices and faces :
    vertices = np.vstack([src[k]['rr'] for k in [0, 1]])
    faces = np.vstack([src[k]['tris'] + _f_off[k] for k in [0, 1]])
    lr_index = np.r_[np.ones((_l_nb,)), np.zeros((_r_nb))].astype(bool)
    # Get active vertex and sources :
    activ = np.hstack([src[k]['vertno'] + _act_off[k] for k in [0, 1]])
    sources = np.vstack([src[k]['rr'][src[k]['vertno']] for k in _hemi])
    return fact * vertices, faces, lr_index, activ, fact * sources


def _plt_src(name, kw_brain_obj, active_data, active_vert, sources,
             kw_source_obj, kw_activation, show):
    # Define a brain object and a source object :
    logger.info('    Define a Brain and Source objects')
    from visbrain.objects import BrainObj, SourceObj, SceneObj
    brain_obj, source_obj = name + '_brain', name + '_sources'
    b_obj = BrainObj(brain_obj, **kw_brain_obj)
    s_obj = SourceObj(source_obj, sources, **kw_source_obj)
    s_obj.visible_obj = False
    # Add data to the BrainObj if needed :
    if isinstance(active_data, np.ndarray):
        logger.info("    Add active data between "
                    "[%2f, %2f]" % (active_data.min(), active_data.max()))
        b_obj.add_activation(data=active_data, vertices=active_vert,
                             **kw_activation)
    # Return either a scene or a BrainObj and SourceObj :
    if show is True:  # Display inside the Brain GUI
        # Define a Brain instance :
        from visbrain.gui import Brain
        brain = Brain(brain_obj=b_obj, source_obj=s_obj)
        brain._brain_template.setEnabled(False)
        # By default, display colorbar if activation :
        if isinstance(active_data, np.ndarray):
            brain.menuDispCbar.setChecked(True)
            brain._fcn_menu_disp_cbar()
        brain.show()
    elif show is 'scene':  # return a SceneObj
        logger.info("    Define a unique scene for the Brain and Source "
                    "objects")
        sc = SceneObj()
        sc.add_to_subplot(s_obj)
        sc.add_to_subplot(b_obj, use_this_cam=True)
        return sc
    else:  # return the BrainObj and SourceObj
        s_obj.visible_obj = True
        return b_obj, s_obj


def mne_plot_source_estimation(sbj, sbj_dir, fwd_file, stc_file=None,
                               hemisphere='both', parc='aparc', active_data=0,
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
        Path to the .stc inverse solution file.
    hemisphere : {'left', 'both', 'right'}
        The hemisphere to plot.
    parc : string | 'aparc'
        The parcellation to use, e.g., ‘aparc’ or ‘aparc.a2009s’.
    active_data : array_like, int | 0
        The data to set to vertices. If an stc file is provided and if
        `active_data` is an integer, it describes the time instant in which you
        want to see the activation. Otherwise, `active_data` must be an array
        with the same same shape as the number of active vertices.
    kw_brain_obj : dict | {}
        Additional inputs to pass to the :class:`visbrain.objects.BrainObj`
        class.
    kw_source_obj : dict | {}
        Additional inputs to pass to the :class:`visbrain.objects.SourceObj`
        class.
    kw_activation : dict | {}
        Additional inputs to pass to the
        :class:`visbrain.objects.BrainObj.add_activation` method.
    show : bool | False
        If True, the window of the :class:`visbrain.Brain` module is
        automatically displayed. If False, a :class:`visbrain.objects.BrainObj`
        and a :class:`visbrain.objects.SourceObj` are returned. Finally, if
        'scene'a :class:`visbrain.objects.SceneObj` is returned.

    Returns
    -------
    b_obj : BrainObj
        A predefined :class:`visbrain.objects.BrainObj` (if `show=False`)
    s_obj : SourceObj
        A predefined :class:`visbrain.objects.SourceObj`, hide by default (if
        `show=False`)
    """
    # Test that mne is installed and import :
    is_mne_installed(raise_error=True)
    import mne
    from mne.source_space import head_to_mni
    # Read the forward solution :
    fwd = mne.read_forward_solution(fwd_file)
    logger.debug('Read the forward solution')
    # Get source space :
    fwd_src = fwd['src']
    # Get the MRI (surface RAS)-> head matrix
    mri_head_t = fwd['mri_head_t']
    # Extract arrays from src structure :
    (vertices, faces, lr_index, active_vert,
     sources) = _extract_arrays_from_src(fwd_src, hemisphere)
    # Head to MNI conversion
    logger.info("    Head to MNI conversion")
    vertices = head_to_mni(vertices, sbj, mri_head_t, subjects_dir=sbj_dir)
    sources = head_to_mni(sources, sbj, mri_head_t, subjects_dir=sbj_dir)
    # Add data to the mesh :
    if isinstance(active_data, np.ndarray):
        if len(active_data) != len(active_vert):
            logger.error("The length of `active data` (%i) must be the same "
                         "the length of the number of active vertices "
                         "(%i)" % (len(active_data), len(active_vert)))
            active_data = active_vert = None
        else:
            logger.info("    Array of active data used.")
    elif isinstance(stc_file, str) and isinstance(active_data, int):
        # Get active data :
        assert os.path.isfile(stc_file)
        n_tp = active_data
        data = mne.read_source_estimate(stc_file).data
        active_data = np.abs(data[:, n_tp] / data[:, n_tp].max())
        logger.info("    Time instant %i used for activation" % n_tp)
    else:
        logger.info("    No active data detected.")
        active_data = active_vert = None
    # Complete dicts :
    kw_brain_obj['vertices'], kw_brain_obj['faces'] = vertices, faces
    kw_brain_obj['lr_index'], kw_brain_obj['hemisphere'] = lr_index, hemisphere
    return _plt_src(sbj, kw_brain_obj, active_data, active_vert, sources,
                    kw_source_obj, kw_activation, show)


def mne_plot_source_space(fif_file, active_data=None, hemisphere='both',
                          kw_brain_obj={}, kw_source_obj={}, kw_activation={},
                          show=True):
    """Plot source space.

    Parameters
    ----------
    fif_file : string
        Full path to the .fif file.
    active_data : array_like | None
        The data to set to vertices.
    hemisphere : {'left', 'both', 'right'}
        The hemisphere to plot.
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
        A predefined `SourceObj`, hide by default (if `show=False`)
    """
    # Test that mne is installed and import :
    is_mne_installed(raise_error=True)
    from mne import read_source_spaces
    assert os.path.isfile(fif_file)
    src = read_source_spaces(fif_file)
    # Build vertices / faces :
    (vertices, faces, lr_index, active_vert,
     sources) = _extract_arrays_from_src(src, hemisphere, fact=1000.)
    # Complete dicts :
    kw_brain_obj['vertices'], kw_brain_obj['faces'] = vertices, faces
    kw_brain_obj['lr_index'], kw_brain_obj['hemisphere'] = lr_index, hemisphere
    file = os.path.splitext(os.path.split(fif_file)[1])[0]
    return _plt_src(file, kw_brain_obj, active_data, active_vert, sources,
                    kw_source_obj, kw_activation, show)
