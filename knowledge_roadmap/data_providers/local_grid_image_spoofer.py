

from multiprocessing.context import SpawnProcess


class LocalGridImageSpoofer():
    def __init__(self) -> None:
        pass


        def sim_calc_total_img_length_in_m(
        self, whole_damn_img, cell_size_in_m: float
    ) -> tuple:
        total_img_length_in_m_x = whole_damn_img.shape[0] * cell_size_in_m
        total_img_length_in_m_y = whole_damn_img.shape[1] * cell_size_in_m
        return total_img_length_in_m_x, total_img_length_in_m_y

    def sim_calc_cells_per_m(
        self, whole_damn_img, total_img_length_in_m: tuple
    ) -> tuple:
        """
        Given the total length of the image in meters, return the cell size in pixels.
        
        :param whole_damn_img: the image
        :param total_img_length_in_m: the length of the image in meters
        :return: The cell size in pixels.
        """
        Nx_cells = whole_damn_img.shape[1]
        Ny_cells = whole_damn_img.shape[0]

        x_cells_per_meter = Nx_cells // total_img_length_in_m[0]
        y_cells_per_meter = Ny_cells // total_img_length_in_m[1]

        return x_cells_per_meter, y_cells_per_meter

    def sim_calc_cell_size_in_m(
        self, whole_damn_img, total_img_length_in_m: tuple
    ) -> tuple:
        """
        Given the total length of the image in meters, return the cell size in meters.
        
        :param whole_damn_img: the image
        :param total_img_length_in_m: the length of the image in meters
        :return: The cell size in meters.
        """
        Nx_cells = whole_damn_img.shape[0]
        Ny_cells = whole_damn_img.shape[1]

        cell_length_x = total_img_length_in_m[0] / Nx_cells
        cell_length_y = total_img_length_in_m[1] / Ny_cells

        return cell_length_x, cell_length_y


    def world_coord2global_pix_idx(self, map_img:list, x_pos:float, y_pos:float, spoof_img_length_in_m: tuple) -> tuple:
        Nx_pix = map_img.shape[1]
        Ny_pix = map_img.shape[0]

        x_map_length_scale = spoof_img_length_in_m[0]
        y_map_length_scale = spoof_img_length_in_m[1]

        x_pix_per_meter = Nx_pix // x_map_length_scale
        y_pix_per_meter = Ny_pix // y_map_length_scale

        x_origin_pix_offset = Nx_pix // 2
        y_origin_pix_offset = Ny_pix // 2

        x_pix = x_pos * x_pix_per_meter - x_origin_pix_offset
        y_pix = y_pos * y_pix_per_meter - y_origin_pix_offset

        return x_pix, y_pix

    def sim_spoof_local_grid_from_img_world(self, agent_pos: tuple, img: list, num_cells: int, spoof_img_length_in_m: tuple) -> list:
        x, y = agent_pos  # world coords
        x, y = self.world_coord2global_pix_idx(img, x, y, spoof_img_length_in_m)
        half_size_in_pix = num_cells // 2
        
        # BUG:: cannot sample near edge of the image world_img.
        # BUG: rounding error can create uneven shaped local grid.
        local_grid_img = img[
            int(y - half_size_in_pix) : int(y + half_size_in_pix),
            int(x - half_size_in_pix) : int(x + half_size_in_pix),
        ]
        if not local_grid_img.shape[0:2] == (num_cells, num_cells):
            print(f"mismatch in localgrid shape {local_grid_img.shape=}, lg num cells {num_cells =}")

        return local_grid_img

