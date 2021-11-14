import networkx as nx
import plotly.graph_objects as go
import pandas as pd


#Let's import the ZKC graph:
ZKC_graph = nx.karate_club_graph()

#Let's keep track of which nodes represent John A and Mr Hi
Mr_Hi = 0
John_A = 33

#remember the number of nodes since this will come in useful later
Num_nodes = 34

#get the club labels - i.e. which club each individual ended up joining
club_labels = list(nx.get_node_attributes(ZKC_graph, 'club').values())

#communities from last time - one list for each community
community_0 = [8, 14, 15, 18, 20, 22, 23,
               24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
community_1 = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 16, 17, 19, 21]

#label for each node corresponds to community 0 or community 1
community_label = [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1,
                   0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#Let's opt for a spring layout
spring_pos = nx.spring_layout(ZKC_graph, seed=2)

#draw the network
nx.draw_networkx_nodes(ZKC_graph, spring_pos,
                       nodelist=community_0, node_color='g', alpha=0.4)
nx.draw_networkx_nodes(ZKC_graph, spring_pos,
                       nodelist=community_1, node_color='m', alpha=0.4)

#let's highlight Mr Hi (solid purple) and John A (solid green)
nx.draw_networkx_nodes(ZKC_graph, spring_pos, nodelist=[
                       John_A], node_color='g', alpha=1)
nx.draw_networkx_nodes(ZKC_graph, spring_pos, nodelist=[
                       Mr_Hi], node_color='m', alpha=1)

nx.draw_networkx_edges(ZKC_graph, spring_pos, style='dashed', width=0.5)


#As before we use networkx to determine node positions. We want to do the same spring layout but in 3D
spring_3D = nx.spring_layout(ZKC_graph, dim=3, seed=18)

#an example node coordinate
spring_3D[4]

#we need to seperate the X,Y,Z coordinates for Plotly
x_nodes = [spring_3D[i][0] for i in range(Num_nodes)]  # x-coordinates of nodes
y_nodes = [spring_3D[i][1] for i in range(Num_nodes)]  # y-coordinates
z_nodes = [spring_3D[i][2] for i in range(Num_nodes)]  # z-coordinates


#We also need a list of edges to include in the plot
edge_list = ZKC_graph.edges()

edge_list


#we  need to create lists that contain the starting and ending coordinates of each edge.
x_edges = []
y_edges = []
z_edges = []

#need to fill these with all of the coordiates
for edge in edge_list:
    #format: [beginning,ending,None]
    x_coords = [spring_3D[edge[0]][0], spring_3D[edge[1]][0], None]
    x_edges += x_coords

    y_coords = [spring_3D[edge[0]][1], spring_3D[edge[1]][1], None]
    y_edges += y_coords

    z_coords = [spring_3D[edge[0]][2], spring_3D[edge[1]][2], None]
    z_edges += z_coords


#create a trace for the edges
trace_edges = go.Scatter3d(x=x_edges,
                           y=y_edges,
                           z=z_edges,
                           mode='lines',
                           line=dict(color='black', width=2),
                           hoverinfo='none')


#create a trace for the nodes
trace_nodes = go.Scatter3d(x=x_nodes,
                           y=y_nodes,
                           z=z_nodes,
                           mode='markers',
                           marker=dict(symbol='circle',
                                       size=10,
                                       color=community_label,  # color the nodes according to their community
                                       # either green or mageneta
                                       colorscale=['lightgreen', 'magenta'],
                                       line=dict(color='black', width=0.5)),
                           text=club_labels,
                           hoverinfo='text')


trace_MrHi = go.Scatter3d(x=[x_nodes[Mr_Hi]],
                          y=[y_nodes[Mr_Hi]],
                          z=[z_nodes[Mr_Hi]],
                          mode='markers',
                          name='Mr_Hi',
                          marker=dict(symbol='circle',
                                      size=10,
                                      color='darkmagenta',
                                      line=dict(color='black', width=0.5)
                                      ),
                          text=['Mr_Hi'],
                          hoverinfo='text')


trace_JohnA = go.Scatter3d(x=[x_nodes[John_A]],
                           y=[y_nodes[John_A]],
                           z=[z_nodes[John_A]],
                           mode='markers',
                           name='John_A',
                           marker=dict(symbol='circle',
                                       size=10,
                                       color='green',
                                       line=dict(color='black', width=0.5)
                                       ),
                           text=['Officer'],
                           hoverinfo='text')


#we need to set the axis for the plot
axis = dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title='')


#also need to create the layout for our plot
layout = go.Layout(title="Two Predicted Factions of Zachary's Karate Club",
                   width=650,
                   height=625,
                   showlegend=False,
                   scene=dict(xaxis=dict(axis),
                              yaxis=dict(axis),
                              zaxis=dict(axis),
                              ),
                   margin=dict(t=100),
                   hovermode='closest')

#Include the traces we want to plot and create a figure
data = [trace_edges, trace_nodes, trace_MrHi, trace_JohnA]
fig = go.Figure(data=data, layout=layout)

fig.show()
