import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
import numpy.typing as npt
from skimage import draw

from src.config import Scenario, cfg
from src.shared.topics import Topics
from src.utils.event import post_event


@dataclass
class FrontierSamplingViewModel:
    local_grid_img: npt.NDArray
    new_frontier_cells: list[tuple[int, int]]
    collision_cells: list[tuple[int, int]]


class LocalGrid:
    def __init__(self, world_pos: tuple, img_data: npt.NDArray):
        self._log = logging.getLogger(__name__)

        # Where the robot was when the lg image was obtained
        self.lg_xy = world_pos
        self.data = img_data  # r,c with origin top left (numpy convention)

        self.lg_length_in_m = cfg.LG_LENGTH_IN_M
        self.meter_per_cell = cfg.LG_CELL_SIZE_M
        self.LG_LENGTH_AS_NUMBER_OF_CELLS = int(
            self.lg_length_in_m / self.meter_per_cell
        )

        self.PIXEL_OCCUPIED_THRESHOLD = 220

        if not self.data.shape[0:2] == (
            self.LG_LENGTH_AS_NUMBER_OF_CELLS,
            self.LG_LENGTH_AS_NUMBER_OF_CELLS,
        ):
            self._log.warning(
                f"ERROR: data.shape = {self.data.shape[0:2]}, length_num_cells = {self.LG_LENGTH_AS_NUMBER_OF_CELLS}"
            )

    def is_within_local_grid(self, coords: tuple[float, float]) -> bool:
        """
        Check if the world coordinates are within the local grid.
        """
        if (
            coords[0] < self.lg_xy[0] - self.lg_length_in_m / 2
            or coords[0] > self.lg_xy[0] + self.lg_length_in_m / 2
            or coords[1] < self.lg_xy[1] - self.lg_length_in_m / 2
            or coords[1] > self.lg_xy[1] + self.lg_length_in_m / 2
        ):
            return False
        return True

    def xy2rc(self, xy: tuple[float, float]) -> tuple[int, int]:
        """
        Convert the world coordinates to the cell indices of the local grid.
        assumes that the world coordinate falls within the local grid.
        """

        if not self.is_within_local_grid(xy):
            raise ValueError(f"World coordinate {xy} is not within the local grid.")


        # x = self.lg_xy[0] + (rc[1] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2) * self.meter_per_cell
        # x - self.lg_xy[0] =  (rc[1] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2) * self.meter_per_cell
        # (x - self.lg_xy[0]) / self.meter_per_cell =  rc[1] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2
        # (x - self.lg_xy[0]) / self.meter_per_cell + self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2=  rc[1] 


        if cfg.SCENARIO == Scenario.REAL:
            c = int((xy[0] - self.lg_xy[0]) / self.meter_per_cell + self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2)

            # y = self.lg_xy[1] + (rc[0] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2) * self.meter_per_cell
            # y - self.lg_xy[1] = (rc[0] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2) * self.meter_per_cell
            # (y - self.lg_xy[1])/self.meter_per_cell = rc[0] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2
            # (y - self.lg_xy[1])/self.meter_per_cell  + self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2 = rc[0]
            r = int((xy[1] - self.lg_xy[1])/self.meter_per_cell  + self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2)

        
        else:
            c = int((xy[0] - self.lg_xy[0] + self.lg_length_in_m / 2) / self.meter_per_cell)
            r = int(
                (-xy[1] + self.lg_xy[1] + self.lg_length_in_m / 2) / self.meter_per_cell
            )

        return r, c

    def rc2xy(self, rc: tuple[int, int]) -> tuple[float, float]:
        """
        Convert the cell indices to the world coordinates.
        """

        # somehow switched between spot grid and my own grid
        # FIXME: need to make sim equal to spot
        # if cfg.SCENARIO == Scenario.REAL:
        #     x_coord = (
        #         self.world_pos[0]
        #         + (idxs[0] - self.length_num_cells // 2) * self.cell_size_in_m
        #     )
        #     y_coord = (
        #         self.world_pos[1]
        #         + (idxs[1] - self.length_num_cells // 2) * self.cell_size_in_m
        #     )
        # else:
        #     x_coord = (
        #         self.world_pos[0] + idxs[1] * self.cell_size_in_m - self.length_in_m / 2
        #     )
        #     y_coord = (
        #         self.world_pos[1] + idxs[0] * self.cell_size_in_m - self.length_in_m / 2
        #     )
        # return x_coord, y_coord


        if cfg.SCENARIO == Scenario.REAL:
            x = self.lg_xy[0] + (rc[1] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2) * self.meter_per_cell
            y = self.lg_xy[1] + (rc[0] - self.LG_LENGTH_AS_NUMBER_OF_CELLS / 2) * self.meter_per_cell
        else:
            x = self.lg_xy[0] - self.lg_length_in_m / 2 + rc[1] * self.meter_per_cell
            y = self.lg_xy[1] + self.lg_length_in_m / 2 - rc[0] * self.meter_per_cell

        # c = int((xy[0] - self.lg_xy[0] + self.lg_length_in_m / 2) / self.meter_per_cell)
        # c * self.meter_per_cell = xy[0] - self.lg_xy[0] + self.lg_length_in_m / 2
        # c * self.meter_per_cell +  self.lg_xy[0] = xy[0] + self.lg_length_in_m / 2
        # xy[0] = c * self.meter_per_cell +  self.lg_xy[0] - self.lg_length_in_m / 2 


        # r = -xy[1] + self.lg_xy[1] + self.lg_length_in_m / 2) / self.meter_per_cell
        # r * self.meter_per_cell = -xy[1] + self.lg_xy[1] + self.lg_length_in_m / 2
        # xy[1] + r * self.meter_per_cell = + self.lg_xy[1] + self.lg_length_in_m / 2
        # xy[1]  = + self.lg_xy[1] + self.lg_length_in_m / 2 - r * self.meter_per_cell

        return x, y

    # def _construct_line_on_image_matrix(
    #     self, r0c0: tuple[int, int], r1c1: tuple[int, int]
    # ) -> tuple:
    #     """follows numpy conventions"""
    #     line_row_cells, line_column_cells = draw.line(
    #         int(r0c0[0]), int(r0c0[1]), int(r1c1[0]), int(r1c1[1])
    #     )

    #     return line_row_cells, line_column_cells

    # def is_collision_free_straight_line_between_cells(
    #     self, at: tuple[int, int], to: tuple[int, int]
    # ) -> tuple[bool, Optional[tuple[float, float]]]:
    #     # FIXME: make my loaded images consistent with the spot local grid somehow
    #     if cfg.SCENARIO == Scenario.REAL:
    #         # FIXME: spot obstacle map has rr and cc flipped somehow
    #         rr, cc = self._get_cells_under_line(at, to)
    #         for r, c in zip(rr, cc):
    #             if np.greater(
    #                 self.data[r, c][0:2],
    #                 [self.pixel_occupied_treshold, self.pixel_occupied_treshold],
    #             ).any():
    #                 x, y = self.cell_idx2world_coords((c, r))
    #                 collision_point = (x, y)
    #                 # print(f"collision at : {collision_point}")

    #                 return False, collision_point
    #         return True, None

    #     if cfg.SCENARIO == Scenario.SIM_MAZE_MEDIUM:
    #         rr, cc = self._get_cells_under_line(at, to)
    #         for r, c in zip(rr, cc):
    #             if np.greater(
    #                 self.data[c, r][3],
    #                 [self.pixel_occupied_treshold],
    #             ).any():
    #                 x, y = self.cell_idx2world_coords((c, r))
    #                 collision_point = (x, y)

    #                 return False, collision_point
    #         return True, None

    #     else:
    #         rr, cc = self._get_cells_under_line(at, to)
    #         for r, c in zip(rr, cc):
    #             if np.less(
    #                 self.data[c, r],
    #                 [
    #                     self.pixel_occupied_treshold,
    #                     self.pixel_occupied_treshold,
    #                     self.pixel_occupied_treshold,
    #                     self.pixel_occupied_treshold,
    #                 ],
    #             ).any():
    #                 x, y = self.cell_idx2world_coords((c, r))
    #                 collision_point = (x, y)

    #                 return False, collision_point
    #         return True, None

    def is_collision_free_straight_line_between_cells(
        self, r0c0: tuple[int, int], r1c1: tuple[int, int]
    ) -> tuple[bool, Optional[tuple[float, float]]]:

        rr, cc = draw.line(int(r0c0[0]), int(r0c0[1]), int(r1c1[0]), int(r1c1[1]))

        if cfg.SCENARIO == Scenario.REAL:
            for r, c in zip(rr, cc):
                if np.greater(
                    self.data[r, c][0:2],
                    [self.PIXEL_OCCUPIED_THRESHOLD, self.PIXEL_OCCUPIED_THRESHOLD],
                ).any():
                    x, y = self.rc2xy((r, c))
                    collision_point = (x, y)

                    return False, collision_point
            return True, None
        else:
            for r, c in zip(rr, cc):
                if np.less(
                    self.data[r, c],
                    [
                        self.PIXEL_OCCUPIED_THRESHOLD,
                        self.PIXEL_OCCUPIED_THRESHOLD,
                        self.PIXEL_OCCUPIED_THRESHOLD,
                        self.PIXEL_OCCUPIED_THRESHOLD,
                    ],
                ).any():
                    x, y = self.rc2xy((r, c))
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
            x_center = local_grid.LG_LENGTH_AS_NUMBER_OF_CELLS // 2
            y_center = local_grid.LG_LENGTH_AS_NUMBER_OF_CELLS // 2

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
                r0c0=(x, y),
                r1c1=(x_sample, y_sample),
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
        We start in cell coords
        """
        collision_cells = []
        candidate_frontiers = []
        for angle in np.linspace(0, 2 * np.pi, cfg.N_SAMPLES):

            SAMPLE_RADIUS = cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS
            c_central = math.floor(local_grid.LG_LENGTH_AS_NUMBER_OF_CELLS // 2)
            r_central = math.floor(local_grid.LG_LENGTH_AS_NUMBER_OF_CELLS // 2)

            # so the sample does not match the r,c on the image... but it does not matter
            r_sample = int(c_central + SAMPLE_RADIUS * np.sin(angle))
            c_sample = int(r_central + SAMPLE_RADIUS * np.cos(angle))

            (
                sample_valid,
                collision_point,
            ) = local_grid.is_collision_free_straight_line_between_cells(
                # at=(central_column, central_row),
                r0c0=(r_central, c_central),
                r1c1=(r_sample, c_sample),
            )

            if sample_valid:
                # candidate_frontiers.append((c_sample, r_sample))  # this is the wrong way around and it becomes apparent when we viz it
                candidate_frontiers.append((r_sample, c_sample))
            else:
                collision_cell = local_grid.xy2rc(collision_point)
                collision_cells.append(collision_cell)

        post_event(
            str(Topics.FRONTIER_SAMPLING),
            FrontierSamplingViewModel(
                local_grid_img=local_grid.data,
                new_frontier_cells=candidate_frontiers,
                collision_cells=collision_cells,
            ),
        )

        return candidate_frontiers
