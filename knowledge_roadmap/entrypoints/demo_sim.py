import matplotlib.pyplot as plt
# import os
# from PIL import Image
import logging

from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.data_providers.spot_agent import SpotAgent


from knowledge_roadmap.data_providers.manual_graph_world import ManualGraphWorld
from knowledge_roadmap.entrypoints.vizualizer import Vizualizer
from knowledge_roadmap.usecases.exploration_usecase import ExplorationUsecase
from knowledge_roadmap.data_providers.local_grid_adapter import LocalGridAdapter
from knowledge_roadmap.entities.knowledge_roadmap import KnowledgeRoadmap
from knowledge_roadmap.entities.local_grid import LocalGrid
from knowledge_roadmap.utils.config import Configuration
from knowledge_roadmap.utils.coordinate_transforms import img_axes2world_axes

import matplotlib

matplotlib.use("Tkagg")

############################################################################################
# DEMONSTRATIONS
############################################################################################


def init_sim_entities():
    gui = Vizualizer()
    agent = Agent(start_pos=cfg.agent_start_pos)
    krm = KnowledgeRoadmap(start_pos=agent.pos)
    lga = LocalGridAdapter()
    exploration_usecase = ExplorationUsecase(agent)

    return gui, agent, krm, lga, exploration_usecase


def exploration_with_sampling_viz(plotting="none"):
    # this is the prior image of the villa we can include for visualization purposes
    # It is different from the map we use to emulate the local grid.
    step = 0
    my_logger = logging.getLogger(__name__)

    gui, agent, krm, lga, exploration_usecase = init_sim_entities()

    exploration_completed = False
    while agent.no_more_frontiers == False: # TODO: no more frontiers should be exploration atttribute

        local_grid_img = lga.get_local_grid(agent)

        lg = LocalGrid(
            world_pos=agent.pos,
            data=local_grid_img,
            length_in_m=cfg.lg_length_in_m,
            cell_size_in_m=cfg.lg_cell_size_m,
        )

        exploration_completed = exploration_usecase.run_exploration_step(agent, krm, lg)
        
        if exploration_completed:
            continue

        if plotting == "all" or plotting == "intermediate only":            
            gui.figure_update(krm, agent, lg)

        my_logger.info(f"step = {step}")
        step += 1

    if plotting == "result only" or plotting == "all":
        gui.figure_update(krm, agent, lg)

        plt.ioff()
        plt.show()
        return exploration_completed


if __name__ == "__main__":
    cfg = Configuration()

    # exploration_with_sampling_viz("result only")
    # exploration_with_sampling_viz("none")
    exploration_with_sampling_viz("all")
