import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
from numpy import typing as npt

from src.config import cfg
from src.platform_autonomy.state.local_grid import LocalGrid
from src.core.topics import Topics
from src.core.event_system import post_event


class FrontierSamplingStrategy(ABC):
    """Base class for frontier sampling strategies."""

    @abstractmethod
    def sample_frontiers(self, local_grid: LocalGrid) -> list[tuple[int, int]]:
        """Sample frontiers from the local grid."""
        pass


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
            elif collision_point:
                collision_cell = local_grid.xy2rc(collision_point)
                collision_cells.append(collision_cell)

        post_event(
            Topics.FRONTIER_SAMPLING,
            FrontierSamplingViewModel(
                local_grid_img=local_grid.img_data,
                new_frontier_cells=candidate_frontiers,
                collision_cells=collision_cells,
            ),
        )

        return candidate_frontiers


@dataclass
class FrontierSamplingViewModel:
    local_grid_img: npt.NDArray
    new_frontier_cells: list[tuple[int, int]]
    collision_cells: list[tuple[int, int]]
