import logging
import math
from abc import ABC, abstractmethod
from typing import Optional, Sequence

import numpy as np
import numpy.typing as npt
from skimage import draw

from src.config import Scenario, cfg


class LocalGrid:
    def __init__(self, world_pos: tuple, img_data: npt.NDArray):
        self._log = logging.getLogger(__name__)

        self.world_pos = world_pos
        self.data = img_data
        self.length_in_m = cfg.LG_LENGTH_IN_M
        self.cell_size_in_m = cfg.LG_CELL_SIZE_M
        self.length_num_cells = int(self.length_in_m / self.cell_size_in_m)

        self.pixel_occupied_treshold = 220

        if not self.data.shape[0:2] == (self.length_num_cells, self.length_num_cells):
            self._log.warning(
                f"ERROR: data.shape = {self.data.shape[0:2]}, length_num_cells = {self.length_num_cells}"
            )

    def world_coords2cell_idxs(self, coords: tuple[float, float]) -> tuple[int, int]:
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

    def cell_idx2world_coords(self, idxs: tuple[int, int]) -> tuple[float, float]:
        """
        Convert the cell indices to the world coordinates.
        """
        # somehow switched between spot grid and my own grid
        # FIXME: need to make sim equal to spot
        if cfg.SCENARIO == Scenario.REAL:
            x_coord = (
                self.world_pos[0]
                + (idxs[0] - self.length_num_cells // 2) * self.cell_size_in_m
            )
            y_coord = (
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

    def _get_cells_under_line(self, a: tuple[int, int], b: tuple[int, int]) -> tuple:
        line_row_cells, line_column_cells = draw.line(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

        return line_row_cells, line_column_cells

    def is_collision_free_straight_line_between_cells(
        self, at: tuple[int, int], to: tuple[int, int]
    ) -> tuple[bool, Optional[tuple[float, float]]]:
        # FIXME: make my loaded images consistent with the spot local grid somehow
        if cfg.SCENARIO == Scenario.REAL:
            # FIXME: spot obstacle map has rr and cc flipped somehow
            rr, cc = self._get_cells_under_line(at, to)
            for r, c in zip(rr, cc):
                if np.greater(
                    self.data[r, c][0:2],
                    [self.pixel_occupied_treshold, self.pixel_occupied_treshold],
                ).any():
                    x, y = self.cell_idx2world_coords((c, r))
                    collision_point = (x, y)
                    # print(f"collision at : {collision_point}")

                    return False, collision_point
            return True, None

        if cfg.SCENARIO == Scenario.SIM_MAZE_MEDIUM:
            rr, cc = self._get_cells_under_line(at, to)
            for r, c in zip(rr, cc):
                if np.greater(
                    self.data[c, r][3],
                    [self.pixel_occupied_treshold],
                ).any():
                    x, y = self.cell_idx2world_coords((c, r))
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
                    x, y = self.cell_idx2world_coords((c, r))
                    collision_point = (x, y)

                    return False, collision_point
            return True, None


class FrontierSamplingStrategy(ABC):
    """Base class for frontier sampling strategies."""

    @abstractmethod
    def sample_frontiers(self, local_grid: LocalGrid) -> npt.NDArray:
        """Sample frontiers from the local grid."""
        pass


class LOSFrontierSamplingStrategy(FrontierSamplingStrategy):
    def sample_frontiers(
        self,
        local_grid: LocalGrid,
    ) -> Sequence[tuple[int, int]]:
        """
        Given a local grid, sample N points around a given point, and return the sampled points.
        """
        radius: int = cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS
        num_frontiers_to_sample: int = cfg.N_SAMPLES

        candidate_frontiers = []
        while len(candidate_frontiers) < num_frontiers_to_sample:
            x_center = local_grid.length_num_cells // 2
            y_center = local_grid.length_num_cells // 2

            sample = self._sample_cell_in_donut_around_other_cell(
                local_grid, x_center, y_center, radius
            )
            if sample:
                x_sample, y_sample = sample

                candidate_frontiers.append((y_sample, x_sample))
            else:
                break

        return candidate_frontiers

    def _sample_cell_in_donut_around_other_cell(
        self, local_grid: LocalGrid, x: int, y: int, radius: int
    ) -> Optional[tuple[int, int]]:
        sample_valid = False
        attempts = 0
        x_sample, y_sample = None, None
        while not sample_valid and attempts < 100:
            r = radius * np.sqrt(
                np.random.uniform(low=1 - cfg.SAMPLE_RING_WIDTH, high=1)
            )
            theta = np.random.random() * 2 * np.pi

            x_sample = int(x + r * np.cos(theta))
            y_sample = int(y + r * np.sin(theta))

            sample_valid, _ = local_grid.is_collision_free_straight_line_between_cells(
                at=(x, y),
                to=(x_sample, y_sample),
            )
            attempts += 1

        if sample_valid:
            return x_sample, y_sample
        else:
            local_grid._log.warning("Could not sample a valid cell around other cell")


class AngularLOSFrontierSamplingStrategy(FrontierSamplingStrategy):
    def sample_frontiers(
        self,
        local_grid: LocalGrid,
    ) -> Sequence[tuple[int, int]]:
        """
        Given a local grid, sample N_SAMPLES points in a circle around the agent, and return the sampled frontiers.
        """

        candidate_frontiers = []
        for angle in np.linspace(0, 2 * np.pi, cfg.N_SAMPLES):

            r = cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS
            x_center = math.floor(local_grid.length_num_cells // 2)
            y_center = math.floor(local_grid.length_num_cells // 2)

            x_sample = int(x_center + r * np.cos(angle))
            y_sample = int(y_center + r * np.sin(angle))

            sample_valid, _ = local_grid.is_collision_free_straight_line_between_cells(
                at=(x_center, y_center),
                to=(x_sample, y_sample),
            )

            if sample_valid:
                candidate_frontiers.append((y_sample, x_sample))

        return candidate_frontiers
