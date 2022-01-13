import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt
import keyboard

from src.entities.knowledge_road_map import KnowledgeRoadmap
from src.entities.agent import Agent
from src.data_providers.world import *
from src.entrypoints.GUI import GUI
from src.usecases.exploration import Exploration
from src.data_providers.world_graph_generator import GraphGenerator

############################################################################################
# DEMONSTRATIONS
############################################################################################

def exploration(world, agent, exploration_use_case, gui, stepwise=False):
    # TODO: fix agent.krm bullshit
    # TODO: fix ugly init_plot(), like hide this in the vizualisaiton and run the first time only
    gui.init_plot(agent, agent.krm)
    while agent.no_more_frontiers == False:
        if not stepwise:
            exploration_use_case.run_exploration_step(world)

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

def exploration_on_manual_graph_world():
    world = ManualGraphWorld()
    gui = GUI(map_img=True)
    gui.preview_graph_world(world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent, debug=False)
    exploration(world, agent, exploration_use_case, gui)

def graph_generator_debug():
    world = GraphGenerator(200)
    gui = GUI()
    gui.preview_graph_world(world)

if __name__ == '__main__':

    # exploration_on_manual_graph_world()
    exploration_on_randomly_generated_graph_world()
    # graph_generator_debug()
    