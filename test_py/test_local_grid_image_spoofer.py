from src.data_providers.sim.local_grid_image_spoofer import LocalGridImageSpoofer

import os
from src.utils.coordinate_transforms import img_axes2world_axes
from PIL import Image
import numpy as np

from src.utils.config import Config

def test_sim_calc_total_img_length_in_m():
    cfg = Config()
    map_img = np.zeros((100, 100))
    lga = LocalGridImageSpoofer(cfg)
    assert (1, 1) == lga.sim_calc_total_img_length_in_m(map_img, 0.01)


def test_sim_calc_total_img_length_in_m_real_map():
    cfg = Config()

    full_path = os.path.join("resource", "villa_holes_closed.png")

    upside_down_map_img = Image.open(full_path)
    map_img = img_axes2world_axes(upside_down_map_img)
    cell_size = 0.01
    lga = LocalGridImageSpoofer(cfg)
    Lx = map_img.shape[0] * cell_size
    Ly = map_img.shape[1] * cell_size
    assert (Lx, Ly) == lga.sim_calc_total_img_length_in_m(map_img, cell_size)


def test_sim_calc_total_img_length_in_m2():
    map_img = np.zeros((500, 100))
    cfg = Config()

    lga = LocalGridImageSpoofer(cfg)
    assert (5, 1) == lga.sim_calc_total_img_length_in_m(map_img, 0.01)


def test_calc_cells_per_m():
    map_img = np.zeros((100, 100))
    cfg = Config()

    lga = LocalGridImageSpoofer(cfg)
    assert (50, 50) == lga.sim_calc_cells_per_m(map_img, (2, 2))


def test_sim_calc_cell_size_in_m():
    map_img = np.zeros((400, 300))
    cfg = Config()

    lga = LocalGridImageSpoofer(cfg)
    assert (0.1, 0.1) == lga.sim_calc_cell_size_in_m(map_img, (40, 30))
