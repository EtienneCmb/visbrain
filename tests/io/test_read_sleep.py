import datetime

import numpy as np

from visbrain.io import read_sleep


def test_read_edf_filters_low_rate_channels(monkeypatch, tmp_path):
    """EDF reader should ignore low-rate channels when loading data."""
    dummy_path = tmp_path / "dummy.edf"
    dummy_path.write_bytes(b"")

    from visbrain.utils.sleep import edf as edf_module

    class DummyEdf(edf_module.Edf):
        def __init__(self, path):
            self.filename = str(path)
            self.hdr = {
                "n_samples_per_record": [10, 20],
                "record_length": 1.0,
                "n_records": 1,
                "label": ["low", "high"],
                "digital_min": np.array([0.0, 0.0], dtype=float),
                "digital_max": np.array([1.0, 1.0], dtype=float),
                "physical_min": np.array([0.0, 0.0], dtype=float),
                "physical_max": np.array([1.0, 1.0], dtype=float),
            }

        def return_hdr(self):
            return (
                "subject",
                datetime.datetime(2000, 1, 1),
                self.hdr["n_samples_per_record"][0] / self.hdr["record_length"],
                list(self.hdr["label"]),
                self.hdr["n_samples_per_record"][0] * self.hdr["n_records"],
                self.hdr,
            )

        def _read_dat(self, i_chan, begsam, endsam):
            length = int(endsam - begsam)
            return (np.arange(length, dtype=np.int16) + i_chan * 100).astype(
                "<i2"
            )

    monkeypatch.setattr(edf_module, "Edf", DummyEdf)

    result = read_sleep.read_edf(str(dummy_path), downsample=None)
    sf, downsample, dsf, data, channels, n, start_time, annotations = result

    assert sf == 20.0
    assert channels == ["high"]
    assert data.shape == (1, 20)
    expected = np.arange(20) + 100
    np.testing.assert_array_equal(data[0], expected)
    assert n == 20
    assert annotations is None
    assert start_time == datetime.time(0, 0)
    assert dsf == 1
    assert downsample is None
