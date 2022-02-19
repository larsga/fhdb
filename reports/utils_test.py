
import maputils
from nose.tools import eq_

# ===========================================================================
# SCALE COMPUTATION

def test_hop_wort_ratio_scale():
    eq_((15, 0), maputils.calibrate_scale(13, 0.3))

def test_gale_years_scale():
    eq_((2000, -1500), maputils.calibrate_scale(1707.0, -1370.0))
