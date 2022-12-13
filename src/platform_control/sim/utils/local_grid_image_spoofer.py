import math
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from PIL import Image

from src.config import cfg


@dataclass
class ImageMapViewModel:
    upside_down_map_img_data: npt.NDArray
    map_img_rotated: npt.NDArray
    map_img_axes_alligned: npt.NDArray
    data: npt.NDArray


class LocalGridImageSpoofer:
    def __init__(self) -> None:
        self.set_map(cfg.MAP_PATH)

    def set_map(self, new_map_path: str) -> None:
        self.map_img = np.asarray(Image.open(new_map_path))

    def world_coord2global_pix_idx(
        self,
        x: float,
        y: float,
    ) -> tuple[int, int]:

        number_of_columns = self.map_img.shape[1]
        number_of_rows = self.map_img.shape[0]

        length_scale_of_map_in_x = cfg.TOTAL_MAP_LEN_M[0]
        length_scale_of_map_in_y = cfg.TOTAL_MAP_LEN_M[1]

        columns_per_meter = number_of_columns // length_scale_of_map_in_x
        rows_per_meter = number_of_rows // length_scale_of_map_in_y

        # (0,0) carthesian is in the middle of the image
        central_column = number_of_columns // 2
        central_row = number_of_rows // 2

        c = int(x * columns_per_meter) + central_column
        r = central_row - int(y * rows_per_meter)

        return r, c

    def sim_spoof_local_grid_from_img_world(
        self, agent_pos: tuple[float, float]
    ) -> npt.NDArray:
        HALF_LG_SIZE_IN_PIX = cfg.LG_NUM_CELLS // 2

        x, y = agent_pos  # world coords
        r, c = self.world_coord2global_pix_idx(x, y)

        r_start = r - HALF_LG_SIZE_IN_PIX
        r_end = r + HALF_LG_SIZE_IN_PIX
        c_start = c - HALF_LG_SIZE_IN_PIX
        c_end = c + HALF_LG_SIZE_IN_PIX

        local_grid_img = self.map_img[
            r_start:r_end,
            c_start:c_end,
        ]

        return local_grid_img
