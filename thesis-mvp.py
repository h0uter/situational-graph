import networkx as nx
import plotly.graph_objects as go
import matplotlib.pyplot as plt


G = nx.Graph()

###############################################################################
# define the nodes of the graph
G.add_node(1, pos=(0, 0), type="place")
G.add_node(2, pos=(2, 2), type="place")
G.add_edge(1, 2, type="place_edge")
G.add_node(3, pos=(4, 2), type="place")
G.add_edge(2, 3, type="place_edge")
G.add_node(4, pos=(4, 4), type="place")
G.add_edge(3, 4, type="place_edge")
G.add_node(5, pos=(4, 6), type="place")
G.add_edge(4, 5, type="place_edge")
G.add_node(6, pos=(2, 6), type="place")
G.add_edge(5, 6, type="place_edge")
G.add_node("victim1", pos=(2, 3), type="world_object")
G.add_edge(4, "victim1", type="world_object")

pos = nx.get_node_attributes(G, 'pos')
###############################################################################

# filter the nodes and edges based on their type
place_nodes = dict((n, d['type'])
                     for n, d in G.nodes().items() if d['type'] == 'place')
world_object_nodes = dict((n, d['type'])
                   for n, d in G.nodes().items() if d['type'] == 'world_object')

world_object_edges = dict((e, d['type'])
                          for e, d in G.edges().items() if d['type'] == 'world_object')

place_edges = dict((e, d['type'])
                          for e, d in G.edges().items() if d['type'] == 'place_edge')


fig, ax = plt.subplots()

# draw the nodes, edges and labels separately
nx.draw_networkx_nodes(G, pos, nodelist=world_object_nodes.keys(),
        ax=ax, node_color='orange')
nx.draw_networkx_nodes(G, pos, nodelist=place_nodes.keys(), ax=ax, node_color='red')

nx.draw_networkx_edges(G, pos, ax=ax, edgelist=place_edges.keys(), edge_color='red')
nx.draw_networkx_edges(G, pos, ax=ax, edgelist=world_object_edges.keys(), edge_color='orange')
nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)


limits = plt.axis('on')  # turns on axis
ax.set_aspect('equal', 'box') # set the aspect ratio of the plot

ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)


plt.show()