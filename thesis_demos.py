from re import L
import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt
import keyboard
from matplotlib import image
import os
import numpy as np

from src.entities.knowledge_road_map import KnowledgeRoadmap
from src.entities.agent import Agent
from src.data_providers.manual_graph_world import *
from src.entrypoints.GUI import GUI
from src.usecases.exploration import Exploration
from src.data_providers.world_graph_generator import GraphGenerator
# from src

############################################################################################
# DEMONSTRATIONS
############################################################################################

def exploration(world, agent, exploration_use_case, gui, stepwise=False):
    # TODO: fix agent.krm bullshit
    # TODO: fix ugly init_plot(), like hide this in the vizualisaiton and run the first time only
    gui.init_plot(agent, agent.krm)
    while agent.no_more_frontiers == False:
        if not stepwise:
            local_grid_size = 110
            local_grid_img = agent.observe_local_grid(local_grid_size, world)
            # print(local_grid_img)
            gui.draw_local_grid(local_grid_img, agent)

            exploration_use_case.run_exploration_step(world)
            # TODO: translate agent coords to pixel coords
            # world.observe_local_grid(agent.pos, 500)

            gui.viz_krm(agent, agent.krm) # TODO: make the KRM independent of the agent
            gui.draw_agent(agent.pos)
            plt.pause(0.001)
        elif stepwise:
            # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
            keypress = keyboard.read_key()
            if keypress:
                keypress = False
                exploration_use_case.run_exploration_step(world)

                gui.viz_krm(agent, agent.krm) # TODO: make the KRM independent of the agent
                gui.draw_agent(agent.pos)
                plt.pause(0.01)

    plt.ioff()
    plt.show()

def exploration_on_randomly_generated_graph_world():
    world = GraphGenerator(100)
    gui = GUI(map_img=False)
    gui.preview_graph_world(world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent, debug=False)
    exploration(world, agent, exploration_use_case, gui)

def img_axes2world_axes(upside_down_map_img):
    map_img_rotated = np.rot90(upside_down_map_img, axes=(1, 0))
    map_img_axes_alligned = np.swapaxes(map_img_rotated, 0, 1)
    # plt.imshow(map_img_axes_alligned, origin='lower')
    return map_img_axes_alligned

def exploration_on_manual_graph_world():
    full_path = os.path.join('resource', 'floor-plan-villa.png')
    upside_down_map_img = image.imread(full_path)
    map_img = img_axes2world_axes(upside_down_map_img)

    # print(map_img.shape)
    world = ManualGraphWorld(map_img=map_img)
    gui = GUI(map_img=world.map_img)
    gui.preview_graph_world(world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent, debug=False)
    exploration(world, agent, exploration_use_case, gui)

def graph_generator_debug():
    world = GraphGenerator(200)
    gui = GUI()
    gui.preview_graph_world(world)

# def sample_img_world_while_moving():
#     world = ManualGraphWorld()
#     gui = GUI(map_img=True)
#     agent = Agent()
#     exploration_use_case = Exploration(agent, debug=False)
#     exploration(world, agent, exploration_use_case, gui)

if __name__ == '__main__':

    exploration_on_manual_graph_world()
    # exploration_on_randomly_generated_graph_world()
    # graph_generator_debug()
    