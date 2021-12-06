import uuid
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from networkx.generators.small import sedgewick_maze_graph
import numpy as np

class KnowledgeRoadmap():
    '''
    An agent implements a Knowledge Roadmap to keep track of the 
    world beliefs which are relevant for navigating during his mission.
    A KRM is a graph with 3 distinct node and corresponding edge types.
    - Waypoint Nodes:: correspond to places the robot has been and can go to.
    - Frontier Nodes:: correspond to places the robot has not been but expects it can go to.
    TODO:- World Object Nodes:: correspond to actionable items the robot has seen.
    '''
    def __init__(self, start_pos=(0, 0)):
        self.KRM = nx.Graph() # Knowledge Road Map

        # TODO: start node like this is lame
        self.KRM.add_node(0, pos=start_pos, type="waypoint", id=uuid.uuid4())
        self.next_wp_idx = 1
        self.next_frontier_idx = 1000
        self.next_wo_idx = 2000

        self.init_plot()

    def add_waypoint(self, pos, prev_wp):
        ''' adds new waypoints and increments wp the idx'''
        self.KRM.add_node(self.next_wp_idx, pos=pos, type="waypoint", id=uuid.uuid4())
        self.KRM.add_edge(self.next_wp_idx, prev_wp, type="waypoint_edge", id=uuid.uuid4())
        self.next_wp_idx += 1

    def add_waypoints(self, wp_array):
        ''' adds waypoints to the graph'''
        for wp in wp_array:
            self.add_waypoint(wp)

    # TODO: remove the agent_at_wp parameter requirement
    def add_frontier(self, pos, agent_at_wp):
        ''' adds a frontier to the graph'''
        self.KRM.add_node(self.next_frontier_idx, pos=pos,
                        type="frontier", id=uuid.uuid4())
        self.KRM.add_edge(agent_at_wp, self.next_frontier_idx,
                          type="frontier_edge", id=uuid.uuid4())
        self.next_frontier_idx += 1

    def remove_frontier(self, target_frontier):
        ''' removes a frontier from the graph'''
        if target_frontier['type'] == 'frontier':
            target = self.get_node_by_UUID(target_frontier['id'])
            # print("removing frontier: ", target)
            self.KRM.remove_node(target)

    def add_world_object(self, pos, label):
        ''' adds a world object to the graph'''
        self.KRM.add_node(label, pos=pos, type="world_object", id=uuid.uuid4())
        self.next_wo_idx += 1

    # TODO: this feels duplicative wtih draw_current_krm
    def init_plot(self):
        ''' initializes the plot'''
        # self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig, self.ax = plt.subplots()
        self.img = plt.imread("resource/floor-plan-villa.png")

        plt.ion()
        self.draw_current_krm()
        plt.pause(0.1)

    def draw_current_krm(self):
        ''' draws the current Knowledge Roadmap Graph'''
        plt.cla()
        self.ax.set_title('Online Construction of Knowledge Roadmap')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)
        self.ax.imshow(self.img, extent=[-20, 20, -15, 15])

        pos = nx.get_node_attributes(self.KRM, 'pos')
        # filter the nodes and edges based on their type
        waypoint_nodes = dict((n, d['type'])
                            for n, d in self.KRM.nodes().items() if d['type'] == 'waypoint')
        frontier_nodes = dict((n, d['type'])
                              for n, d in self.KRM.nodes().items() if d['type'] == 'frontier')
        world_object_nodes = dict((n, d['type'])
                                for n, d in self.KRM.nodes().items() if d['type'] == 'world_object')

        world_object_edges = dict((e, d['type'])
                                for e, d in self.KRM.edges().items() if d['type'] == 'world_object_edge')
        waypoint_edges = dict((e, d['type'])
                            for e, d in self.KRM.edges().items() if d['type'] == 'waypoint_edge')
        frontier_edges = dict((e, d['type'])
                              for e, d in self.KRM.edges().items() if d['type'] == 'frontier_edge')

        # draw the nodes, edges and labels separately
        nx.draw_networkx_nodes(self.KRM, pos, nodelist=world_object_nodes.keys(),
                            ax=self.ax, node_color='purple')
        nx.draw_networkx_nodes(self.KRM, pos, nodelist=frontier_nodes.keys(),
                            ax=self.ax, node_color='green')
        nx.draw_networkx_nodes(
            self.KRM, pos, nodelist=waypoint_nodes.keys(), ax=self.ax, node_color='red', node_size=150)
        nx.draw_networkx_edges(
            self.KRM, pos, ax=self.ax, edgelist=waypoint_edges.keys(), edge_color='red')
        nx.draw_networkx_edges(
            self.KRM, pos, ax=self.ax, edgelist=world_object_edges.keys(), edge_color='purple')
        nx.draw_networkx_edges(
            self.KRM, pos, ax=self.ax, edgelist=frontier_edges.keys(), edge_color='green', width=4)
        nx.draw_networkx_labels(self.KRM, pos, ax=self.ax, font_size=8)
        plt.axis('on')  # turns on axis
        self.ax.set_aspect('equal', 'box')  # set the aspect ratio of the plot
        self.ax.tick_params(left=True, bottom=True,
                            labelleft=True, labelbottom=True)

        # plt.draw()
        # plt.pause(0.1)
    
    def get_node_by_pos(self, pos):
        ''' returns the node at the given position '''
        for node in self.KRM.nodes():
            if self.KRM.nodes[node]['pos'] == pos:
                return node

    def get_node_by_UUID(self, UUID):
        ''' returns the node with the given UUID '''
        for node in self.KRM.nodes():
            if self.KRM.nodes[node]['id'] == UUID:
                return node

    def get_node_by_idx(self, idx):
        ''' returns the node corresponding to the given index '''
        return self.KRM.nodes[idx]

    def get_all_waypoints(self):
        ''' returns all waypoints in the graph'''
        return [self.KRM.nodes[node] for node in self.KRM.nodes() if self.KRM.nodes[node]['type'] == 'waypoint']

    def get_all_frontiers(self):
        ''' returns all frontiers in the graph'''
        return [self.KRM.nodes[node] for node in self.KRM.nodes() if self.KRM.nodes[node]['type'] == 'frontier']

    # not used
    def get_all_waypoints2(self):
        ''' returns all node idx keyed dictionary with keys of strings which type each node is'''
        # return [self.KRM.nodes[node] for node in self.KRM.nodes() if self.KRM.nodes[node]['type'] == 'waypoint']
        return nx.get_node_attributes(self.KRM, 'type')



    # def add_worldobject(self):
    #     self.KRM.add_node("victim1", pos=(6, 6), type="world_object")
    #     self.KRM.add_edge(4, "victim1", type="world_object_edge")
    #     self.KRM.add_node("victim2", pos=(10, 10), type="world_object")
    #     self.KRM.add_edge(10, "victim2", type="world_object_edge")

