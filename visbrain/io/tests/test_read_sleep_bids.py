import datetime
import os
import sys
import types

import numpy as np
import pytest

from visbrain.io.mneio import build_sleep_payload
from visbrain.io.read_sleep import (
    _discover_bids_files,
    _match_bids_candidate,
    _load_bids_directory,
    sleep_switch,
)


@pytest.fixture(autouse=True)
def _fake_mne_bids(monkeypatch):
    """Provide a lightweight stub of :mod:`mne_bids` for tests."""

    class FakeBIDSPath:
        def __init__(self, check=False, **entities):
            self.entities = dict(entities)

        def copy(self):
            return FakeBIDSPath(**self.entities)

        def update(self, **updates):
            data = dict(self.entities)
            data.update(updates)
            return FakeBIDSPath(**data)

        def __str__(self):
            root = self.entities.get('root', '')
            parts = [
                f"{key}-{value}"
                for key, value in sorted(self.entities.items())
                if key != 'root'
            ]
            basename = '_'.join(parts)
            return os.path.join(root, basename)

    class FakeRaw:
        def __init__(self):
            self._data = np.arange(20.0).reshape(2, 10)
            self.info = {'sfreq': 100.0, 'ch_names': ['C3', 'C4'], 'bads': []}
            self.annotations = None
            self._raw_extras = ()

        def pick_types(self, **kwargs):
            return self

        def get_data(self, picks=None):
            return self._data

    def read_raw_bids(bids_path, extra_params=None, verbose=None):
        return FakeRaw()

    module = types.SimpleNamespace(BIDSPath=FakeBIDSPath, read_raw_bids=read_raw_bids)
    monkeypatch.setitem(sys.modules, 'mne_bids', module)
    monkeypatch.setattr(
        'visbrain.io.read_sleep.is_mne_bids_installed',
        lambda raise_error=False: True,
    )
    return module


def _add_bids_recording(dataset, run_label='2'):
    """Create an additional placeholder recording for *dataset*."""

    recording = dataset.recording
    if 'run-1' not in recording.name:
        raise AssertionError('Unexpected fixture naming convention')
    new_recording = recording.with_name(
        recording.name.replace('run-1', f'run-{run_label}')
    )
    new_recording.write_bytes(b'EDF')
    metadata = new_recording.with_suffix('.json')
    metadata.write_text('{}')
    return new_recording


def test_match_bids_candidate_resolve_last(bids_sleep_directory):
    extra_recording = _add_bids_recording(bids_sleep_directory, run_label='2')
    root = str(bids_sleep_directory.root)
    candidates = _discover_bids_files(root)
    _, summary = _match_bids_candidate(candidates, {}, root, resolve='last')
    assert summary['selected'] == os.path.relpath(str(extra_recording), root)
    assert summary['strategy'] == 'last'


def test_match_bids_candidate_reports_available(bids_sleep_directory):
    _add_bids_recording(bids_sleep_directory, run_label='2')
    root = str(bids_sleep_directory.root)
    candidates = _discover_bids_files(root)
    with pytest.raises(FileNotFoundError) as err:
        _match_bids_candidate(candidates, {'run': '99'}, root)
    message = str(err.value)
    assert 'run-1' in message
    assert 'run-2' in message


def test_load_bids_directory_metadata(bids_sleep_directory):
    root = str(bids_sleep_directory.root)
    expected_rel = os.path.relpath(
        str(bids_sleep_directory.recording),
        root,
    )
    requested_entities = {'run': '1', 'task': 'rest'}
    payload = _load_bids_directory(
        root,
        downsample=50.0,
        kwargs_mne={
            'bids_entities': requested_entities,
            'bids_resolve': 'first',
        },
    )
    metadata = payload['metadata']
    assert metadata['bids']['selected'] == expected_rel
    assert metadata['bids']['selected_abspath'] == str(bids_sleep_directory.recording)
    assert metadata['bids']['strategy'] == 'unique-match'
    assert metadata['bids']['requested_entities'] == requested_entities
    assert metadata['bids']['resolve'] == 'first'
    assert metadata['source'] == str(bids_sleep_directory.recording)


def test_sleep_switch_bids_fallback(monkeypatch, bids_sleep_directory):
    def failing_loader(*args, **kwargs):  # pragma: no cover - invoked in test
        raise RuntimeError('forced failure')

    monkeypatch.setattr(
        'visbrain.io.read_sleep._load_bids_directory',
        failing_loader,
    )

    def fake_mne_switch(file, ext, downsample, **kwargs):
        data = np.ones((1, 8))
        return build_sleep_payload(
            100.0,
            100.0,
            1,
            data,
            ['Cz'],
            data.shape[1],
            datetime.time(0, 0, 0),
            None,
            metadata={'source': os.path.abspath(file + ext)},
        )

    monkeypatch.setattr(
        'visbrain.io.read_sleep.mne_switch',
        fake_mne_switch,
    )

    payload = sleep_switch(
        str(bids_sleep_directory.root),
        '',
        100.0,
        kwargs_mne={'bids_entities': {'run': '1'}},
    )
    metadata = payload['metadata']
    assert 'fallback' in metadata
    expected_rel = os.path.relpath(
        str(bids_sleep_directory.recording),
        str(bids_sleep_directory.root),
    )
    assert metadata['fallback']['selected'] == expected_rel
    assert metadata['fallback']['strategy'] == 'first'
    assert metadata['fallback']['reason'] == 'forced failure'
    assert metadata['source'] == str(bids_sleep_directory.recording)
