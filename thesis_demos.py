import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt
import keyboard
import time

from src.entities.knowledge_road_map import KnowledgeRoadmap
from src.entities.agent import Agent
from src.data_providers.world import *
from src.entrypoints.GUI import GUI
from src.usecases.exploration import Exploration
from src.data_providers.world_graph_generator import GraphGenerator

############################################################################################
# DEMONSTRATIONS
############################################################################################

def demo_agent_driven():
    ''' This is the first demo where the agent takes actions to explore a world'''
    world = ManualGraphWorld()
    # world = LatticeWorld()
    gui = GUI()
    # gui.draw_world(world.world)
    agent = Agent(debug=False)
    exploration = Exploration(agent)

    exploration.explore(world)
    # agent.explore_stepwise(world)
    # agent.explore(world)

    plt.ioff()
    plt.show()


def pure_exploration_usecase():
    world = GraphGenerator(100)
    # world = gen.generate_graph(100)

    # world = ManualGraphWorld()
    gui = GUI()
    # gui.preview_godmode_frontier_graph_world(world.world)
    agent = Agent(debug=False)
    exploration_use_case = Exploration(agent, debug=True)

    stepwise = False
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

def graph_generator_debug():
    world = GraphGenerator(50)
    # world = gen.generate_graph(50)
    print(world)
    gui = GUI()
    gui.preview_graph_world(world)

if __name__ == '__main__':

    # demo_with_agent_drawn(world.structure)
    # demo_instant_graph_from_waypoints(wp_data)
    # demo_agent_driven()
    # pure_exploration_usecase()
    graph_generator_debug()
    