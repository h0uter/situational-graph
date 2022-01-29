import matplotlib.pyplot as plt
import os
from PIL import Image

from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.data_providers.manual_graph_world import *
from knowledge_roadmap.entrypoints.GUI import GUI
from knowledge_roadmap.usecases.exploration_usecase import ExplorationUsecase
from knowledge_roadmap.data_providers.world_graph_generator import GraphGenerator
from knowledge_roadmap.data_providers.local_grid_adapter import LocalGridAdapter
from knowledge_roadmap.entities.frontier_sampler import FrontierSampler
from knowledge_roadmap.entities.knowledge_road_map import KnowledgeRoadmap
from knowledge_roadmap.entities.local_grid import LocalGrid


import matplotlib

matplotlib.use("Tkagg")

############################################################################################
# DEMONSTRATIONS
############################################################################################


class CFG:
    def __init__(self):
        self.total_map_len_m_x = 50
        # self.total_map_len_m_x = 17 # BUG: completely broken on different length scales
        # self.total_map_len_m_y = 13
        # self.total_map_len_m_y = 40
        self.total_map_len_m_y = (
            self.total_map_len_m_x / 2026
        ) * 1686  # zo klopt het met de foto verhoudingen (square cells)
        self.total_map_len_m = (self.total_map_len_m_x, self.total_map_len_m_y)
        self.lg_num_cells = 400  # max:400 due to img border margins
        # self.lg_num_cells = 50
        self.lg_cell_size_m = self.total_map_len_m_x / 2026
        self.lg_length_scale = self.lg_num_cells * self.lg_cell_size_m / 2
        # self.agent_start_pos = (0, 0)
        self.agent_start_pos = (-9, 13)


def exploration_with_sampling_viz(result_only):
    # this is the prior image of the villa we can include for visualization purposes
    # It is different from the map we use to emulate the local grid.
    cfg = CFG()

    full_path = os.path.join("resource", "villa_holes_closed.png")
    upside_down_map_img = Image.open(full_path)
    # print(upside_down_map_img.size)
    map_img = img_axes2world_axes(upside_down_map_img)
    world = ManualGraphWorld()
    gui = GUI(
        map_img=map_img,
        origin_x_offset=cfg.total_map_len_m_x / 2,
        origin_y_offset=cfg.total_map_len_m_y / 2,
    )

    # gui.preview_graph_world(world)
    agent = Agent(debug=False, start_pos=cfg.agent_start_pos)
    krm = KnowledgeRoadmap(start_pos=agent.pos)

    debug_container = {
        "world": world,
        "agent": agent,
        # 'exploration_use_case': exploration_use_case,
        "gui": gui,
    }

    lga = LocalGridAdapter(
        img_length_in_m=cfg.total_map_len_m,
        mode="spoof",
        num_cells=cfg.lg_num_cells,
        cell_size_m=cfg.lg_cell_size_m,
        debug_container=debug_container,
    )

    exploration_use_case = ExplorationUsecase(
        agent,
        debug=False,
        len_of_map=cfg.total_map_len_m,
        lg_num_cells=cfg.lg_num_cells,
        lg_length_m=cfg.lg_length_scale,
    )

    # sampler = FrontierSampler()
    exploration_completed = False

    while agent.no_more_frontiers == False:

        local_grid_img = lga.get_local_grid()

        lg = LocalGrid(
            world_pos=agent.pos,
            data=local_grid_img,
            length_in_m=lga.lg_length_in_m,
            cell_size_in_m=lga.cell_size_m,
        )

        # print(f"lga.num_cells: {lga.num_cells}, lg.num_cells: {lg.length_num_cells}, lg shape")
        gui.draw_local_grid(lg)

        exploration_completed = exploration_use_case.run_exploration_step(
            agent, local_grid_img, lga, krm
        )
        if exploration_completed:
            return exploration_completed
        if not result_only:

            close_nodes = krm.get_nodes_of_type_in_margin(lg.world_pos, cfg.lg_length_scale, "waypoint")
            points = []
            for node in close_nodes:
                points.append(krm.get_node_data_by_idx(node)['pos'])

            if points:
                lg.plot_line_to_points_in_world_coord(points)
            gui.plot_unzoomed_world_coord(lg)
            gui.viz_krm(krm)  # TODO: make the KRM independent of the agent
            gui.draw_agent(agent.pos, rec_len=cfg.lg_length_scale * 2)
            plt.pause(0.001)

    plt.ioff()
    plt.show()


if __name__ == "__main__":

    exploration_with_sampling_viz(False)
