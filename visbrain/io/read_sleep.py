"""Load sleep files.

This file contain functions to load :
- European Data Format (*.edf)
- Micromed (*.trc)
- BrainVision (*.vhdr)
- ELAN (*.eeg)
- Hypnogram (*.hyp)
"""
import os
import io
from warnings import warn
import logging
import datetime
from concurrent.futures import Future
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import iqr

from visbrain.io.dependencies import is_mne_installed, is_mne_bids_installed
from visbrain.io.dialog import dialog_load
from visbrain.io.mneio import build_sleep_payload, finalize_raw, mne_switch
from visbrain.io.rw_hypno import (read_hypno, oversample_hypno)
from visbrain.io.rw_utils import get_file_ext
from visbrain.io.write_data import write_csv
from visbrain.io.read_annotations import merge_annotations
from visbrain.io.background import call_on_main_thread, run_in_loader_thread

from visbrain.utils.others import get_dsf
from visbrain.utils.mesh import vispy_array
from visbrain.utils.sleep.hypnoprocessing import sleepstats

from visbrain.config import PROFILER

logger = logging.getLogger('visbrain')

_DATA_FILE_FILTER = (
    "Any EEG files (*.vhdr *.edf *.gdf *.bdf *.eeg *.egi *.mff *.cnt *.trc "
    "*.set *.rec);;BrainVision (*.vhdr);;EDF (*.edf);;GDF (*.gdf);;"
    "BDF (*.bdf);;Elan (*.eeg);;EGI (*.egi);;MFF (*.mff);;CNT (*.cnt);;"
    "Micromed (*.trc);;EEGLab (*.set);;REC (*.rec)"
)

_HYPNO_FILE_FILTER = (
    "Text file (*.txt);;Elan (*.hyp);;CSV file (*.csv);;EDF+ file(*.edf);;"
    "All files (*.*)"
)

_BIDS_DATA_EXTENSIONS = (
    '.vhdr',
    '.edf',
    '.bdf',
    '.gdf',
    '.set',
    '.fif',
    '.mff',
    '.cnt',
    '.trc',
    '.rec',
    '.eeg',
)

_BIDS_ENTITY_MAP = {
    'sub': 'subject',
    'ses': 'session',
    'task': 'task',
    'acq': 'acquisition',
    'run': 'run',
    'proc': 'processing',
    'space': 'space',
    'split': 'split',
    'desc': 'description',
    'rec': 'recording',
}

__all__ = ['ReadSleepData', 'get_sleep_stats']


def _invoke_dialog(func, *args, **kwargs):
    """Ensure Qt dialogs execute on the GUI thread."""

    return call_on_main_thread(func, *args, **kwargs)


_PAYLOAD_FIELDS = (
    "sf",
    "downsample",
    "dsf",
    "data",
    "channels",
    "n",
    "start_time",
    "annotations",
)


def _ensure_payload(payload: Any) -> Dict[str, Any]:
    """Normalize payloads emitted by readers into a canonical mapping."""

    if isinstance(payload, Mapping):
        missing = [field for field in _PAYLOAD_FIELDS if field not in payload]
        if missing:
            raise KeyError(f"Incomplete payload missing fields: {missing}")
        metadata = dict(payload.get("metadata") or {})
        return build_sleep_payload(
            payload["sf"],
            payload.get("downsample"),
            payload["dsf"],
            payload["data"],
            payload["channels"],
            payload["n"],
            payload["start_time"],
            payload["annotations"],
            metadata=metadata,
        )

    if isinstance(payload, (tuple, list)) and len(payload) >= len(_PAYLOAD_FIELDS):
        base = payload[: len(_PAYLOAD_FIELDS)]
        metadata = (
            payload[len(_PAYLOAD_FIELDS)]
            if len(payload) > len(_PAYLOAD_FIELDS)
            else None
        )
        return build_sleep_payload(*base, metadata=metadata)

    raise TypeError(f"Unsupported payload type: {type(payload)!r}")


def _legacy_payload(
    result: Sequence[Any],
    path: str,
    loader_name: str,
) -> Dict[str, Any]:
    metadata = {
        "library": "visbrain",
        "loader": loader_name,
        "source": os.path.abspath(path),
    }
    return build_sleep_payload(*result, metadata=metadata)


def _select_bids_recording(
    candidates: Iterable[str],
    entities: Mapping[str, str],
    bids_root: str,
    resolve: Any,
) -> Tuple[str, Dict[str, Any]]:
    paths = sorted(candidates)
    if not paths:
        raise FileNotFoundError(f"No BIDS recordings found in {bids_root}")

    canonical = {
        (_BIDS_ENTITY_MAP.get(k, k)): v
        for k, v in dict(entities).items()
        if v
    }
    parsed_entries: List[Tuple[str, Dict[str, str]]] = []
    matched: List[Tuple[str, Dict[str, str]]] = []

    for path in paths:
        parsed = _parse_bids_basename(os.path.splitext(os.path.basename(path))[0])
        parsed_entries.append((path, parsed))
        if canonical and not all(
            parsed.get(key) == value for key, value in canonical.items()
        ):
            continue
        matched.append((path, parsed))

    if canonical and not matched:
        available = ", ".join(
            os.path.relpath(path, bids_root) for path, _ in parsed_entries
        )
        raise FileNotFoundError(
            "No BIDS recordings in %s matched entities %s. Available recordings: %s"
            % (bids_root, canonical, available or "<none>"),
        )

    pool = matched if matched else parsed_entries
    if len(pool) == 1:
        selected_path = pool[0][0]
        summary = {
            "strategy": "unique-match" if matched else "unique-candidate",
            "candidates": [os.path.relpath(path, bids_root) for path, _ in pool],
            "selected": os.path.relpath(selected_path, bids_root),
            "selected_abspath": os.path.abspath(selected_path),
            "entities": canonical,
            "matched": bool(matched),
        }
        return selected_path, summary

    selected_path, summary = _resolve_bids_strategy(pool, resolve, bids_root, canonical)
    return selected_path, summary


def _resolve_bids_strategy(
    pool: Sequence[Tuple[str, Dict[str, str]]],
    resolve: Any,
    bids_root: str,
    canonical: Mapping[str, str],
) -> Tuple[str, Dict[str, Any]]:
    strategy = resolve
    if strategy is None:
        strategy = 'raise'

    def _serialize_candidates() -> str:
        return ", ".join(os.path.relpath(path, bids_root) for path, _ in pool)

    if isinstance(strategy, str):
        key = strategy.lower()
        if key in {'raise', 'error', 'strict'}:
            message = (
                "Multiple BIDS recordings detected in %s (%s). "
                "Provide 'bids_entities' or set 'bids_resolve' "
                "(first/last/index) to choose one."
                % (bids_root, _serialize_candidates())
            )
            raise RuntimeError(message)
        if key == 'first':
            selected = pool[0]
            label = 'first'
        elif key == 'last':
            selected = pool[-1]
            label = 'last'
        elif key.isdigit():
            index = int(key)
            if index >= len(pool):
                count = len(pool)
                raise IndexError(
                    f"bids_resolve index {index} out of range for {count} recordings"
                )
            selected = pool[index]
            label = f'index:{index}'
        else:
            raise ValueError(
                f"Unsupported bids_resolve strategy '{strategy}'"
            )
    elif isinstance(strategy, int):
        index = strategy
        if index < 0:
            index += len(pool)
        if index < 0 or index >= len(pool):
            raise IndexError(
                f"bids_resolve index {strategy} out of range for {len(pool)} recordings"
            )
        selected = pool[index]
        label = f'index:{strategy}'
    elif callable(strategy):
        try:
            result = strategy([path for path, _ in pool])
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError("Callable bids_resolve failed") from exc
        if result is None:
            raise RuntimeError("Callable bids_resolve returned None")
        candidates = {path for path, _ in pool}
        if result not in candidates:
            choices = ", ".join(sorted(candidates))
            raise ValueError(
                "Callable bids_resolve must return one of: %s" % choices
            )
        for entry in pool:
            if entry[0] == result:
                selected = entry
                break
        else:  # pragma: no cover - defensive
            raise RuntimeError("Callable bids_resolve returned unexpected path")
        label = getattr(strategy, '__name__', 'callable')
    else:
        raise TypeError(f"Unsupported bids_resolve value: {type(strategy)!r}")

    summary = {
        "strategy": label,
        "candidates": [os.path.relpath(path, bids_root) for path, _ in pool],
        "selected": os.path.relpath(selected[0], bids_root),
        "selected_abspath": os.path.abspath(selected[0]),
        "entities": dict(canonical),
        "matched": bool(canonical),
    }
    return selected[0], summary


class ReadSleepData(object):
    """Main class for reading sleep data."""

    @classmethod
    def load_async(cls, *args, **kwargs) -> Future["ReadSleepData"]:
        """Instantiate ``cls`` in the shared loader executor."""

        return run_in_loader_thread(cls, *args, **kwargs)

    def __init__(self, data, channels, sf, hypno, href, preload, use_mne,
                 downsample, kwargs_mne, annotations):
        """Init."""
        # ========================== LOAD DATA ==========================
        kwargs_mne = dict(kwargs_mne or {})
        if 'preload' in kwargs_mne:
            preload = kwargs_mne['preload']
        else:
            kwargs_mne['preload'] = preload
        if 'downsample' in kwargs_mne and kwargs_mne['downsample'] is not None:
            downsample = kwargs_mne.pop('downsample')
        else:
            kwargs_mne.pop('downsample', None)

        # Dialog window if data is None :
        if data is None:
            data = _invoke_dialog(
                dialog_load,
                self,
                "Open dataset",
                '',
                _DATA_FILE_FILTER,
            )
            upath = os.path.split(data)[0]
        else:
            upath = ''

        payload: Optional[Dict[str, Any]] = None
        payload_metadata: Dict[str, Any] = {}
        file_ref: Optional[str] = None

        if isinstance(data, str):  # file is defined
            logger.info("Loading dataset from %s", data)
            # ---------- USE SLEEP or MNE ----------
            # Find file extension :
            try:
                file, ext = get_file_ext(data)
            except ValueError:
                if os.path.isdir(data):
                    file, ext = data, ''
                else:
                    raise
            # Force to use MNE if preload is False :
            use_mne = True if not preload else use_mne
            # Get if the file has to be loaded using Sleep or MNE python :
            sleep_ext = ['.eeg', '.vhdr', '.edf', '.trc', '.rec']
            if ext not in sleep_ext or (ext == '' and os.path.isdir(file)):
                use_mne = True

            if use_mne:
                is_mne_installed(raise_error=True)

            # ---------- LOAD THE FILE ----------
            if use_mne:  # Load using MNE functions
                logger.debug("Load file using MNE-python (ext=%s)", ext or '<dir>')
                kwargs_mne.setdefault('preload', preload)
                if ext == '' and os.path.isdir(file):
                    payload = sleep_switch(
                        file,
                        ext,
                        downsample,
                        kwargs_mne=kwargs_mne,
                    )
                else:
                    payload = mne_switch(file, ext, downsample, **kwargs_mne)
            else:  # Load using Sleep functions
                logger.debug("Load file using Sleep legacy readers (ext=%s)", ext)
                payload = sleep_switch(
                    file,
                    ext,
                    downsample,
                    kwargs_mne=kwargs_mne,
                )

            payload = _ensure_payload(payload)
            payload_metadata = dict(payload.get('metadata', {}))
            info = (
                "Data successfully loaded (%s):"
                "\n- Sampling-frequency : %.2fHz"
                "\n- Number of time points (before down-sampling): %i"
                "\n- Down-sampling frequency : %.2fHz"
                "\n- Number of time points (after down-sampling): %i"
                "\n- Number of channels : %i"
            )
            sf = payload['sf']
            n = payload['n']
            downsample = payload.get('downsample')
            dsf = payload['dsf']
            data = payload['data']
            channels = payload['channels']
            offset = payload['start_time']
            annot = payload['annotations']
            n_channels, n_pts_after = data.shape
            source_path = payload_metadata.get('source')
            display_name = source_path or (file + ext)
            file_ref = display_name
            logger.info(
                info % (
                    display_name,
                    sf,
                    n,
                    downsample if downsample is not None else sf,
                    n_pts_after,
                    n_channels,
                )
            )
            PROFILER("Data file loaded", level=1)

        elif isinstance(data, np.ndarray):  # array of data is defined
            if not isinstance(sf, (int, float)):
                raise ValueError("When passing raw data, the sampling "
                                 "frequency parameter, sf, must either be an "
                                 "integer or a float.")
            file = annot = None
            offset = datetime.time(0, 0, 0)
            dsf, downsample = get_dsf(downsample, sf)
            n = data.shape[1]
            data = data[:, ::dsf]
            payload_metadata = {
                'library': 'numpy',
                'loader': 'ndarray',
                'source': 'ndarray',
            }
        else:
            raise IOError("The data should either be a string which refer to "
                          "the path of a file or an array of raw data of shape"
                          " (n_electrodes, n_time_points).")

        # Keep variables :
        self._file = file_ref or file
        self._metadata = dict(payload_metadata)
        self._annot_file = np.c_[merge_annotations(annotations, annot)]
        self._N = n
        self._dsf = dsf
        self._sfori = float(sf)
        self._toffset = offset.hour * 3600. + offset.minute * 60. + \
            offset.second
        time = np.arange(n)[::dsf] / sf
        self._sf = float(downsample) if downsample is not None else float(sf)

        # ========================== LOAD HYPNOGRAM ==========================
        # Dialog window for hypnogram :
        if hypno is None:
            hypno = _invoke_dialog(
                dialog_load,
                self,
                "Open hypnogram",
                upath,
                _HYPNO_FILE_FILTER,
            )
            hypno = None if hypno == '' else hypno
        if isinstance(hypno, np.ndarray):  # array_like
            if len(hypno) == n:
                hypno = hypno[::dsf]
            else:
                raise ValueError("Then length of the hypnogram must be the "
                                 "same as raw data")
        if isinstance(hypno, str):  # (*.hyp / *.txt / *.csv)
            hypno, _ = read_hypno(hypno, time=time, datafile=file)
            # Oversample then downsample :
            hypno = oversample_hypno(hypno, self._N)[::dsf]
            PROFILER("Hypnogram file loaded", level=1)

        # ========================== CHECKING ==========================
        # ---------- DATA ----------
        # Check data shape :
        if data.ndim is not 2:
            raise ValueError("The data must be a 2D array")
        nchan, npts = data.shape

        # ---------- CHANNELS ----------
        if (channels is None) or (len(channels) != nchan):
            warn("The number of channels must be " + str(nchan) + ". Default "
                 "channel names will be used instead.")
            channels = ['chan' + str(k) for k in range(nchan)]

        # ---------- STAGE ORDER ----------
        # href checking :
        absref = ['art', 'wake', 'n1', 'n2', 'n3', 'rem']
        absint = [-1, 0, 1, 2, 3, 4]
        if href is None:
            href = absref
        elif (href is not None) and isinstance(href, list):
            # Force lower case :
            href = [k.lower() for k in href]
            # Check that all stage are present :
            for k in absref:
                if k not in href:
                    raise ValueError(k + " not found in href.")
            # Force capitalize :
            href = [k.capitalize() for k in href]
            href[href.index('Rem')] = 'REM'
        else:
            raise ValueError("The href parameter must be a list of string and"
                             " must contain 'art', 'wake', 'n1', 'n2', 'n3' "
                             "and 'rem'")
        # Conversion variable :
        absref = ['Art', 'Wake', 'N1', 'N2', 'N3', 'REM']
        conv = {absint[absref.index(k)]: absint[i] for i, k in enumerate(href)}

        # ---------- HYPNOGRAM ----------
        if hypno is None:
            hypno = np.zeros((npts,), dtype=np.float32)
        else:
            n = len(hypno)
            # Check hypno values :
            if (hypno.min() < -1.) or (hypno.max() > 4) or (n != npts):
                warn("\nHypnogram values must be comprised between -1 and 4 "
                     "(see Iber et al. 2007). Use:\n-1 -> Art (optional)\n 0 "
                     "-> Wake\n 1 -> N1\n 2 -> N2\n 3 -> N4\n 4 -> REM\nEmpty "
                     "hypnogram will be used instead")
                hypno = np.zeros((npts,), dtype=np.float32)

        # ---------- SCALING ----------
        # Assume that the inter-quartile amplitude of EEG data is ~50 uV
        iqr_chan = iqr(data[:, :int(data.shape[1] / 4)], axis=-1)
        bad_iqr = iqr_chan < 1.

        if np.any(bad_iqr):
            mult_fact = np.zeros_like(iqr_chan)
            iqr_chan[iqr_chan == 0.] = 1.
            mult_fact[bad_iqr] = np.floor(np.log10(50. / iqr_chan[bad_iqr]))
            data *= 10. ** mult_fact[..., np.newaxis]
            warn("Wrong channel data amplitude. ")

        # ---------- CONVERSION ----------=
        # Convert data and hypno to be contiguous and float 32 (for vispy):
        self._data = vispy_array(data)
        self._hypno = vispy_array(hypno)
        self._time = vispy_array(time)
        self._channels = channels
        self._href = href
        self._hconv = conv
        PROFILER("Check data", level=1)

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return metadata associated with the loaded dataset."""

        return dict(self._metadata)


def _discover_bids_files(root: str) -> list[str]:
    """Return candidate raw files contained inside a BIDS directory."""

    matches: list[str] = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith(_BIDS_DATA_EXTENSIONS):
                matches.append(os.path.join(dirpath, name))
    return sorted(matches)


def _looks_like_bids(directory: str) -> bool:
    """Heuristically determine whether *directory* follows BIDS layout."""

    try:
        entries = os.listdir(directory)
    except OSError:
        return False
    if 'dataset_description.json' in entries or 'participants.tsv' in entries:
        return True
    return any(name.startswith('sub-') for name in entries)


def _parse_bids_basename(basename: str) -> Dict[str, str]:
    """Parse BIDS key-value pairs from a file basename."""

    entities: Dict[str, str] = {}
    parts = [part for part in basename.split('_') if part]
    if not parts:
        return entities

    suffix_candidate = parts[-1]
    if '-' in suffix_candidate:
        key, value = suffix_candidate.split('-', 1)
        mapped = _BIDS_ENTITY_MAP.get(key)
        if mapped is not None:
            entities[mapped] = value
            suffix_candidate = ''
    if suffix_candidate:
        entities['suffix'] = suffix_candidate

    for part in parts[:-1]:
        if '-' not in part:
            continue
        key, value = part.split('-', 1)
        mapped = _BIDS_ENTITY_MAP.get(key)
        if mapped is not None:
            entities[mapped] = value
    return entities


def _build_bids_path(raw_path: str, bids_root: str):
    from mne_bids import BIDSPath

    raw_path = os.path.abspath(raw_path)
    bids_root = os.path.abspath(bids_root)
    basename = os.path.splitext(os.path.basename(raw_path))[0]
    entities = _parse_bids_basename(basename)

    rel_parent = os.path.relpath(os.path.dirname(raw_path), bids_root)
    datatype = os.path.basename(rel_parent)
    if datatype in {'eeg', 'ieeg', 'meg', 'beh', 'anat', 'physio', 'pet'}:
        entities['datatype'] = datatype

    entities['extension'] = os.path.splitext(raw_path)[1]
    entities.setdefault('suffix', entities.get('datatype', 'eeg'))
    entities['root'] = bids_root

    return BIDSPath(check=False, **entities)


def _match_bids_candidate(
    candidates: Iterable[str],
    entities: Mapping[str, str],
    bids_root: str,
    *,
    resolve: Any = None,
) -> Tuple[Any, Dict[str, Any]]:
    selected_path, summary = _select_bids_recording(
        candidates,
        entities,
        bids_root,
        resolve,
    )
    logger.info(
        "Resolved BIDS selection using strategy '%s': %s",
        summary["strategy"],
        summary["selected"],
    )
    bids_path = _build_bids_path(selected_path, bids_root)
    summary["bids_path"] = str(bids_path)
    return bids_path, summary


def _coerce_bids_path(reference: Any, bids_root: str):
    from mne_bids import BIDSPath

    if isinstance(reference, BIDSPath):
        return reference.copy().update(root=bids_root, check=False)
    if isinstance(reference, dict):
        params = dict(reference)
        params.setdefault('root', bids_root)
        return BIDSPath(check=False, **params)
    if isinstance(reference, str):
        target = reference
        if not os.path.isabs(target):
            target = os.path.join(bids_root, target)
        if os.path.isdir(target):
            candidates = _discover_bids_files(target)
            bids_path, _ = _match_bids_candidate(candidates, {}, target)
            return bids_path
        return _build_bids_path(target, bids_root)
    raise TypeError("Unsupported bids_path reference: %r" % (reference,))


def _load_bids_directory(
    directory: str,
    downsample: Optional[float],
    kwargs_mne: Dict[str, Any],
):
    is_mne_bids_installed(raise_error=True)
    from mne_bids import read_raw_bids

    bids_root = os.path.abspath(directory)
    bids_path_param = kwargs_mne.pop('bids_path', None)
    entities = kwargs_mne.pop('bids_entities', {}) or {}
    bids_resolve = kwargs_mne.pop('bids_resolve', None)
    preload = kwargs_mne.pop('preload', True)
    verbose = kwargs_mne.pop('verbose', None)
    extra_params = kwargs_mne.pop('extra_params', {}) or {}
    extra_params = dict(extra_params)

    if bids_path_param is not None:
        bids_path = _coerce_bids_path(bids_path_param, bids_root)
        selection_summary = {
            'strategy': 'explicit-path',
            'candidates': [],
            'selected': str(bids_path),
            'selected_abspath': str(bids_path),
            'entities': dict(entities),
            'matched': True,
            'bids_path': str(bids_path),
        }
    else:
        candidates = _discover_bids_files(bids_root)
        bids_path, selection_summary = _match_bids_candidate(
            candidates,
            entities,
            bids_root,
            resolve=bids_resolve,
        )

    extra_params.setdefault('preload', preload)
    extra_params.update(kwargs_mne)
    raw = read_raw_bids(bids_path, extra_params=extra_params, verbose=verbose)

    bids_metadata = {
        'bids': {
            'root': bids_root,
            'entities': dict(selection_summary.get('entities', {})),
            'candidates': list(selection_summary.get('candidates', [])),
            'strategy': selection_summary.get('strategy'),
            'selected': selection_summary.get('selected'),
        },
        'source': selection_summary.get('selected_abspath', bids_root),
    }
    if entities:
        bids_metadata['bids']['requested_entities'] = dict(entities)
    if selection_summary.get('bids_path'):
        bids_metadata['bids']['bids_path'] = selection_summary['bids_path']
    if bids_resolve is not None:
        bids_metadata['bids']['resolve'] = bids_resolve

    return finalize_raw(raw, downsample, metadata=bids_metadata)


def sleep_switch(file, ext, downsample, kwargs_mne=None):
    """Switch between sleep data files.

    Parameters
    ----------
    file : string
        Path to the file to load.
    ext : string
        Extension name (e.g. '.eeg')
    downsample : int
        Down-sampling frequency.
    kwargs_mne : dict | None
        Additional parameters forwarded to the MNE readers when applicable.

    Returns
    -------
    sf : float
        The original sampling-frequency.
    downsample : float
        The down-sampling frequency used.
    dsf : int
        The down-sampling factor.
    data : array_like
        The raw data of shape (n_channels, n_points)
    channels : list
        List of channel names.
    n : int
        Number of time points before down-sampling.
    start_time : datetime.time
        The time offset.
    annotations : array_like
        Array of annotations.
    """
    # Get full path :
    kwargs_mne = dict(kwargs_mne or {})
    legacy_kwargs = dict(kwargs_mne)
    path = file + ext if ext else file

    if ext == '' and os.path.isdir(file) and _looks_like_bids(file):
        try:
            return _load_bids_directory(file, downsample, kwargs_mne)
        except Exception as exc:
            logger.warning(
                "Falling back to file-based loading for %s due to %s",
                file,
                exc,
            )
            candidates = _discover_bids_files(file)
            if candidates:
                fallback_entities = legacy_kwargs.get('bids_entities', {}) or {}
                fallback_resolve = legacy_kwargs.get('bids_resolve', 'first')
                try:
                    selected_path, selection_summary = _select_bids_recording(
                        candidates,
                        fallback_entities,
                        file,
                        fallback_resolve,
                    )
                except Exception as select_exc:
                    logger.debug(
                        "Failed to resolve fallback candidate in %s: %s",
                        file,
                        select_exc,
                    )
                else:
                    for key in ('bids_entities', 'bids_path', 'bids_resolve'):
                        legacy_kwargs.pop(key, None)
                    fallback_file, fallback_ext = os.path.splitext(selected_path)
                    logger.info(
                        "Attempting fallback load of %s using extension %s",
                        selected_path,
                        fallback_ext or '<unknown>',
                    )
                    try:
                        payload = mne_switch(
                            fallback_file,
                            fallback_ext,
                            downsample,
                            **legacy_kwargs,
                        )
                    except Exception as mne_exc:  # pragma: no cover - defensive
                        logger.debug("MNE fallback failed: %s", mne_exc)
                    else:
                        payload_metadata = dict(payload.get('metadata', {}))
                        fallback_meta = payload_metadata.setdefault('fallback', {})
                        fallback_meta['reason'] = str(exc)
                        fallback_meta['strategy'] = selection_summary.get('strategy')
                        fallback_meta['selected'] = selection_summary.get('selected')
                        payload['metadata'] = payload_metadata
                        return payload

    if ext == '.vhdr':  # BrainVision
        return _legacy_payload(read_bva(path, downsample), path, 'brainvision')

    if ext == '.eeg':  # Elan
        return _legacy_payload(read_elan(path, downsample), path, 'elan')

    elif ext in ['.edf', '.rec']:  # European Data Format
        label = 'edf' if ext == '.edf' else 'rec'
        return _legacy_payload(read_edf(path, downsample), path, label)

    elif ext == '.trc':  # Micromed
        return _legacy_payload(read_trc(path, downsample), path, 'micromed')

    else:  # None
        raise ValueError("*" + ext + " files are currently not supported.")


###############################################################################
###############################################################################
#                               LOAD FILES
###############################################################################
###############################################################################

def read_edf(path, downsample):
    """Read data from a European Data Format (edf) file.

    Use phypno class for reading EDF files:
        http: // phypno.readthedocs.io / api / phypno.ioeeg.edf.html

    Parameters
    ----------
    path: str
        Filename(with full path) to EDF file
    downsample : int
        Down-sampling frequency.

    Returns
    -------
    sf : int
        The sampling frequency.
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    n : int
        Number of points in the original data
    start_time : array_like
        Starting time of the recording (hh:mm:ss)
    annotations : array_like
        Array of annotations.
    """
    assert os.path.isfile(path)

    from ..utils.sleep.edf import Edf

    edf = Edf(path)

    # Return header informations
    _, start_time, sf, chan, n_samples, _ = edf.return_hdr()
    start_time = start_time.time()

    # Keep only data channels (e.g excludes marker chan)
    freqs = np.unique(edf.hdr['n_samples_per_record']) / edf.hdr[
        'record_length']
    sf = freqs.max()

    if len(freqs) != 1:
        bad_chans = np.where(edf.hdr['n_samples_per_record'] < sf)
        chan = np.delete(chan, bad_chans)

    # Load all samples of selected channels
    np.seterr(divide='ignore', invalid='ignore')
    data = edf.return_dat(chan, 0, n_samples)

    # Get original signal length :
    n = data.shape[1]

    # Get down-sample factor :
    sf = float(sf)
    chan = list(chan)
    dsf, downsample = get_dsf(downsample, sf)

    return sf, downsample, dsf, data[:, ::dsf], chan, n, start_time, None


def read_trc(path, downsample):
    """Read data from a Micromed (trc) file (version 4).

    Poor man's version of micromedio.py from Neo package
    (https://pythonhosted.org/neo/)

    Parameters
    ----------
    path : str
        Filename(with full path) to .trc file
    downsample : int
        Down-sampling frequency.

    Returns
    -------
    sf : float
        The sampling frequency.
    downsample : float
        The downsampling frequency
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    n : int
        Number of samples before down-sampling.
    start_time : array_like
        Starting time of the recording (hh:mm:ss)
    annotations : array_like
        Array of annotations.
    """
    import struct

    def read_f(f, fmt):
        return struct.unpack(fmt, f.read(struct.calcsize(fmt)))

    with io.open(path, 'rb') as f:
        # Read header
        f.seek(175, 0)
        header_version, = read_f(f, 'b')
        assert header_version == 4

        f.seek(138, 0)
        data_start_offset, n_chan, _, sf, nbytes = read_f(f, 'IHHHH')

        f.seek(128, 0)
        day, month, year, hour, minute, sec = read_f(f, 'bbbbbb')
        start_time = datetime.time(hour, minute, sec)

        # Raw data
        f.seek(data_start_offset, 0)
        m_raw = np.fromstring(f.read(), dtype='u' + str(nbytes))
        m_raw = m_raw.reshape((int(m_raw.size / n_chan), n_chan)).transpose()

        # Read label / gain
        gain = []
        chan = []
        logical_ground = []
        data = np.empty(shape=m_raw.shape, dtype=np.float32)

        f.seek(176, 0)
        zone_names = ['ORDER', 'LABCOD']
        zones = {}
        for zname in zone_names:
            zname2, pos, length = read_f(f, '8sII')
            zones[zname] = zname2, pos, length

        zname2, pos, length = zones['ORDER']
        f.seek(pos, 0)
        code = np.fromfile(f, dtype='u2', count=n_chan)

        for c in range(n_chan):
            zname2, pos, length = zones['LABCOD']
            f.seek(pos + code[c] * 128 + 2, 0)

            chan = np.append(chan, f.read(6).decode('utf-8').strip())
            logical_min, logical_max, logic_ground_chan, physical_min, \
                physical_max = read_f(f, 'iiiii')

            logical_ground = np.append(logical_ground, logic_ground_chan)

            gain = np.append(gain, float(physical_max - physical_min) /
                             float(logical_max - logical_min + 1))

    # Multiply by gain
    m_raw = m_raw - logical_ground[:, np.newaxis]
    data = m_raw * gain[:, np.newaxis].astype(np.float32)

    # Get original signal length :
    n = data.shape[1]

    # Get down-sample factor :
    sf = float(sf)
    chan = list(chan)
    dsf, downsample = get_dsf(downsample, sf)

    return sf, downsample, dsf, data[:, ::dsf], chan, n, start_time, None


def read_bva(path, downsample, read_markers=False):
    """Read data from a BrainVision (*.vhdr) file.

    Poor man's version of https: // gist.github.com / breuderink / 6266871

    Assumes that data are saved with the following parameters:
        - Data format: Binary
        - Orientation: Multiplexed
        - Format: int16

    Parameters
    ----------
    path : str
        Filename(with full path) to .vhdr file. Data file must be in the
        same directory.
    downsample : int
        Down-sampling frequency.
    read_markers : bool | False
        Import markers from the .vmrk files as annotations

    Returns
    -------
    sf : float
        The sampling frequency.
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    n : int
        Number of points before down-sampling.
    start_time : array_like
        Starting time of the recording (hh:mm:ss)
    annotations : array_like
        Array of annotations.
    """
    import re

    assert os.path.isfile(path)

    # Read header
    ent = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0, encoding='utf-8')

    for item in ent:
        if 'DataFile=' in item:
            data_file = item.split('=')[1]
            data_path = os.path.join(os.path.dirname(path), data_file)
            assert os.path.isfile(data_path)
        elif 'MarkerFile=' in item:
            marker_file = item.split('=')[1]
            marker_path = os.path.join(os.path.dirname(path), marker_file)
        elif 'NumberOfChannels=' in item:
            n_chan = int(re.findall('\d+', item)[0])
        elif 'SamplingInterval=' in item:
            si = float(re.findall("[-+]?\d*\.\d+|\d+", item)[0])
            sf = 1 / (si * 0.000001)
        elif 'DataFormat' in item:
            data_format = item.split('=')[1]
        elif 'BinaryFormat' in item:
            binary_format = item.split('=')[1]
        elif 'DataOrientation' in item:
            data_orient = item.split('=')[1]

    # Check binary format
    assert "BINARY" in data_format
    assert "INT_16" in binary_format
    assert "MULTIPLEXED" in data_orient

    # Extract channel labels and resolution
    start_label = np.array(np.where(np.char.find(ent, 'Ch1=') == 0)).min()
    chan = {}
    resolution = np.empty(shape=n_chan)

    for i, j in enumerate(range(start_label, start_label + n_chan)):
        chan[i] = re.split('\W+', ent[j])[1]
        resolution[i] = float(ent[j].split(",")[2])

    chan = np.array(list(chan.values())).flatten()

    # Read marker file (if present) to extract recording time
    if os.path.isfile(marker_path):
        vmrk = np.genfromtxt(marker_path, delimiter='\n', usecols=[0],
                             dtype=None, skip_header=0, encoding='utf-8')

        # Read start-time
        for item in vmrk:
            if 'New Segment' in item:
                st = re.split('\W+', item)[-1]
                start_time = datetime.time(int(st[8:10]), int(st[10:12]),
                                           int(st[12:14]))
                break
            else:
                start_time = datetime.time(0, 0, 0)

        # Read markers
        if read_markers:
            onsets = np.array([], dtype=float)
            durations = np.array([], dtype=float)
            descriptions = np.array([], dtype=str)
            for item in vmrk:
                if 'Mk' in item and ';' not in item:
                    onsets = np.append(onsets, int(
                        re.sub(r'\s', '', item).split(',')[2]))
                    durations = np.append(durations, int(
                        re.sub(r'\s', '', item).split(',')[3]))
                    descriptions = np.append(descriptions, re.sub(
                        r'\s', '', item).split(',')[1])
                    anot = np.c_[onsets, durations, descriptions]
        else:
            anot = None

    with io.open(data_path, 'rb') as f:
        raw = f.read()
        size = int(len(raw) / 2)

        ints = np.ndarray((n_chan, int(size / n_chan)),
                          dtype='<i2', order='F', buffer=raw)

        data = np.float32(np.diag(resolution)).dot(ints)

    # Get original signal length :
    n = data.shape[1]

    # Get down-sample factor :
    sf = float(sf)
    chan = list(chan)
    dsf, downsample = get_dsf(downsample, sf)

    return sf, downsample, dsf, data[:, ::dsf], chan, n, start_time, anot


def read_elan(path, downsample):
    """Read data from a ELAN (eeg) file.

    Elan format specs: http: // elan.lyon.inserm.fr/

    Parameters
    ----------
    path : str
        Filename(with full path) to Elan .eeg file
    downsample : int
        Down-sampling frequency.

    Returns
    -------
    sf : int
        The sampling frequency.
    data : array_like
        The data organised as well(n_channels, n_points)
    chan : list
        The list of channel's names.
    n : int
        Number of samples before down-sampling.
    start_time : array_like
        Starting time of the recording (hh:mm:ss)
    annotations : array_like
        Array of annotations.
    """
    header = path + '.ent'

    assert os.path.isfile(path)
    assert os.path.isfile(header)

    # Read .ent file
    ent = np.genfromtxt(header, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0, encoding='utf-8')

    # eeg file version
    eeg_version = ent[0]

    if eeg_version == 'V2':
        nb_oct = 2
        formread = '>i2'
    elif eeg_version == 'V3':
        nb_oct = 4
        formread = '>i4'

    # Sampling rate
    sf = 1. / float(ent[8])

    # Record starting time
    if ent[4] != "No time":
        hour, minutes, sec = ent[4].split(':')
        start_time = datetime.time(int(hour), int(minutes), int(sec))
        day, month, year = ent[3].split(':')
    else:
        start_time = datetime.time(0, 0, 0)

    # Channels
    nb_chan = np.int(ent[9])
    nb_chan = nb_chan

    # Last 2 channels do not contain data
    nb_chan_data = nb_chan - 2
    chan_list = slice(nb_chan_data)
    chan = ent[10:10 + nb_chan_data]

    # Gain
    gain = np.zeros(nb_chan)
    offset1 = 9 + 3 * nb_chan
    offset2 = 9 + 4 * nb_chan
    offset3 = 9 + 5 * nb_chan
    offset4 = 9 + 6 * nb_chan

    for i in np.arange(1, nb_chan + 1):

        min_an = float(ent[offset1 + i])
        max_an = float(ent[offset2 + i])
        min_num = float(ent[offset3 + i])
        max_num = float(ent[offset4 + i])

        gain[i - 1] = (max_an - min_an) / (max_num - min_num)
    if gain.dtype != np.float32:
        gain = gain.astype(np.float32, copy=False)

    # Load memmap
    nb_bytes = os.path.getsize(path)
    nb_samples = int(nb_bytes / (nb_oct * nb_chan))

    m_raw = np.memmap(path, dtype=formread, mode='r',
                      shape=(nb_chan, nb_samples), order={'F'})

    # Get original signal length :
    n = m_raw.shape[1]

    # Get down-sample factor :
    sf = float(sf)
    chan = list(chan)
    dsf, downsample = get_dsf(downsample, sf)

    # Multiply by gain :
    data = m_raw[chan_list, ::dsf] * \
        gain[chan_list][..., np.newaxis]

    return sf, downsample, dsf, data, chan, n, start_time, None


def get_sleep_stats(hypno_file, output_file=None):
    """Compute sleep statistics from hypnogram file and export them in csv.

    Sleep statistics specifications:

        * Time in Bed (TIB) : total duration of the hypnogram.
        * Total Dark Time (TDT) : duration of the hypnogram from beginning
          to last period of sleep.
        * Sleep Period Time (SPT) : duration from first to last period of
          sleep.
        * Wake After Sleep Onset (WASO) : duration of wake periods within SPT
        * Sleep Efficiency (SE) : TST / TDT * 100 (%).
        * Total Sleep Time (TST) : SPT - WASO.
        * W, N1, N2, N3 and REM: sleep stages duration.
        * % (W, ... REM) : sleep stages duration expressed in percentages of
          TDT.
        * Latencies: latencies of sleep stages from the beginning of the
          record.

    (All values except SE and percentages are expressed in minutes)

    Parameters
    ----------
    hypno_file : string
        Full path to the hypnogram file.
    output_file : string | None
        Full path to the output file. If no file is provided, sleep statictics
        are print out to the terminal.
    """
    # File conversion :
    if output_file is not None:  # Check extension
        ext = os.path.splitext(output_file)[1][1:].strip().lower()
        if ext == '':
            output_file = output_file + '.csv'

    # Load hypnogram
    hypno, sf_hyp = read_hypno(hypno_file)
    if sf_hyp < 1:
        mult = int(np.round(len(hypno) / sf_hyp))
        hypno = oversample_hypno(hypno, mult)
        sf_hyp = 1

    # Get sleep stats
    stats = sleepstats(hypno, sf_hyp=sf_hyp)
    stats['File'] = hypno_file
    print('\nSLEEP STATS\n===========')
    keys, val = [''] * len(stats), [''] * len(stats)
    # Fill table :
    for num, (k, v) in enumerate(stats.items()):
        print(k, '\t', str(v))
        # Remember variables :
        keys[int(num)] = k
        val[int(num)] = str(v)
    if output_file is not None:
        write_csv(output_file, zip(keys, val))
        print('===========\nCSV file saved to:', output_file)
