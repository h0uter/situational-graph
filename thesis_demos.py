import matplotlib.pyplot as plt
import keyboard
from matplotlib import image
import os
import numpy as np
from skimage import draw
from PIL import Image

from knowledge_roadmap.entities.agent import Agent
from knowledge_roadmap.data_providers.manual_graph_world import *
from knowledge_roadmap.entrypoints.GUI import GUI
from knowledge_roadmap.usecases.exploration import Exploration
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

class CFG():
    def __init__(self):
        # self.total_map_len_m_x = 17
        self.total_map_len_m_x = 50
        # self.total_map_len_m_y = 13
        self.total_map_len_m_y = 40
        self.total_map_len_m = (self.total_map_len_m_x, self.total_map_len_m_y)
        self.lg_num_cells = 400


def exploration_with_sampling_viz(result_only):
    # this is the prior image of the villa we can include for visualization purposes
    # It is different from the map we use to emulate the local grid.
    # full_path = os.path.join('resource', 'output-onlinepngtools.png')
    cfg = CFG()
    full_path = os.path.join('resource', 'villa_holes_closed.png')
    upside_down_map_img = Image.open(full_path)
    # print(upside_down_map_img.size)
    map_img = img_axes2world_axes(upside_down_map_img)
    world = ManualGraphWorld()
    gui = GUI(
            map_img=map_img, 
            origin_x_offset=cfg.total_map_len_m_x/2, 
            origin_y_offset=cfg.total_map_len_m_y/2,
            )

    # gui.preview_graph_world(world)
    agent = Agent(debug=False)
    krm = KnowledgeRoadmap(start_pos=agent.pos)
    exploration_use_case = Exploration(agent, debug=False, len_of_map=cfg.total_map_len_m)

    debug_container = {
        'world': world, 
        'agent': agent, 
        'exploration_use_case': exploration_use_case, 
        'gui': gui}

    lga = LocalGridAdapter(
        # img_length_in_m=(gui.origin_x_offset, gui.origin_y_offset),
        img_length_in_m=cfg.total_map_len_m,
        mode='spoof',
        num_cells=cfg.lg_num_cells, 
        cell_size_m=1, 
        debug_container=debug_container
        )

    # sampler = FrontierSampler()
    exploration_completed = False

    while agent.no_more_frontiers == False:
    # while agent.no_more_frontiers == False:
        local_grid_img = lga.get_local_grid()
        # cell_size = 3.0 / local_grid_img.shape[1]
        # print(f"local_grid_img.shape: {local_grid_img.shape}")
        # print(cell_size)
        lg = LocalGrid(agent.pos, local_grid_img, lga.lg_size, lga.cell_size_m)
        # lg.plot_zoomed_world_coord()
        lg.plot_unzoomed_world_coord((gui.origin_x_offset, gui.origin_y_offset))

        gui.draw_local_grid(local_grid_img)

        exploration_completed = exploration_use_case.run_exploration_step(agent, local_grid_img, lga, krm)
        if exploration_completed:
            return exploration_completed
        if not result_only:
            gui.viz_krm(krm) # TODO: make the KRM independent of the agent
            gui.draw_agent(agent.pos)
            plt.pause(0.001)
    
    plt.ioff()
    plt.show()


if __name__ == '__main__':

    exploration_with_sampling_viz(False)
