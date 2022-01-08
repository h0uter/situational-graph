import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt

from src.entities.knowledge_road_map import KnowledgeRoadmap
from src.entities.agent import Agent
from src.data_providers.world import *
from src.entrypoints.GUI import GUI
from src.usecases.exploration import Exploration

############################################################################################
# DEMONSTRATIONS
############################################################################################

def demo_instant_graph_from_waypoints(wp_data):
    ''' This demo instantly creates a graph from a list of waypoints'''
    KRM = KnowledgeRoadmap()

    KRM.init_plot()

    KRM.add_waypoints(wp_data)
    KRM.draw_current_krm() 
    plt.ioff()
    plt.show()

def demo_online_graph(wp_data):
    ''' 
    This demo creates and visualises a graph online 
    from an array of waypoint data
    '''
    KRM = KnowledgeRoadmap()
    KRM.init_plot()
    for wp in wp_data:
        KRM.add_waypoint(wp)
        KRM.draw_current_krm()

    plt.ioff()
    plt.show()

def demo_with_agent_drawn(wp_data):
    ''' 
    This demo creates and visualises a graph online 
    from an array of waypoint data
    '''
    agent = Agent()
    KRM = KnowledgeRoadmap((0, 0))
    KRM.init_plot()

    for wp in wp_data:
        KRM.add_waypoint(wp)
        agent.draw_agent(wp)
        KRM.draw_current_krm()

    plt.ioff()
    plt.show()

def demo_agent_driven():
    ''' This is the first demo where the agent takes actions to explore a world'''
    world = ManualGraphWorld()
    # world = LatticeWorld()
    gui = GUI()
    # gui.draw_world(world.world)
    # agent = Agent(debug=False)
    exploration = Exploration()
    # gui.run_and_vizualize_exploration(exploration, world)

    exploration.explore(world)
    # agent.explore_stepwise(world)
    # agent.explore(world)

    plt.ioff()

    plt.show()


def demo_separate_gui_from_exploration():

    world = ManualGraphWorld()
    gui = GUI()
    # gui.draw_world(world.world)
    exploration = Exploration()

    exploration.explore2(world)


    plt.ioff()

    plt.show()

if __name__ == '__main__':

    # TODO: generalize this to a "sensor data stream" which is then processed by the agent.
    # outputs will be world objects and waypoints
    # TODO: how to emulate the sampling of frontier nodes?
    # world = GraphWorld()

    # demo_with_agent_drawn(world.structure)
    # demo_instant_graph_from_waypoints(wp_data)
    # demo_agent_driven()
    demo_separate_gui_from_exploration()
    # world = GraphWorldExperiment()
    