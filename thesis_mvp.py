import networkx as nx
from networkx.drawing.nx_pylab import draw
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from graph_manager import KnowledgeRoadmap

############################################################################################
# DEMONSTRATIONS
############################################################################################

def demo_instant_graph_from_waypoints(wp_data):
    ''' This demo instantly creates a graph from a list of waypoints'''
    KRM = KnowledgeRoadmap((0,0))

    KRM.init_plot()

    KRM.add_waypoints(wp_data)
    KRM.draw_current_graph()
    plt.ioff()
    plt.show()

def demo_online_graph(wp_data):
    ''' 
    This demo creates and visualises a graph online 
    from an array of waypoint data
    '''

    KRM = KnowledgeRoadmap((0, 0))
    KRM.init_plot()

    for wp in wp_data:
        KRM.add_waypoint(wp)
        KRM.draw_current_graph()

    plt.ioff()
    plt.show()

if __name__ == '__main__':
    
    # TODO: generalize this to a "sensor data stream" which is then processed by the agent.
    # outputs will be world objects and waypoints
    # TODO: how to emulate the sampling of frontier nodes?
    wp_data = [(4, 0), (8, 0), (12, 0), (16, 0), (16, -4), (16, -8), (16, -12), (12, -12), (12, -8), (12, -4), (12, 0), (8, 0),
               (5, 6), (0, 6), (-4, 6), (-8, 6), (-12, 6), (-16, 6), (-16, 11)]

    demo_online_graph(wp_data)
    # demo_instant_graph_from_waypoints(wp_data)
    

# how do I want to create this graph?
# probably I want to create a system which can dynamically add nodes and edges
# I want to demonstrate how this graph is created dynamically from inputs about the world.
# 
