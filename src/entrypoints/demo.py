import matplotlib.pyplot as plt
import logging

from src.entities.simulated_agent import SimulatedAgent
from src.data_providers.spot_agent import SpotAgent


from src.data_providers.manual_graph_world import ManualGraphWorld
from src.entrypoints.vizualizer import Vizualizer
from src.usecases.exploration_usecase import ExplorationUsecase
from src.data_providers.local_grid_adapter import LocalGridAdapter
from src.entities.knowledge_roadmap import KnowledgeRoadmap
from src.entities.local_grid import LocalGrid
from src.utils.configuration import Configuration
from src.utils.coordinate_transforms import img_axes2world_axes

import matplotlib

matplotlib.use("Tkagg")

############################################################################################
# DEMONSTRATIONS
############################################################################################


def init_spot_entities():
    gui = Vizualizer()
    # agent = Agent(start_pos=cfg.AGENT_START_POS)
    agent = SpotAgent()
    krm = KnowledgeRoadmap(start_pos=agent.pos)
    lga = LocalGridAdapter()
    exploration_usecase = ExplorationUsecase(agent)

    return gui, agent, krm, lga, exploration_usecase


def init_sim_entities():
    gui = Vizualizer()
    agent = SimulatedAgent(start_pos=cfg.AGENT_START_POS)
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
    while exploration_usecase.no_more_frontiers == False: # TODO: no more frontiers should be exploration atttribute

        lg_img = lga.get_local_grid(agent)

        lg = LocalGrid(
            world_pos=agent.pos,
            img_data=lg_img,
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
