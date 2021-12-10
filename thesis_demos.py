import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt

from knowledge_road_map import KnowledgeRoadmap
from agent import Agent
from world import *

############################################################################################
# DEMONSTRATIONS
############################################################################################

def demo_instant_graph_from_waypoints(wp_data):
    ''' This demo instantly createsn a graph from a list of waypoints'''
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
    ''' this is the first demo where the agent takes actions to explore a world'''
    world = ManualGraphWorld()
    # world = LatticeWorld()
    agent = Agent()

    # agent.explore_stepwise(world)
    agent.explore(world)

    # TODO:: agent.await_command()

    plt.ioff()
    plt.show()


if __name__ == '__main__':

    # TODO: generalize this to a "sensor data stream" which is then processed by the agent.
    # outputs will be world objects and waypoints
    # TODO: how to emulate the sampling of frontier nodes?
    # world = GraphWorld()

    # demo_with_agent_drawn(world.structure)
    # demo_instant_graph_from_waypoints(wp_data)
    demo_agent_driven()
    # world = GraphWorldExperiment()
    