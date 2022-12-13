import numpy as np
import pytest

from src.config import cfg
from src.platform_state.local_grid import LocalGrid


def test_calc_length_num_cells():
    lg = LocalGrid((9, 9), np.array([]))

    assert lg.LG_LEN_IN_N_CELLS == cfg.LG_LEN_IN_M / cfg.LG_MTR_PER_CELL


def test_transformation_back_to_back():
    lg = LocalGrid((10, 10), np.array([]))
    a = (10, 10)
    b = lg.xy2rc(a)
    assert a == pytest.approx(lg.rc2xy(b), 0.1)

def test_transformation_back_to_back2():
    lg = LocalGrid((9, 9), np.array([]))
    a = (10, 10)
    b = lg.xy2rc(a)
    assert a == pytest.approx(lg.rc2xy(b), 0.1)
