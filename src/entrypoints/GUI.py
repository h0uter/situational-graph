import matplotlib.pyplot as plt
import networkx as nx

from src.usecases.exploration import Exploration


class GUI():
    def __init__(self):
        # self.init_plot()
        self.agent_drawing = None
        self.local_grid_drawing = None

        # pass

    def draw_world(self, world):
        ''' draws the world '''

        fig, self.ax = plt.subplots(figsize=(10, 10))

        self.img = plt.imread("resource/floor-plan-villa.png")

        self.ax.set_title('GraphWorld simplification of optimal frontiers for exploration')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)
        self.ax.imshow(self.img, extent=[-20, 20, -15, 15])

        nx.draw_networkx_nodes(
                                world, 
                                pos=nx.get_node_attributes(world, 'pos'),
                                ax=self.ax, 
                                node_color='grey')
        nx.draw_networkx_edges(
                                world, 
                                pos=nx.get_node_attributes(world, 'pos'), 
                                ax=self.ax, 
                                edge_color='grey')

        nx.draw_networkx_labels(
                                world, 
                                pos=nx.get_node_attributes(world, 'pos'), 
                                ax=self.ax, 
                                font_size=10)

        plt.axis('on')
        self.ax.tick_params(left=True, 
                            bottom=True,
                            labelleft=True, 
                            labelbottom=True)
        plt.show()

    def init_plot(self, agent, krm):
        ''' initializes the plot'''
        # self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig, self.ax = plt.subplots()
        self.img = plt.imread("resource/floor-plan-villa.png")

        plt.ion()
        self.viz_krm(agent, krm)
        plt.pause(0.1)

    def viz_krm(self, agent, krm):

        ''' draws the current Knowledge Roadmap Graph'''
        plt.cla()
        self.ax.set_title('Online Construction of Knowledge Roadmap')
        self.ax.set_xlim([-20, 20])
        self.ax.set_xlabel('x', size=10)
        self.ax.set_ylim([-15, 15])
        self.ax.set_ylabel('y', size=10)

        # HACK: floorplan should be dependent on the specified priors and not be included in KRM
        self.ax.imshow(self.img, extent=[-20, 20, -15, 15])

        pos = nx.get_node_attributes(krm.KRM, 'pos') # TODO: unclear variable name
        # filter the nodes and edges based on their type
        waypoint_nodes = dict((n, d['type'])
                                for n, d in krm.KRM.nodes().items() if d['type'] == 'waypoint')
        frontier_nodes = dict((n, d['type'])
                                for n, d in krm.KRM.nodes().items() if d['type'] == 'frontier')
        world_object_nodes = dict((n, d['type'])
                                for n, d in krm.KRM.nodes().items() if d['type'] == 'world_object')

        world_object_edges = dict((e, d['type'])
                                for e, d in krm.KRM.edges().items() if d['type'] == 'world_object_edge')
        waypoint_edges = dict((e, d['type'])
                                for e, d in krm.KRM.edges().items() if d['type'] == 'waypoint_edge')
        frontier_edges = dict((e, d['type'])
                                for e, d in krm.KRM.edges().items() if d['type'] == 'frontier_edge')

        '''draw the nodes, edges and labels separately'''
        nx.draw_networkx_nodes(
                                krm.KRM, 
                                pos, 
                                nodelist=world_object_nodes.keys(),
                                ax=self.ax, 
                                node_color='violet',
                                node_size=575
        )
        nx.draw_networkx_nodes(
                                krm.KRM, 
                                pos, 
                                nodelist=frontier_nodes.keys(),
                                ax=self.ax, 
                                node_color='green',
                                node_size=350
                                
        )
        nx.draw_networkx_nodes(
                                krm.KRM, 
                                pos, 
                                nodelist=waypoint_nodes.keys(), 
                                ax=self.ax, 
                                node_color='red', 
                                node_size=140
        )
        nx.draw_networkx_edges(
                                krm.KRM, 
                                pos, 
                                ax=self.ax, 
                                edgelist=waypoint_edges.keys(), 
                                edge_color='red'
        )
        nx.draw_networkx_edges(
                                krm.KRM, 
                                pos, 
                                ax=self.ax, 
                                edgelist=world_object_edges.keys(), 
                                edge_color='purple'
        )
        nx.draw_networkx_edges(
                                krm.KRM, 
                                pos, 
                                ax=self.ax, 
                                edgelist=frontier_edges.keys(), 
                                edge_color='green', 
                                width=4
        )

        nx.draw_networkx_labels(krm.KRM, pos, ax=self.ax, font_size=6)
        plt.axis('on')  # turns on axis
        self.ax.set_aspect('equal', 'box')  # set the aspect ratio of the plot
        self.ax.tick_params(left=True, bottom=True,
                            labelleft=True, labelbottom=True)

    def draw_agent(self, pos):
        ''' draw the agent on the world '''
        if self.agent_drawing != None:
            self.agent_drawing.remove()
        if self.local_grid_drawing != None:
            self.local_grid_drawing.remove()
        # self.agent_drawing = plt.arrow(
        #     pos[0], pos[1], 0.3, 0.3, width=0.4, color='blue') # One day the agent will have direction
        self.agent_drawing = plt.gca().add_patch(plt.Circle(
            (pos[0], pos[1]), 1.2, fc='blue'))
        
        rec_len = 10
        self.local_grid_drawing = plt.gca().add_patch(plt.Rectangle(
            (pos[0]-0.5*rec_len, pos[1]-0.5*rec_len), rec_len, rec_len, alpha=0.2, fc='blue'))
