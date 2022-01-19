import matplotlib.pyplot as plt
import keyboard
from matplotlib import image
import os
import numpy as np
from skimage import draw
from PIL import Image

from src.entities.agent import Agent
from src.data_providers.manual_graph_world import *
from src.entrypoints.GUI import GUI
from src.usecases.exploration import Exploration
from src.data_providers.world_graph_generator import GraphGenerator
from src.usecases.sampler import Sampler 

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

                frontiers = sampler.sample_frontiers(agent, local_grid_img, local_grid_size)
                # print(frontiers)
                frontiers = np.array(frontiers)
                # print(f"frontiers: {frontiers[:,1]}")
                # print(f"hello {frontiers[:, 1]+local_grid_size}")
                # plt.plot(frontiers[:,0]+local_grid_size, frontiers[:, 1]+local_grid_size, 'ro')
                for frontier in frontiers:
                    # x, y = sampler.pix_idx2world_coord
                    plt.plot([local_grid_size, frontier[0]], [local_grid_size, frontier[1]])
                # plt.pause(0.001)
                # plt.plot(frontiers[:,0], frontiers[:, 1], 'ro')
                # plt.pause(0.1)
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
    world = GraphGenerator(100)
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
    # print(str(map_img.tolist()))
    # for i in range(map_img.shape[0]):
    #     for j in range(map_img.shape[1]):
    #         for k in range(map_img.shape[2]):
    #             if map_img[i,j, k] != 255:
    #                 print(f"map_img: {map_img[i,j]}")
    # print(f"map_img: {map_img[10, 10]}")

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
        print(f"Sampled point: {x_sample}, {y_sample}")
        # local_grid.draw_line(x_prev, y_prev, x_sample, y_sample)
        # x_prev, y_prev = x_sample, y_sample
        data[y_sample, x_sample] = FRONTIER_CELL

    plt.ioff()
    plt.plot(x_prev, y_prev, marker='s', color='red', linestyle='none')
    local_grid.draw_grid(data)

# def sample_img_world_while_moving():
#     world = ManualGraphWorld()
#     gui = GUI(map_img=True)
#     agent = Agent()
#     exploration_use_case = Exploration(agent, debug=False)
#     exploration(world, agent, exploration_use_case, gui)

if __name__ == '__main__':

    exploration_with_sampling_viz()
    # exploration_on_manual_graph_world()
    # exploration_on_randomly_generated_graph_world()
    # graph_generator_debug()
    # local_grid_sampler_test()
    