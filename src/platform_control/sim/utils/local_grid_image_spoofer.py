from dataclasses import dataclass
import math

import numpy as np
import numpy.typing as npt
from PIL import Image

from src.config import cfg
from src.shared.topics import Topics
from src.utils.event import post_event, subscribe


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
        # upside_down_map_img = Image.open(new_map_path)
        # # self.map_img = upside_down_map_img
        # # upside_down_map_img.show()
        # upside_down_map_img_data = np.asarray(upside_down_map_img)

        # map_img_rotated = np.rot90(upside_down_map_img, axes=(1, 0))
        # # print(f"{map_img_rotated.shape=}")

        # map_img_axes_alligned = np.swapaxes(map_img_rotated, 0, 1)

        # post_event(
        #     str(Topics.IMAGE_MAPDEBUG_VIEW),
        #     ImageMapViewModel(
        #         upside_down_map_img_data, map_img_rotated, map_img_axes_alligned
        #     ),
        # )
        # self.map_img = map_img_axes_alligned
        # # self.map_img = img_axes2world_axes(upside_down_map_img_data)
        self.map_img = np.asarray(Image.open(new_map_path))

    def world_coord2global_pix_idx(
        self,
        x: float,
        y: float,
    ) -> tuple[int, int]:

    
        # Nx_pix = self.map_img.shape[1]
        # Ny_pix = self.map_img.shape[0]

        # x_map_length_scale = cfg.TOTAL_MAP_LEN_M[0]
        # y_map_length_scale = cfg.TOTAL_MAP_LEN_M[1]

        # x_pix_per_meter = Nx_pix // x_map_length_scale
        # y_pix_per_meter = Ny_pix // y_map_length_scale

        # # (0,0) carthesian is in the middle of the image
        # x_origin_pix_offset = Nx_pix // 2
        # y_origin_pix_offset = Ny_pix // 2

        # x_pix = x_pos * x_pix_per_meter - x_origin_pix_offset
        # y_pix = y_pos * y_pix_per_meter - y_origin_pix_offset

        # return x_pix, y_pix
        

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

    # def sim_spoof_local_grid_from_img_world(self, agent_pos: tuple) -> npt.NDArray:
    #     HALF_SIZE_IN_PIX = cfg.LG_NUM_CELLS // 2

    #     x, y = agent_pos  # world coords
    #     x, y = self.world_coord2global_pix_idx(x, y)

    #     # BUG:: cannot sample near edge of the image world_img.
    #     # BUG: rounding error can create uneven shaped local grid.
    #     local_grid_img = self.map_img[
    #         int(y - HALF_SIZE_IN_PIX) : int(y + HALF_SIZE_IN_PIX),
    #         int(x - HALF_SIZE_IN_PIX) : int(x + HALF_SIZE_IN_PIX),
    #     ]
    #     if not local_grid_img.shape[0:2] == (cfg.LG_NUM_CELLS, cfg.LG_NUM_CELLS):
    #         print(
    #             f"mismatch in localgrid shape {local_grid_img.shape}, lg num cells {cfg.LG_NUM_CELLS }"
    #         )

    #     return local_grid_img

    def sim_spoof_local_grid_from_img_world(self, agent_pos: tuple[float,float]) -> npt.NDArray:
        HALF_LG_SIZE_IN_PIX = cfg.LG_NUM_CELLS // 2

        x, y = agent_pos  # world coords
        r, c = self.world_coord2global_pix_idx(x, y)

        r_start = r - HALF_LG_SIZE_IN_PIX
        r_end = r + HALF_LG_SIZE_IN_PIX
        c_start = c - HALF_LG_SIZE_IN_PIX
        c_end = c + HALF_LG_SIZE_IN_PIX

        # print(f"{self.map_img.shape=}")

        local_grid_img = self.map_img[
            r_start:r_end,
            c_start:c_end,
        ]
        # print(f"{local_grid_img.shape=}")
        # post_event(
        #     str(Topics.IMAGE_MAPDEBUG_VIEW),
        #     ImageMapViewModel(
        #         upside_down_map_img_data, map_img_rotated, map_img_axes_alligned
        #     ),
        # )
        # local_grid_img = np.flip(local_grid_img, axis=0)

        return local_grid_img


# def img_axes2world_axes(upside_down_map_img: npt.NDArray):
#     # this function appently takes up most of the compute
#     map_img_rotated = np.rot90(upside_down_map_img, axes=(1, 0))
#     # print(f"{map_img_rotated.shape=}")

#     map_img_axes_alligned = np.swapaxes(map_img_rotated, 0, 1)

#     post_event(
#         str(Topics.IMAGE_MAPDEBUG_VIEW),
#         ImageMapViewModel(
#             upside_down_map_img_data, map_img_rotated, map_img_axes_alligned
#         ),
#     )

#     return map_img_axes_alligned
