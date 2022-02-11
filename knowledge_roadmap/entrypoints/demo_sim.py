import matplotlib.pyplot as plt
import os
from PIL import Image

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


def init_entities():
    # upside_down_map_img = Image.open(cfg.full_path)
    # map_img = img_axes2world_axes(upside_down_map_img)
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

    gui, agent, krm, lga, exploration_usecase = init_entities()

    exploration_completed = False
    while agent.no_more_frontiers == False:

        local_grid_img = lga.get_local_grid(agent)

        lg = LocalGrid(
            world_pos=agent.pos,
            data=local_grid_img,
            length_in_m=cfg.lg_length_in_m,
            cell_size_in_m=cfg.lg_cell_size_m,
        )

        exploration_completed = exploration_usecase.run_exploration_step(
            agent, krm, lg
        )
        if exploration_completed:
            continue
        if plotting == "all" or plotting == "intermediate only":
            close_nodes = krm.get_nodes_of_type_in_margin(
                lg.world_pos, cfg.lg_length_in_m / 2, "waypoint"
            )
            points = [krm.get_node_data_by_idx(node)["pos"] for node in close_nodes]
            if points:
                gui.draw_collision_line_to_points_in_world_coord(points, lg)
            
            gui.figure_update(krm, agent, lg)

        print(f"step= {step}")
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
