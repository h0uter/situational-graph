import math
from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

from src.config import cfg
from src.platform_state.local_grid import FrontierSamplingViewModel, LocalGrid
from src.shared.topics import Topics
from src.utils.event import post_event


class FrontierSamplingStrategy(ABC):
    """Base class for frontier sampling strategies."""

    @abstractmethod
    def sample_frontiers(self, local_grid: LocalGrid) -> list[tuple[int, int]]:
        """Sample frontiers from the local grid."""
        pass


class LOSFrontierSamplingStrategy(FrontierSamplingStrategy):
    def sample_frontiers(
        self,
        local_grid: LocalGrid,
    ) -> list[tuple[int, int]]:
        """
        Given a local grid, sample N points around a given point, and return the sampled points.
        """
        candidate_frontiers: list = []
        radius = cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS
        num_frontiers_to_sample: int = cfg.N_SAMPLES

        while len(candidate_frontiers) < num_frontiers_to_sample:
            x_center = local_grid.LG_LEN_IN_N_CELLS // 2
            y_center = local_grid.LG_LEN_IN_N_CELLS // 2

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
    ) -> list[tuple[int, int]]:
        """
        Given a local grid, sample N_SAMPLES points in a circle around the agent, and return the sampled frontiers.
        We start in cell coords
        """
        collision_cells = []
        candidate_frontiers = []
        for angle in np.linspace(0, 2 * np.pi, cfg.N_SAMPLES):

            SAMPLE_RADIUS = cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS
            c_central = math.floor(local_grid.LG_LEN_IN_N_CELLS // 2)
            r_central = math.floor(local_grid.LG_LEN_IN_N_CELLS // 2)

            # so the sample does not match the r,c on the image... but it does not matter
            r_sample = int(c_central + SAMPLE_RADIUS * np.sin(angle))
            c_sample = int(r_central + SAMPLE_RADIUS * np.cos(angle))

            (
                sample_valid,
                collision_point,
            ) = local_grid.is_collision_free_straight_line_between_cells(
                r0c0=(r_central, c_central),
                r1c1=(r_sample, c_sample),
            )

            if sample_valid:
                candidate_frontiers.append((r_sample, c_sample))
            else:
                collision_cell = local_grid.xy2rc(collision_point)
                collision_cells.append(collision_cell)

        post_event(
            str(Topics.FRONTIER_SAMPLING),
            FrontierSamplingViewModel(
                local_grid_img=local_grid.img_data,
                new_frontier_cells=candidate_frontiers,
                collision_cells=collision_cells,
            ),
        )

        return candidate_frontiers
