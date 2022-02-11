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

def exploration_spot(plotting="none"):
    # this is the prior image of the villa we can include for visualization purposes
    # It is different from the map we use to emulate the local grid.
    cfg = Configuration()
    step = 0

    # FIXME: full path is irrelavant for spot case 
    if cfg.FULL_PATH:
        upside_down_map_img = Image.open(cfg.FULL_PATH)
        map_img = img_axes2world_axes(upside_down_map_img)
    world = ManualGraphWorld()
    gui = Vizualizer(
        origin_x_offset=cfg.TOTAL_MAP_LEN_M_X / 2,
        origin_y_offset=cfg.TOTAL_MAP_LEN_M_Y / 2,
    )

    # gui.preview_graph_world(world)
    # agent = Agent(start_pos=cfg.agent_start_pos)
    # agent = SpotRobot(start_pos=cfg.agent_start_pos)
    
    # FIXME: init spot agent instead
    agent = SpotAgent()
    krm = KnowledgeRoadmap(start_pos=agent.pos)

    debug_container = {
        "world": world,
        "agent": agent,
        "gui": gui,
    }

    lga = LocalGridAdapter(
        total_map_len_m=cfg.TOTAL_MAP_LEN_M,
        mode="spoof",
        lg_num_cells=cfg.LG_NUM_CELLS,
        lg_cell_size_m=cfg.LG_CELL_SIZE_M,
        debug_container=debug_container,
    )

    exploration_use_case = ExplorationUsecase(
        agent,
        debug=False,
        total_map_len_m=cfg.TOTAL_MAP_LEN_M,
        lg_num_cells=cfg.LG_NUM_CELLS,
        lg_length_in_m=cfg.LG_LENGTH_IN_M,
    )

    exploration_completed = False
    while agent.no_more_frontiers == False:
        # FIXME: make it so the local grid adapter can see what type of agent is running
        local_grid_img = lga.get_local_grid(agent=agent)

        lg = LocalGrid(
            world_pos=agent.pos,
            data=local_grid_img,
            length_in_m=cfg.LG_LENGTH_IN_M,
            cell_size_in_m=cfg.LG_CELL_SIZE_M,
        )

        exploration_completed = exploration_use_case.run_exploration_step(
            agent, krm, lg
        )
        if exploration_completed:
            continue
        if plotting == "all" or plotting == "intermediate only":
            close_nodes = krm.get_nodes_of_type_in_margin(
                lg.world_pos, cfg.LG_LENGTH_IN_M / 2, "waypoint"
            )
            points = [krm.get_node_data_by_idx(node)["pos"] for node in close_nodes]
            if points:
                gui.draw_shortcut_collision_lines(points, lg)
            
            gui.figure_update(krm, agent, lg)

        print(f"step= {step}")
        step += 1
    if plotting == "result only" or plotting == "all":
        gui.figure_update(krm, agent, lg)

        plt.ioff()
        plt.show()
        return exploration_completed


if __name__ == "__main__":

    exploration_spot("all")