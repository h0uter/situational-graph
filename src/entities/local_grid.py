import logging
from typing import Optional

import numpy as np
import numpy.typing as npt
from skimage import draw
from src.utils.config import Config, Scenario


class LocalGrid:
    def __init__(self, world_pos: tuple, img_data: npt.NDArray, cfg: Config = Config()):
        self._logger = logging.getLogger(__name__)

        self.world_pos = world_pos
        self.data = img_data
        self.cfg = cfg
        self.length_in_m = cfg.LG_LENGTH_IN_M
        self.cell_size_in_m = cfg.LG_CELL_SIZE_M
        self.length_num_cells = int(self.length_in_m / self.cell_size_in_m)

        self.pixel_occupied_treshold = 220
        self.sample_ring_width = cfg.SAMPLE_RING_WIDTH

        if not self.data.shape[0:2] == (self.length_num_cells, self.length_num_cells):
            self._logger.warning(
                f"ERROR: data.shape = {self.data.shape[0:2]}, length_num_cells = {self.length_num_cells}"
            )

    # XXX: this function is not used
    def is_inside(self, world_pos: tuple) -> bool:
        """
        Check if the world position is inside the local grid.
        """
        if world_pos[0] < self.world_pos[0] - self.length_in_m / 2:
            return False
        if world_pos[0] > self.world_pos[0] + self.length_in_m / 2:
            return False
        if world_pos[1] < self.world_pos[1] - self.length_in_m / 2:
            return False
        if world_pos[1] > self.world_pos[1] + self.length_in_m / 2:
            return False
        return True

    def world_coords2cell_idxs(self, coords: tuple) -> tuple:
        """
        Convert the world coordinates to the cell indices of the local grid.
        """
        x_idx = int(
            (coords[0] - self.world_pos[0] + self.length_in_m / 2) / self.cell_size_in_m
        )
        y_idx = int(
            (coords[1] - self.world_pos[1] + self.length_in_m / 2) / self.cell_size_in_m
        )
        return x_idx, y_idx

    def _cell_idx2world_coords(self, idxs: tuple) -> tuple:
        """
        Convert the cell indices to the world coordinates.
        """
        # somehow switched between spot grid and my own grid
        # FIXME: need to make sim equal to spot
        if self.cfg.SCENARIO == Scenario.REAL:
            x_coord = (
                # self.world_pos[0] + idxs[0] * self.cell_size_in_m - self.length_in_m / 2
                self.world_pos[0]
                + (idxs[0] - self.length_num_cells // 2) * self.cell_size_in_m
            )
            y_coord = (
                # self.world_pos[1] + idxs[1] * self.cell_size_in_m - self.length_in_m / 2
                self.world_pos[1]
                + (idxs[1] - self.length_num_cells // 2) * self.cell_size_in_m
            )
        else:
            x_coord = (
                self.world_pos[0] + idxs[1] * self.cell_size_in_m - self.length_in_m / 2
            )
            y_coord = (
                self.world_pos[1] + idxs[0] * self.cell_size_in_m - self.length_in_m / 2
            )
        return x_coord, y_coord

    # # TODO: optimize this function for speed
    # def cell_idxs2world_coords(self, idxs: tuple) -> tuple:
    #     """
    #     Convert the cell indices to the world coordinates.
    #     """
    #     x_coords = []
    #     y_coords = []
    #     for i in range(len(idxs[0])):
    #         x_coords.append(
    #             self.world_pos[0]
    #             + idxs[1][i] * self.cell_size_in_m
    #             - self.length_in_m / 2
    #         )
    #         y_coords.append(
    #             self.world_pos[1]
    #             + idxs[0][i] * self.cell_size_in_m
    #             - self.length_in_m / 2
    #         )
    #     return x_coords, y_coords

    def _get_cells_under_line(self, a: tuple, b: tuple) -> tuple:
        rr, cc = draw.line(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

        return rr, cc

    def is_collision_free_straight_line_between_cells(
        self, at: tuple, to: tuple
    ) -> tuple:
        # FIXME: make my loaded images consistent with the spot local grid somehow
        if self.cfg.SCENARIO == Scenario.REAL:
            # FIXME: spot obstacle map has rr and cc flipped somehow
            rr, cc = self._get_cells_under_line(at, to)
            for r, c in zip(rr, cc):
                if np.greater(
                    self.data[r, c][0:2],
                    [self.pixel_occupied_treshold, self.pixel_occupied_treshold],
                ).any():
                    x, y = self._cell_idx2world_coords((c, r))
                    collision_point = (x, y)
                    # print(f"collision at : {collision_point}")

                    return False, collision_point
            return True, None

        if self.cfg.SCENARIO == Scenario.SIM_MAZE_MEDIUM:
            rr, cc = self._get_cells_under_line(at, to)
            for r, c in zip(rr, cc):
                if np.greater(
                    self.data[c, r][3], [self.pixel_occupied_treshold],
                ).any():
                    x, y = self._cell_idx2world_coords((c, r))
                    collision_point = (x, y)

                    return False, collision_point
            return True, None

        else:
            rr, cc = self._get_cells_under_line(at, to)
            for r, c in zip(rr, cc):
                if np.less(
                    self.data[c, r],
                    [
                        self.pixel_occupied_treshold,
                        self.pixel_occupied_treshold,
                        self.pixel_occupied_treshold,
                        self.pixel_occupied_treshold,
                    ],
                ).any():
                    x, y = self._cell_idx2world_coords((c, r))
                    collision_point = (x, y)

                    return False, collision_point
            return True, None

    def _sample_cell_around_other_cell(self, x: int, y: int, radius: int) -> Optional[tuple]:
        sample_valid = False
        attempts = 0
        x_sample, y_sample = None, None
        while not sample_valid and attempts < 100:
            r = radius * np.sqrt(
                np.random.uniform(low=1 - self.sample_ring_width, high=1)
            )
            theta = np.random.random() * 2 * np.pi

            x_sample = int(x + r * np.cos(theta))
            y_sample = int(y + r * np.sin(theta))

            sample_valid, _ = self.is_collision_free_straight_line_between_cells(
                at=(x, y), to=(x_sample, y_sample),
            )
            attempts += 1

        if sample_valid:
            return x_sample, y_sample
        else:
            # raise Exception("Could not sample a valid cell around other cell")
            self._logger.warning("Could not sample a valid cell around other cell")
            # raise Exception("Could not sample a valid cell around other cell")

    # TODO: make this a a strategy
    # alternatice strategy should be sampling with dijkstra on a lattice graph.
    def los_sample_frontiers_on_cellmap(
        self, radius: int, num_frontiers_to_sample: int
    ) -> npt.NDArray:
        """
        Given a local grid, sample N points around a given point, and return the sampled points.
        """
        candidate_frontiers = []
        while len(candidate_frontiers) < num_frontiers_to_sample:
            x_center = self.length_num_cells // 2
            y_center = self.length_num_cells // 2

            sample = self._sample_cell_around_other_cell(
                x_center, y_center, radius=radius,
            )
            if sample:
                x_sample, y_sample = sample

                candidate_frontiers.append((y_sample, x_sample))
            else:
                self._logger.warning("sample_cell_around_other_cell() returned None")
                break
            # candidate_frontiers.append((x_sample, y_sample))

        # FIXME: this is hella random
        candidate_frontiers = np.array(candidate_frontiers).astype(int)

        return candidate_frontiers
