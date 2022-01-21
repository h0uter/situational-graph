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
from knowledge_roadmap.usecases.sampler import Sampler 

############################################################################################
# DEMONSTRATIONS
############################################################################################

def exploration_on_graph(world, agent, exploration_use_case, gui, stepwise=False):
    while agent.no_more_frontiers == False:
        if not stepwise:

            exploration_use_case.run_exploration_step(world)

            # TODO: put all drawing logic in one function
            # FIXME: fix agent.krm bullshit, KRM should be an entity which can be shared by multiple agents
            gui.viz_krm(agent, agent.krm) # TODO: make the KRM independent of the agent
            gui.draw_agent(agent.pos)
            if gui.map_img is not None:
                local_grid_size = 150
                local_grid_img = agent.observe_local_grid(local_grid_size, world)
                gui.draw_local_grid(local_grid_img)
            plt.pause(0.001)
        elif stepwise:
            # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
            keypress = keyboard.read_key()
            if keypress:
                keypress = False
                exploration_use_case.run_exploration_step(world)

                gui.viz_krm(agent, agent.krm)
                gui.draw_agent(agent.pos)
                plt.pause(0.01)

    plt.ioff()
    plt.show()


def exploration_sampling(world, agent, exploration_use_case, gui, stepwise=False):
    local_grid_size = 150
    cell_size = 1
    sampler = Sampler(cell_size, local_grid_size)
    # plt.figure(6)
    while agent.no_more_frontiers == False:
        if not stepwise:

            exploration_use_case.run_exploration_step(world)
            gui.viz_krm(agent, agent.krm) # TODO: make the KRM independent of the agent
            gui.draw_agent(agent.pos)
            if gui.map_img is not None: 
                local_grid_img = agent.observe_local_grid(local_grid_size, world)
                gui.draw_local_grid(local_grid_img)

                frontiers = sampler.sample_frontiers(local_grid_img, local_grid_size)
                frontiers = np.array(frontiers).astype(np.int)

                for frontier in frontiers:
                    xx, yy = sampler.get_cells_under_line((local_grid_size, local_grid_size), frontier)
                    # plt.plot([local_grid_size, frontier[0]], [local_grid_size, frontier[1]])
                    plt.plot(xx, yy) # draw the line as collection of pixels

            # TODO: put all drawing logic in one function
            # FIXME: fix agent.krm bullshit, KRM should be an entity which can be shared by multiple agents
            plt.pause(0.001)
        elif stepwise:
            # BUG:: matplotlib crashes after 10 sec if we block the execution like this.
            keypress = keyboard.read_key()
            if keypress:
                keypress = False
                exploration_use_case.run_exploration_step(world)

                gui.viz_krm(agent, agent.krm)
                gui.draw_agent(agent.pos)
                plt.pause(0.01)

    plt.ioff()
    plt.show()

def exploration_on_randomly_generated_graph_world():
    world = GraphGenerator(100,save_world_to_file=True)
    gui = GUI(map_img=None)
    gui.preview_graph_world(world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent, debug=False)
    exploration_on_graph(world, agent, exploration_use_case, gui)

def img_axes2world_axes(upside_down_map_img):
    map_img_rotated = np.rot90(upside_down_map_img, axes=(1, 0))
    map_img_axes_alligned = np.swapaxes(map_img_rotated, 0, 1)

    return map_img_axes_alligned

def exploration_on_manual_graph_world():
    # full_path = os.path.join('resource', 'floor-plan-villa.png')
    full_path = os.path.join('resource', 'output-onlinepngtools.png')
    upside_down_map_img = image.imread(full_path)
    map_img = img_axes2world_axes(upside_down_map_img)

    world = ManualGraphWorld(map_img=map_img)
    gui = GUI(map_img=world.map_img)
    gui.preview_graph_world(world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent, debug=False)
    exploration_on_graph(world, agent, exploration_use_case, gui)

def exploration_with_sampling_viz():
    # full_path = os.path.join('resource', 'floor-plan-villa.png')
    full_path = os.path.join('resource', 'output-onlinepngtools.png')
    upside_down_map_img = Image.open(full_path)
    map_img = img_axes2world_axes(upside_down_map_img)
    world = ManualGraphWorld(map_img=map_img)
    gui = GUI(map_img=world.map_img)
    # gui.preview_graph_world(world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent, debug=False)
    exploration_sampling(world, agent, exploration_use_case, gui)

def graph_generator_debug():
    world = GraphGenerator(200)
    gui = GUI()
    gui.preview_graph_world(world)

def local_grid_sampler_test():
    EMPTY_CELL = 0
    OBSTACLE_CELL = 1
    FRONTIER_CELL = 2
    GOAL_CELL = 3
    MOVE_CELL = 4
    cell_size = 1
    num_cells = 15
    two_times_num_cells = int(num_cells*2)
    # x_prev, y_prev = num_cells, num_cells
    x_prev, y_prev = 5, 5

    empty_data = np.zeros((two_times_num_cells, two_times_num_cells))
    data = empty_data

    # add a boundary to the local grid
    rr, cc = draw.rectangle_perimeter((2,2), (two_times_num_cells-5, two_times_num_cells-5), shape=data.shape)
    data[rr,cc] = 1

    local_grid = Sampler(cell_size, num_cells)
    local_grid.draw_grid(data)


    for i in range(10):
        x_sample, y_sample = local_grid.sample_point_around_other_point(x_prev, y_prev, radius=20, data=data)
        # print(f"Sampled point: {x_sample}, {y_sample}")
        # local_grid.draw_line(x_prev, y_prev, x_sample, y_sample)
        # x_prev, y_prev = x_sample, y_sample
        data[y_sample, x_sample] = FRONTIER_CELL

    plt.ioff()
    plt.plot(x_prev, y_prev, marker='s', color='red', linestyle='none')
    local_grid.draw_grid(data)

if __name__ == '__main__':

    # exploration_with_sampling_viz()
    # exploration_on_manual_graph_world()
    exploration_on_randomly_generated_graph_world()
    # graph_generator_debug()
    # local_grid_sampler_test()
    