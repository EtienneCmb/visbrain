"""Test functions in rw_hypno.py."""
import numpy as np
import pytest

from visbrain.io.rw_hypno import (hypno_sample_to_time, hypno_time_to_sample,
                                  oversample_hypno, read_hypno, write_hypno)
from visbrain.tests._tests_visbrain import _TestVisbrain

state_cfgs = {
    'df': (['Art', 'Wake', 'N1', 'N2', 'N3', 'REM'], [-1, 0, 1, 2, 3, 4]),
    'None': (None, None),
    'superset': (['Art', 'Wake', 'N1', 'N2', 'N3', 'REM', 'other'],
                 [-1, 0, 1, 2, 3, 4, 100]),
    'subset': (['Art', 'Wake'], [-1, 0]),
    'other': (['1', '2', '3'], [1, 2, 3]),
}  # (hstates, hvalues)


class TestRwHypno(_TestVisbrain):
    """Test functions in rw_hypno.py."""

    @staticmethod
    def _get_hypno():
        return np.array([-1, 4, 2, 3, 0])

    @pytest.mark.parametrize(
        "hcfg, hyp", [
            ('df', [-1, -1, 4, 2, 3, 3, 0, 0, 0, 0, 1, 1, 1, -1, -1]),
            ('superset', [-1, -1, 4, 2, 3, 3, 0, 0, 0, 0, 1, 1, 1, -1, -1]),
        ]
    )
    def test_hypno_conversion(self, hcfg, hyp):
        """Test conversion functions."""
        hstates, hvalues = state_cfgs[hcfg]
        hyp = np.array(hyp)
        sf = 100.
        time = np.arange(len(hyp)) / sf
        # Sample -> time :
        df = hypno_sample_to_time(hyp, time, hstates, hvalues)
        # Time -> sample :
        hyp_new, time_new, sf_new = hypno_time_to_sample(
            df.copy(), len(hyp), hstates, hvalues
        )
        hyp_new_2, _, _ = hypno_time_to_sample(
            df.copy(), time, hstates, hvalues
        )
        # Test :
        np.testing.assert_array_equal(hyp, hyp_new)
        np.testing.assert_array_equal(hyp_new, hyp_new_2)
        np.testing.assert_array_almost_equal(time, time_new)
        assert sf == sf_new

    def test_oversample_hypno(self):
        """Test function oversample_hypno."""
        hyp = self._get_hypno()
        hyp_over = oversample_hypno(hyp, 12)
        to_hyp = np.array([-1, -1, 4, 4, 2, 2, 3, 3, 0, 0, 0, 0])
        assert np.array_equal(hyp_over, to_hyp)

    @pytest.mark.parametrize(
        "hcfg, hyp, version, ext, expected", [

            # Default states cfg: works with all versions
            ['None', [-1, -1, 0, 1, 2], 'sample', '.txt', None],
            ['df', [-1, -1, 0, 1, 2], 'sample', '.txt', None],
            ['df', [-1, -1, 0, 1, 2], 'sample', '.hyp', None],
            ['df', [-1, -1, 0, 1, 2], 'time', '.txt', None],
            ['df', [-1, -1, 0, 1, 2], 'time', '.csv', None],
            ['df', [-1, -1, 0, 1, 2], 'time', '.xlsx', None],
            # Check:
            # - Non default state config can't be saved in elan format
            # - Hypnogram can't contain non-mapped keys
            ['subset', [-1, -1, 0, ], 'sample', '.hyp', ValueError],
            ['subset', [-1, -1, 0, ], 'sample', '.txt', None],
            ['subset', [-1, -1, 0, ], 'time', '.txt', None],
            ['subset', [-1, -1, 0, ], 'time', '.csv', None],
            ['subset', [-1, -1, 0, 1], 'time', '.txt', KeyError],
            ['superset', [-1, -1, 0, ], 'sample', '.hyp', ValueError],
            ['superset', [-1, -1, 0, ], 'sample', '.txt', None],
            ['superset', [-1, -1, 0, ], 'time', '.txt', None],
            ['superset', [-1, -1, 0, ], 'time', '.csv', None],
            ['superset', [-2, -1, 0, 1], 'time', '.txt', KeyError],
            ['other', [1, 1, 3, ], 'sample', '.hyp', ValueError],
            ['other', [1, 1, 3, ], 'sample', '.txt', None],
            ['other', [1, 1, 3, ], 'time', '.txt', None],
            ['other', [1, 1, 3, ], 'time', '.csv', None],
            ['other', [2, 1, 3, -2], 'time', '.txt', KeyError],
        ]
    )
    def test_rw_hypno(self, hcfg, hyp, version, ext, expected):
        """Test function write_hypno_txt."""
        hstates, hvalues = state_cfgs[hcfg]
        hyp = np.array(hyp)
        sf, npts = 1., len(hyp)
        time = np.arange(npts) / sf
        info = {'Info_1': 10, 'Info_2': 'coco', 'Info_3': 'veut_un_gateau'}
        filename = self.to_tmp_dir('hyp_test_' + hcfg + version + ext)
        if expected is None:
            # Write
            write_hypno(filename, hyp, version=version, sf=sf, npts=npts,
                        window=1., time=time, info=info, hstates=hstates,
                        hvalues=hvalues, popup=False)
            # Read
            hyp_new, _ = read_hypno(filename, time=time, hstates=hstates,
                                    hvalues=hvalues, popup=False)
            np.testing.assert_array_equal(hyp, hyp_new)
        else:
            with pytest.raises(expected):
                write_hypno(filename, hyp, version=version, sf=sf, npts=npts,
                            window=1., time=time, info=info, hstates=hstates,
                            hvalues=hvalues, popup=False)
