import uuid
import networkx as nx
import matplotlib.pyplot as plt


class GraphManager():
    def __init__(self, start_pos):
        self.test = None
        self.KRM = nx.Graph() # Knowledge Road Map
        self.KRM.add_node(0, pos=start_pos, type="waypoint")
        self.next_wp_idx = 1

    def add_waypoint(self, agent_pos):
        ''' adds new waypoints and increments wp the idx'''
        self.KRM.add_node(self.next_wp_idx, pos=agent_pos, type="waypoint", id=uuid.uuid4())
        self.KRM.add_edge(self.next_wp_idx, self.next_wp_idx-1, type="waypoint_edge", id=uuid.uuid4())
        self.next_wp_idx += 1

    def init_plot(self):
        ''' initializes the plot'''
        fig, self.ax = plt.subplots()
        self.draw_dynamic_graph()
        plt.ion()
        plt.show()
        plt.pause(2)


    def draw_dynamic_graph(self):

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

        limits = plt.axis('on')  # turns on axis
        self.ax.set_aspect('equal', 'box')  # set the aspect ratio of the plot
        self.ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        # plt.show()
        plt.draw()
        plt.pause(0.5)

    # def plotKRM(self):
    #     # self.init_plot()
    #     self.draw_dynamic_graph()
    #     # plt.show()
    #     plt.draw()
    #     plt.pause(0.5)
