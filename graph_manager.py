import uuid
import networkx as nx
import matplotlib.pyplot as plt

# TODO: implement frontier nodes

class KnowledgeRoadmap():
    '''
    An agent implements a Knowledge Roadmap to keep track of the 
    world beliefs which are relevant for navigating during his mission.
    A KRM is a graph with 3 distinct node and corresponding edge types.
    - Waypoint Nodes:: correspond to places the robot has been and can go to.
    - World Object Nodes:: correspond to actionable items the robot has seen.
    - Frontier Nodes:: correspond to places the robot has not been but expects it can go to.
    '''

    def __init__(self, start_pos):
        self.KRM = nx.Graph() # Knowledge Road Map
        self.KRM.add_node(0, pos=start_pos, type="waypoint")
        self.next_wp_idx = 1

    def add_waypoint(self, agent_pos):
        ''' adds new waypoints and increments wp the idx'''
        self.KRM.add_node(self.next_wp_idx, pos=agent_pos, type="waypoint", id=uuid.uuid4())
        self.KRM.add_edge(self.next_wp_idx, self.next_wp_idx-1, type="waypoint_edge", id=uuid.uuid4())
        self.next_wp_idx += 1

    def add_waypoints(self, wp_array):
        ''' adds waypoints to the graph'''
        for wp in wp_array:
            self.add_waypoint(wp)

    def init_plot(self):
        ''' initializes the plot'''
        fig, self.ax = plt.subplots(figsize=(10, 10))
        
        self.img = plt.imread("resource/floor-plan-villa.png")

        self.ax.set_title('Constructing Knowledge Roadmap')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)

        self.ax.imshow(self.img, extent=[-20, 20, -15, 15])

        plt.ion()
        self.draw_current_graph()
        plt.pause(1.5)

    def draw_current_graph(self):
        ''' draws the current Knowledge Roadmap Graph'''

        pos = nx.get_node_attributes(self.KRM, 'pos')
        # filter the nodes and edges based on their type
        waypoint_nodes = dict((n, d['type'])
                            for n, d in self.KRM.nodes().items() if d['type'] == 'waypoint')
        world_object_nodes = dict((n, d['type'])
                                for n, d in self.KRM.nodes().items() if d['type'] == 'world_object')

        world_object_edges = dict((e, d['type'])
                                for e, d in self.KRM.edges().items() if d['type'] == 'world_object_edge')

        waypoint_edges = dict((e, d['type'])
                            for e, d in self.KRM.edges().items() if d['type'] == 'waypoint_edge')

        # draw the nodes, edges and labels separately
        nx.draw_networkx_nodes(self.KRM, pos, nodelist=world_object_nodes.keys(),
                            ax=self.ax, node_color='orange')
        nx.draw_networkx_nodes(
            self.KRM, pos, nodelist=waypoint_nodes.keys(), ax=self.ax, node_color='red')
        nx.draw_networkx_edges(
            self.KRM, pos, ax=self.ax, edgelist=waypoint_edges.keys(), edge_color='red')
        nx.draw_networkx_edges(
            self.KRM, pos, ax=self.ax, edgelist=world_object_edges.keys(), edge_color='orange')
        nx.draw_networkx_labels(self.KRM, pos, ax=self.ax, font_size=10)

        plt.axis('on')  # turns on axis
        self.ax.set_aspect('equal', 'box')  # set the aspect ratio of the plot
        self.ax.tick_params(left=True, bottom=True,
                            labelleft=True, labelbottom=True)
        plt.draw()
        plt.pause(0.5)


    def get_node_by_pos(self, pos):
        for node in self.KRM.nodes():
            print(node)
            if self.KRM.nodes[node]['pos'] == pos:
                return node

    # def add_worldobject(self):

    #     self.KRM.add_node("victim1", pos=(6, 6), type="world_object")
    #     self.KRM.add_edge(4, "victim1", type="world_object_edge")

    #     self.KRM.add_node("victim2", pos=(10, 10), type="world_object")
    #     self.KRM.add_edge(10, "victim2", type="world_object_edge")
