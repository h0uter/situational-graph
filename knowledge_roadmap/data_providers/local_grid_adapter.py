import os
from PIL import Image

from knowledge_roadmap.utils.config import Configuration
from knowledge_roadmap.utils.coordinate_transforms import img_axes2world_axes
from knowledge_roadmap.data_providers.local_grid_image_spoofer import (
    LocalGridImageSpoofer,
)
from knowledge_roadmap.data_providers.manual_graph_world import ManualGraphWorld
from knowledge_roadmap.entities.abstract_agent import AbstractAgent
from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.data_providers.spot_agent import SpotAgent, get_local_grid


class LocalGridAdapter:
    def __init__(
        self, img_length_in_m: tuple, num_cells: int, cell_size_m: float,
    ):
        self.is_spoof_setup = False
        self.num_cells = num_cells
        self.cell_size_m = cell_size_m
        self.lg_length_in_m = num_cells * cell_size_m
        self.spoof_img_length_in_m = img_length_in_m

    def setup_spoofer(self):
        cfg = Configuration()
        upside_down_map_img = Image.open(cfg.full_path)
        self.map_img = img_axes2world_axes(upside_down_map_img)

        self.lgs = LocalGridImageSpoofer()
        self.is_spoof_setup = True

    def get_local_grid(self, agent: AbstractAgent) -> list:
        """
        Given the agent's position, return the local grid image around the agent.
        
        :return: The local grid.
        """

        # obtain lg from real robot or simulated bot
        if isinstance(agent, SpotAgent):
            # here comes calls to the spot API
            return get_local_grid(agent)

        elif isinstance(agent, Agent):
            if not self.is_spoof_setup:
                self.setup_spoofer()

            return self.lgs.sim_spoof_local_grid_from_img_world(
                agent.pos, self.map_img, self.num_cells, self.spoof_img_length_in_m
            )

        else:
            raise Exception("Agent type not recognized")

