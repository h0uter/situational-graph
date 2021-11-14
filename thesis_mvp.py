import networkx as nx
from networkx.drawing.nx_pylab import draw
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def create_nav_graph(data):
    # create a graph based on array of waypoints
    G = nx.Graph()
    
    for i in range(len(data)):
        G.add_node(i, pos=(data[i][0], data[i][1]), type="waypoint")
        if i > 0:
            G.add_edge(i-1, i, type="waypoint_edge")
    return G


def create_nav_graph_online(data):
    # create a graph based on array of waypoints
    G = nx.Graph()
    fig, ax = plt.subplots()
    plt.ion()
    plt.show()
    
    for i in range(len(data)):
        G.add_node(i, pos=(data[i][0], data[i][1]), type="waypoint")
        if i > 0:
            G.add_edge(i-1, i, type="waypoint_edge")
        
        draw_dynamic_graph(G, ax)
    
    plt.show()
    # return G

def add_world_object_to_graph(graph):

    graph.add_node("victim1", pos=(6, 6), type="world_object")
    graph.add_edge(4, "victim1", type="world_object_edge")

    graph.add_node("victim2", pos=(10, 10), type="world_object")
    graph.add_edge(10, "victim2", type="world_object_edge")

    return graph

def draw_static_graph(G):
    fig, ax = plt.subplots()

    pos = nx.get_node_attributes(G, 'pos')
    # filter the nodes and edges based on their type
    waypoint_nodes = dict((n, d['type'])
                        for n, d in G.nodes().items() if d['type'] == 'waypoint')
    world_object_nodes = dict((n, d['type'])
                    for n, d in G.nodes().items() if d['type'] == 'world_object')

    world_object_edges = dict((e, d['type'])
                            for e, d in G.edges().items() if d['type'] == 'world_object_edge')

    waypoint_edges = dict((e, d['type'])
                            for e, d in G.edges().items() if d['type'] == 'waypoint_edge')

    # fig, ax = plt.subplots()

    # draw the nodes, edges and labels separately
    nx.draw_networkx_nodes(G, pos, nodelist=world_object_nodes.keys(),
            ax=ax, node_color='orange')
    nx.draw_networkx_nodes(G, pos, nodelist=waypoint_nodes.keys(), ax=ax, node_color='red')

    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=waypoint_edges.keys(), edge_color='red')
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=world_object_edges.keys(), edge_color='orange')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)

    limits = plt.axis('on')  # turns on axis
    ax.set_aspect('equal', 'box') # set the aspect ratio of the plot
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    plt.show()

def draw_dynamic_graph(G, ax):

    pos = nx.get_node_attributes(G, 'pos')
    # filter the nodes and edges based on their type
    waypoint_nodes = dict((n, d['type'])
                          for n, d in G.nodes().items() if d['type'] == 'waypoint')
    world_object_nodes = dict((n, d['type'])
                              for n, d in G.nodes().items() if d['type'] == 'world_object')

    world_object_edges = dict((e, d['type'])
                              for e, d in G.edges().items() if d['type'] == 'world_object_edge')

    waypoint_edges = dict((e, d['type'])
                          for e, d in G.edges().items() if d['type'] == 'waypoint_edge')

    # fig, ax = plt.subplots()

    # draw the nodes, edges and labels separately
    nx.draw_networkx_nodes(G, pos, nodelist=world_object_nodes.keys(),
                           ax=ax, node_color='orange')
    nx.draw_networkx_nodes(
        G, pos, nodelist=waypoint_nodes.keys(), ax=ax, node_color='red')

    nx.draw_networkx_edges(
        G, pos, ax=ax, edgelist=waypoint_edges.keys(), edge_color='red')
    nx.draw_networkx_edges(
        G, pos, ax=ax, edgelist=world_object_edges.keys(), edge_color='orange')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)

    limits = plt.axis('on')  # turns on axis
    ax.set_aspect('equal', 'box')  # set the aspect ratio of the plot
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    # plt.show()
    plt.draw()
    plt.pause(0.5)

if __name__ == '__main__':
    # villa_nodes = [
    #     (1, {"pos": (0, 0), "type": "waypoint"}),
    # ]

    data = [[0,0], [2,2], [4,2], [4,4], [4,6], [2,6], [2, 8], [2,10], [4,10], [6,12], [8,12], [10,14], [12,14]]

    graph = create_nav_graph(data)
    # create_nav_graph_online(data)
    plt.show()
    # draw_static_graph(graph)

    graph = add_world_object_to_graph(graph)

    draw_static_graph(graph)


# how do I want to create this graph?
# probably I want to create a system which can dynamically add nodes and edges
# I want to demonstrate how this graph is created dynamically from inputs about the world.
# 
